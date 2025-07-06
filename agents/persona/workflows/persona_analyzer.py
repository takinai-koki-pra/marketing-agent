#!/usr/bin/env python3
"""
ペルソナベースAIエージェント - ペルソナ分析ツール

このスクリプトは、リサーチデータからペルソナを分析・生成します。
- リサーチデータの読み込み・解析
- ペルソナセグメント分析
- 統計処理・データ可視化
- JSON形式での結果出力

使用方法:
    python persona-analyzer.py --input research-data.csv       # CSVデータから分析
    python persona-analyzer.py --project 20250703             # プロジェクト用分析
    python persona-analyzer.py --sample                       # サンプルデータで分析
"""

import os
import sys
import argparse
import datetime
import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('persona-analyzer.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

class PersonaAnalyzer:
    """ペルソナ分析クラス"""
    
    def __init__(self, project_name: str = None):
        self.project_name = project_name or datetime.datetime.now().strftime('%Y%m%d')
        self.project_dir = OUTPUTS_DIR / self.project_name
        self.data = None
        self.personas = []
        self.analysis_results = {}
    
    def load_sample_data(self) -> pd.DataFrame:
        """サンプルデータを生成"""
        logger.info("サンプルデータを生成中...")
        
        np.random.seed(42)  # 再現性のため
        
        # サンプルデータ生成
        n_samples = 1000
        data = {
            'age': np.random.normal(35, 12, n_samples).astype(int),
            'gender': np.random.choice(['男性', '女性'], n_samples, p=[0.48, 0.52]),
            'income': np.random.normal(450, 150, n_samples).astype(int),  # 万円
            'occupation': np.random.choice([
                '会社員', '公務員', '自営業', '専業主婦・主夫', 
                '学生', 'パート・アルバイト', '退職者'
            ], n_samples, p=[0.4, 0.1, 0.15, 0.1, 0.05, 0.15, 0.05]),
            'region': np.random.choice([
                '関東', '関西', '中部', '九州', '東北', '中国・四国', '北海道・沖縄'
            ], n_samples, p=[0.35, 0.2, 0.15, 0.1, 0.08, 0.07, 0.05]),
            'lifestyle': np.random.choice([
                'アクティブ', '家庭重視', 'キャリア重視', '趣味重視', 'バランス重視'
            ], n_samples, p=[0.2, 0.25, 0.2, 0.15, 0.2]),
            'tech_savvy': np.random.choice([
                '高い', '普通', '低い'
            ], n_samples, p=[0.3, 0.5, 0.2]),
            'spending_pattern': np.random.choice([
                '価格重視', '品質重視', 'ブランド重視', '利便性重視'
            ], n_samples, p=[0.3, 0.35, 0.15, 0.2])
        }
        
        # 年齢による調整
        df = pd.DataFrame(data)
        df.loc[df['age'] < 25, 'income'] = df.loc[df['age'] < 25, 'income'] * 0.6
        df.loc[df['age'] > 60, 'income'] = df.loc[df['age'] > 60, 'income'] * 0.8
        df['income'] = df['income'].clip(lower=150, upper=1000)  # 150-1000万円の範囲
        
        return df
    
    def load_csv_data(self, file_path: Path) -> pd.DataFrame:
        """CSVファイルからデータを読み込み"""
        logger.info(f"CSVデータを読み込み中: {file_path}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"データ読み込み完了: {len(df)}行")
            return df
        except Exception as e:
            logger.error(f"CSV読み込みエラー: {e}")
            raise
    
    def analyze_demographics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """人口統計学的分析"""
        logger.info("人口統計学的分析を実行中...")
        
        demographics = {
            'age_stats': {
                'mean': float(df['age'].mean()),
                'median': float(df['age'].median()),
                'std': float(df['age'].std()),
                'min': int(df['age'].min()),
                'max': int(df['age'].max())
            },
            'gender_distribution': df['gender'].value_counts().to_dict(),
            'income_stats': {
                'mean': float(df['income'].mean()),
                'median': float(df['income'].median()),
                'std': float(df['income'].std())
            },
            'occupation_distribution': df['occupation'].value_counts().to_dict(),
            'region_distribution': df['region'].value_counts().to_dict(),
            'lifestyle_distribution': df['lifestyle'].value_counts().to_dict()
        }
        
        return demographics
    
    def segment_personas(self, df: pd.DataFrame, n_personas: int = 3) -> List[Dict[str, Any]]:
        """ペルソナセグメンテーション"""
        logger.info(f"{n_personas}個のペルソナセグメントを生成中...")
        
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import LabelEncoder
        
        # カテゴリカル変数のエンコーディング
        df_encoded = df.copy()
        encoders = {}
        
        categorical_columns = ['gender', 'occupation', 'region', 'lifestyle', 'tech_savvy', 'spending_pattern']
        for col in categorical_columns:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col + '_encoded'] = le.fit_transform(df_encoded[col])
                encoders[col] = le
        
        # クラスタリング用の特徴量選択
        feature_columns = ['age', 'income'] + [col + '_encoded' for col in categorical_columns if col in df.columns]
        X = df_encoded[feature_columns]
        
        # K-meansクラスタリング
        kmeans = KMeans(n_clusters=n_personas, random_state=42, n_init=10)
        df_encoded['cluster'] = kmeans.fit_predict(X)
        
        # 各クラスターの代表的なペルソナ生成
        personas = []
        for i in range(n_personas):
            cluster_data = df[df_encoded['cluster'] == i]
            
            persona = {
                'id': i + 1,
                'name': f'ペルソナ{i + 1}',
                'size': len(cluster_data),
                'percentage': round(len(cluster_data) / len(df) * 100, 1),
                'characteristics': {
                    'age_range': f"{int(cluster_data['age'].quantile(0.25))}-{int(cluster_data['age'].quantile(0.75))}歳",
                    'typical_age': int(cluster_data['age'].median()),
                    'gender_ratio': cluster_data['gender'].value_counts(normalize=True).to_dict(),
                    'income_range': f"{int(cluster_data['income'].quantile(0.25))}-{int(cluster_data['income'].quantile(0.75))}万円",
                    'typical_income': int(cluster_data['income'].median()),
                    'top_occupation': cluster_data['occupation'].mode().iloc[0],
                    'top_region': cluster_data['region'].mode().iloc[0],
                    'top_lifestyle': cluster_data['lifestyle'].mode().iloc[0],
                    'tech_savvy_level': cluster_data['tech_savvy'].mode().iloc[0],
                    'spending_preference': cluster_data['spending_pattern'].mode().iloc[0]
                }
            }
            
            personas.append(persona)
        
        return personas
    
    def generate_persona_descriptions(self, personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ペルソナの詳細説明を生成"""
        logger.info("ペルソナの詳細説明を生成中...")
        
        # ペルソナ名のマッピング
        persona_names = [
            "アクティブ田中", "バランス佐藤", "品質志向の山田",
            "コスト重視の鈴木", "トレンド敏感な高橋"
        ]
        
        # ライフスタイル説明のマッピング
        lifestyle_descriptions = {
            'アクティブ': '積極的に新しいことに挑戦し、外出やイベント参加を好む',
            '家庭重視': '家族との時間を大切にし、安定した日常を求める',
            'キャリア重視': '仕事での成功を重視し、自己投資に積極的',
            '趣味重視': '個人の趣味や興味を優先し、自分の時間を大切にする',
            'バランス重視': '仕事とプライベートのバランスを重視する'
        }
        
        for i, persona in enumerate(personas):
            characteristics = persona['characteristics']
            
            # より詳細な説明を追加
            persona['detailed_profile'] = {
                'name': persona_names[i] if i < len(persona_names) else f"ペルソナ{persona['id']}",
                'summary': f"{characteristics['typical_age']}歳の{characteristics['top_occupation']}。{characteristics['top_region']}在住。",
                'lifestyle_description': lifestyle_descriptions.get(
                    characteristics['top_lifestyle'], 
                    f"{characteristics['top_lifestyle']}な生活スタイル"
                ),
                'purchase_behavior': f"{characteristics['spending_preference']}で商品を選択。ITリテラシーは{characteristics['tech_savvy_level']}。",
                'communication_preference': self._get_communication_preference(characteristics),
                'pain_points': self._generate_pain_points(characteristics),
                'motivations': self._generate_motivations(characteristics)
            }
        
        return personas
    
    def _get_communication_preference(self, characteristics: Dict) -> str:
        """コミュニケーション嗜好を生成"""
        tech_level = characteristics['tech_savvy_level']
        age = characteristics['typical_age']
        
        if tech_level == '高い':
            return "SNS、アプリ、Webサイトでの情報収集を好む"
        elif age < 30:
            return "SNSやオンラインコミュニティを活用"
        elif age > 50:
            return "テレビ、新聞、口コミを重視"
        else:
            return "オンラインとオフラインの情報をバランス良く活用"
    
    def _generate_pain_points(self, characteristics: Dict) -> List[str]:
        """ペインポイントを生成"""
        pain_points = []
        
        if characteristics['spending_preference'] == '価格重視':
            pain_points.append("コストパフォーマンスの低い商品・サービス")
        elif characteristics['spending_preference'] == '品質重視':
            pain_points.append("品質の不安定さや信頼性の欠如")
        
        if characteristics['tech_savvy_level'] == '低い':
            pain_points.append("複雑な操作や設定が必要なサービス")
        
        if characteristics['top_lifestyle'] == '家庭重視':
            pain_points.append("家族との時間を奪われること")
        
        return pain_points or ["時間の無駄", "期待値とのギャップ"]
    
    def _generate_motivations(self, characteristics: Dict) -> List[str]:
        """モチベーションを生成"""
        motivations = []
        
        if characteristics['top_lifestyle'] == 'キャリア重視':
            motivations.append("スキルアップ・キャリア向上")
        elif characteristics['top_lifestyle'] == '家庭重視':
            motivations.append("家族の幸せ・安心")
        elif characteristics['top_lifestyle'] == 'アクティブ':
            motivations.append("新しい体験・挑戦")
        
        if characteristics['spending_preference'] == 'ブランド重視':
            motivations.append("ステータス・自己表現")
        
        return motivations or ["生活の質向上", "時間の有効活用"]
    
    def create_visualizations(self, df: pd.DataFrame, personas: List[Dict[str, Any]]):
        """データ可視化を作成"""
        logger.info("データ可視化を作成中...")
        
        # 出力ディレクトリ作成
        vis_dir = self.project_dir / "visualizations"
        vis_dir.mkdir(exist_ok=True)
        
        # 1. 年齢分布
        plt.figure(figsize=(10, 6))
        plt.hist(df['age'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('年齢分布', fontsize=14, fontweight='bold')
        plt.xlabel('年齢')
        plt.ylabel('人数')
        plt.grid(True, alpha=0.3)
        plt.savefig(vis_dir / 'age_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 収入分布
        plt.figure(figsize=(10, 6))
        plt.hist(df['income'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.title('収入分布', fontsize=14, fontweight='bold')
        plt.xlabel('年収（万円）')
        plt.ylabel('人数')
        plt.grid(True, alpha=0.3)
        plt.savefig(vis_dir / 'income_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. ペルソナサイズ比較
        persona_names = [p['detailed_profile']['name'] for p in personas]
        persona_sizes = [p['size'] for p in personas]
        
        plt.figure(figsize=(10, 6))
        plt.pie(persona_sizes, labels=persona_names, autopct='%1.1f%%', startangle=90)
        plt.title('ペルソナ分布', fontsize=14, fontweight='bold')
        plt.savefig(vis_dir / 'persona_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"可視化ファイルを保存: {vis_dir}")
    
    def save_results(self, df: pd.DataFrame, personas: List[Dict[str, Any]], demographics: Dict[str, Any]):
        """結果を保存"""
        logger.info("分析結果を保存中...")
        
        # 結果データ作成
        results = {
            'project_info': {
                'project_name': self.project_name,
                'analysis_date': datetime.datetime.now().isoformat(),
                'data_size': len(df),
                'persona_count': len(personas)
            },
            'demographics': demographics,
            'personas': personas,
            'metadata': {
                'version': '1.0',
                'analyzer': 'persona-analyzer.py'
            }
        }
        
        # JSON保存
        output_file = self.project_dir / f"persona-analysis-{self.project_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析結果を保存: {output_file}")
        return results
    
    def run_analysis(self, data_source: str = 'sample', n_personas: int = 3):
        """分析を実行"""
        logger.info(f"ペルソナ分析開始: {self.project_name}")
        
        # データ読み込み
        if data_source == 'sample':
            df = self.load_sample_data()
        else:
            df = self.load_csv_data(Path(data_source))
        
        # 基本統計分析
        demographics = self.analyze_demographics(df)
        
        # ペルソナセグメンテーション
        personas = self.segment_personas(df, n_personas)
        
        # 詳細説明生成
        personas = self.generate_persona_descriptions(personas)
        
        # 可視化作成
        self.create_visualizations(df, personas)
        
        # 結果保存
        results = self.save_results(df, personas, demographics)
        
        logger.info(f"ペルソナ分析完了: {self.project_name}")
        return results

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='ペルソナベースAIエージェント ペルソナ分析ツール'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='入力CSVファイルパス'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='プロジェクト名 (YYYYMMDD形式)'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='サンプルデータで分析'
    )
    
    parser.add_argument(
        '--personas',
        type=int,
        default=3,
        help='生成するペルソナ数 (デフォルト: 3)'
    )
    
    args = parser.parse_args()
    
    # プロジェクト名決定
    project_name = args.project or datetime.datetime.now().strftime('%Y%m%d')
    
    # 分析器初期化
    analyzer = PersonaAnalyzer(project_name)
    
    # プロジェクトディレクトリ作成
    analyzer.project_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # データソース決定
        if args.sample or (not args.input):
            data_source = 'sample'
        else:
            data_source = args.input
        
        # 分析実行
        results = analyzer.run_analysis(data_source, args.personas)
        
        print(f"\n✅ ペルソナ分析が完了しました！")
        print(f"📁 プロジェクト: {project_name}")
        print(f"👥 生成ペルソナ数: {len(results['personas'])}")
        print(f"📊 データサイズ: {results['project_info']['data_size']}件")
        print(f"📂 結果保存先: {analyzer.project_dir}")
        
        # ペルソナ一覧表示
        print(f"\n🎯 生成されたペルソナ:")
        for persona in results['personas']:
            profile = persona['detailed_profile']
            print(f"  - {profile['name']}: {profile['summary']}")
        
    except Exception as e:
        logger.error(f"分析中にエラーが発生: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 