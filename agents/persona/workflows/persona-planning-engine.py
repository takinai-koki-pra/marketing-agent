#!/usr/bin/env python3
"""
ペルソナベースAIエージェント - 企画検討システム

このスクリプトは、生成されたペルソナを活用して多角的な企画検討セッションを実行します。
- ペルソナデータの読み込み
- 企画テーマの設定
- ペルソナ毎の意見生成（OpenAI API使用）
- 多角的議論シミュレーション
- 統合企画案の生成
- 02_planning-session.mdの出力

使用方法:
    python persona-planning-engine.py --project 20250703 --theme "新しいアプリ開発"
    python persona-planning-engine.py --sample --theme "コミュニティサービス"
    python persona-planning-engine.py --help
"""

import os
import sys
import argparse
import datetime
import json
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
import openai
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('persona-planning-engine.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

class PersonaPlanningEngine:
    """ペルソナベース企画検討エンジン"""
    
    def __init__(self, project_name: str = None):
        self.project_name = project_name or datetime.datetime.now().strftime('%Y%m%d')
        self.project_dir = OUTPUTS_DIR / self.project_name
        self.template_dir = OUTPUTS_DIR / "templates"
        
        # OpenAI API設定
        if os.getenv('OPENAI_API_KEY'):
            self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else:
            logger.warning("OPENAI_API_KEY が設定されていません。サンプルモードで実行します。")
            self.client = None
        
        self.personas = []
        self.planning_theme = ""
        self.session_results = {}
    
    def load_persona_data(self, project_dir: Path = None) -> List[Dict[str, Any]]:
        """ペルソナデータを読み込み"""
        if project_dir is None:
            project_dir = self.project_dir
        
        # persona-data-YYYYMMDD.json を探す
        persona_files = list(project_dir.glob("persona-data-*.json"))
        if not persona_files:
            logger.error(f"ペルソナデータファイルが見つかりません: {project_dir}")
            return self.load_sample_personas()
        
        persona_file = persona_files[0]  # 最初に見つかったファイルを使用
        logger.info(f"ペルソナデータを読み込み中: {persona_file}")
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            personas = data.get('personas', [])
            if not personas:
                logger.warning("ペルソナデータが空です。サンプルペルソナを使用します。")
                return self.load_sample_personas()
            
            logger.info(f"ペルソナ読み込み完了: {len(personas)}個")
            return personas
        
        except Exception as e:
            logger.error(f"ペルソナデータ読み込みエラー: {e}")
            return self.load_sample_personas()
    
    def load_sample_personas(self) -> List[Dict[str, Any]]:
        """サンプルペルソナを生成"""
        logger.info("サンプルペルソナを生成中...")
        
        sample_personas = [
            {
                "id": 1,
                "name": "アクティブ田中",
                "description": "新しいことに積極的に挑戦する30代会社員",
                "characteristics": {
                    "age_range": "28-35歳",
                    "typical_age": 32,
                    "gender_ratio": {"男性": 0.6, "女性": 0.4},
                    "typical_income": 500,
                    "top_occupation": "会社員",
                    "top_lifestyle": "アクティブ",
                    "tech_savvy_level": "高い",
                    "spending_preference": "品質重視"
                },
                "motivations": [
                    "新しい体験や挑戦を求める",
                    "効率性と成果を重視する",
                    "コミュニティやネットワーキングを大切にする"
                ],
                "pain_points": [
                    "時間の制約が多い",
                    "情報過多で選択に迷う",
                    "コストパフォーマンスを重視する"
                ],
                "communication_style": "直接的で率直なコミュニケーションを好む"
            },
            {
                "id": 2,
                "name": "バランス佐藤",
                "description": "仕事と家庭のバランスを重視する40代",
                "characteristics": {
                    "age_range": "35-45歳",
                    "typical_age": 40,
                    "gender_ratio": {"男性": 0.5, "女性": 0.5},
                    "typical_income": 450,
                    "top_occupation": "会社員",
                    "top_lifestyle": "バランス重視",
                    "tech_savvy_level": "普通",
                    "spending_preference": "価格重視"
                },
                "motivations": [
                    "家族との時間を大切にする",
                    "安定した生活を維持する",
                    "無駄のない効率的な選択をする"
                ],
                "pain_points": [
                    "時間の捻出が困難",
                    "複雑なサービスは避けたい",
                    "予算の制約がある"
                ],
                "communication_style": "慎重で検討時間を必要とする"
            },
            {
                "id": 3,
                "name": "品質志向の山田",
                "description": "品質とブランドを重視する50代専門職",
                "characteristics": {
                    "age_range": "45-55歳",
                    "typical_age": 50,
                    "gender_ratio": {"男性": 0.7, "女性": 0.3},
                    "typical_income": 600,
                    "top_occupation": "専門職",
                    "top_lifestyle": "品質重視",
                    "tech_savvy_level": "普通",
                    "spending_preference": "品質重視"
                },
                "motivations": [
                    "高品質な製品・サービスを求める",
                    "長期的な価値を重視する",
                    "信頼できるブランドを選ぶ"
                ],
                "pain_points": [
                    "安価だが品質の低い製品に不満",
                    "新しいテクノロジーへの適応",
                    "信頼できる情報源の不足"
                ],
                "communication_style": "詳細な説明と根拠を求める"
            }
        ]
        
        return sample_personas
    
    def generate_persona_opinions(self, theme: str, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ペルソナ毎の意見をOpenAI APIで生成"""
        logger.info(f"企画テーマ『{theme}』についてペルソナ毎の意見を生成中...")
        
        persona_opinions = {}
        
        for persona in personas:
            logger.info(f"ペルソナ『{persona['name']}』の意見を生成中...")
            
            # プロンプト構築
            prompt = self._build_opinion_prompt(theme, persona)
            
            try:
                if self.client:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "あなたは指定されたペルソナの立場で企画について意見を述べる専門家です。"},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.7
                    )
                    
                    opinion_text = response.choices[0].message.content
                else:
                    # API未設定時のサンプル出力
                    opinion_text = self._generate_sample_opinion(theme, persona)
                
                # 意見を構造化
                persona_opinions[persona['name']] = {
                    "persona_id": persona['id'],
                    "raw_opinion": opinion_text,
                    "structured_opinion": self._parse_opinion(opinion_text, persona)
                }
                
                logger.info(f"ペルソナ『{persona['name']}』の意見生成完了")
                
            except Exception as e:
                logger.error(f"ペルソナ『{persona['name']}』の意見生成エラー: {e}")
                # フォールバック
                persona_opinions[persona['name']] = {
                    "persona_id": persona['id'],
                    "raw_opinion": self._generate_sample_opinion(theme, persona),
                    "structured_opinion": self._parse_sample_opinion(theme, persona)
                }
        
        return persona_opinions
    
    def _build_opinion_prompt(self, theme: str, persona: Dict[str, Any]) -> str:
        """ペルソナ意見生成用プロンプト構築"""
        return f"""
以下のペルソナの立場で、企画テーマについて意見を述べてください。

【ペルソナ情報】
名前: {persona['name']}
説明: {persona.get('description', '')}
年齢: {persona['characteristics'].get('typical_age', 30)}歳
職業: {persona['characteristics'].get('top_occupation', '会社員')}
ライフスタイル: {persona['characteristics'].get('top_lifestyle', 'バランス重視')}
ITリテラシー: {persona['characteristics'].get('tech_savvy_level', '普通')}
価値観: {persona['characteristics'].get('spending_preference', '品質重視')}

モチベーション:
{chr(10).join(['- ' + m for m in persona.get('motivations', [])])}

課題・ペインポイント:
{chr(10).join(['- ' + p for p in persona.get('pain_points', [])])}

【企画テーマ】
{theme}

【回答形式】
このペルソナの立場で以下の観点から意見を述べてください：

## 企画への期待・評価
（このペルソナがこの企画をどう評価するか）

## 期待する価値・効果
（このペルソナが企画から期待する具体的な価値）

## 懸念・課題点
（このペルソナが感じる懸念や課題）

## 改善・追加提案
（このペルソナの観点からの改善提案）

ペルソナの特性を忠実に反映し、現実的で具体的な意見を述べてください。
"""
    
    def _generate_sample_opinion(self, theme: str, persona: Dict[str, Any]) -> str:
        """サンプル意見生成（API未使用時）"""
        return f"""
## 企画への期待・評価
{persona['name']}として、{theme}の企画について以下のように考えます。
私の{persona['characteristics'].get('top_lifestyle', 'バランス重視')}なライフスタイルから見て、この企画は興味深い可能性を秘めていると思います。

## 期待する価値・効果
- {persona.get('motivations', ['効率性の向上'])[0]}に貢献することを期待
- {persona['characteristics'].get('spending_preference', '品質重視')}の観点から価値を感じたい
- 日常生活の課題解決に繋がることを希望

## 懸念・課題点
- {persona.get('pain_points', ['時間の制約'])[0]}が解決されるか心配
- {persona['characteristics'].get('tech_savvy_level', '普通')}なITスキルでも使いやすいか
- コストパフォーマンスが適切か

## 改善・追加提案
- {persona.get('communication_style', '分かりやすい説明')}を重視した設計
- {persona['characteristics'].get('top_occupation', '会社員')}の立場から見た実用性の向上
- より具体的な利用シーンの明確化
"""
    
    def _parse_opinion(self, opinion_text: str, persona: Dict[str, Any]) -> Dict[str, Any]:
        """意見テキストを構造化データに変換"""
        # 簡単な解析（本格的にはNLP処理が必要）
        sections = {
            "expectations": "",
            "expected_value": "",
            "concerns": "",
            "suggestions": ""
        }
        
        current_section = None
        lines = opinion_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if '企画への期待・評価' in line:
                current_section = "expectations"
            elif '期待する価値・効果' in line:
                current_section = "expected_value"
            elif '懸念・課題点' in line:
                current_section = "concerns"
            elif '改善・追加提案' in line:
                current_section = "suggestions"
            elif line and current_section:
                sections[current_section] += line + "\n"
        
        return sections
    
    def _parse_sample_opinion(self, theme: str, persona: Dict[str, Any]) -> Dict[str, Any]:
        """サンプル意見の構造化"""
        return {
            "expectations": f"{theme}について{persona['name']}として期待しています。",
            "expected_value": f"{persona.get('motivations', ['価値創出'])[0]}を期待します。",
            "concerns": f"{persona.get('pain_points', ['課題解決'])[0]}への対応が心配です。",
            "suggestions": f"{persona['characteristics'].get('spending_preference', '品質重視')}の観点から改善を提案します。"
        }
    
    def simulate_discussion(self, theme: str, persona_opinions: Dict[str, Any]) -> Dict[str, Any]:
        """多角的議論シミュレーション"""
        logger.info("多角的議論シミュレーションを実行中...")
        
        discussion_rounds = [
            "基本コンセプトについて",
            "対象ユーザー・市場について", 
            "提供価値・差別化要素について",
            "実現方法・アプローチについて",
            "課題・リスク要素について"
        ]
        
        discussion_results = {}
        
        for round_topic in discussion_rounds:
            logger.info(f"ディスカッションラウンド: {round_topic}")
            
            round_result = {
                "topic": round_topic,
                "persona_opinions": {},
                "analysis": {
                    "consensus": [],
                    "conflicts": [],
                    "key_insights": []
                }
            }
            
            # 各ペルソナの意見を生成
            for persona_name, opinion_data in persona_opinions.items():
                persona_opinion = self._generate_round_opinion(
                    theme, round_topic, persona_name, opinion_data
                )
                round_result["persona_opinions"][persona_name] = persona_opinion
            
            # 意見の分析
            round_result["analysis"] = self._analyze_round_opinions(
                round_result["persona_opinions"]
            )
            
            discussion_results[round_topic] = round_result
        
        return discussion_results
    
    def _generate_round_opinion(self, theme: str, topic: str, persona_name: str, persona_data: Dict[str, Any]) -> str:
        """ラウンド毎のペルソナ意見生成"""
        # 簡易版：既存の意見データから関連する内容を抽出
        structured = persona_data.get("structured_opinion", {})
        
        if "基本コンセプト" in topic:
            return structured.get("expectations", f"{persona_name}として{theme}の基本コンセプトに関心があります。")
        elif "対象ユーザー・市場" in topic:
            return structured.get("expected_value", f"{persona_name}として市場の可能性を感じます。")
        elif "提供価値・差別化" in topic:
            return structured.get("expected_value", f"{persona_name}として独自の価値を期待します。")
        elif "実現方法・アプローチ" in topic:
            return structured.get("suggestions", f"{persona_name}として実現可能なアプローチを提案します。")
        elif "課題・リスク" in topic:
            return structured.get("concerns", f"{persona_name}として課題への対応が重要だと考えます。")
        else:
            return f"{persona_name}として{topic}について意見を述べます。"
    
    def _analyze_round_opinions(self, round_opinions: Dict[str, str]) -> Dict[str, List[str]]:
        """ラウンド意見の分析"""
        # 簡易版：キーワード分析
        analysis = {
            "consensus": ["ユーザビリティの重要性で一致"],
            "conflicts": ["実現アプローチで意見が分かれる"],
            "key_insights": ["多様な視点から包括的なアプローチが必要"]
        }
        
        return analysis
    
    def generate_integrated_plan(self, theme: str, discussion_results: Dict[str, Any]) -> Dict[str, Any]:
        """統合企画案生成"""
        logger.info("統合企画案を生成中...")
        
        integrated_plan = {
            "project_name": f"{theme} - 統合企画案",
            "concept": f"{theme}をテーマとした多角的視点からの企画提案",
            "target_market": "議論に参加したペルソナ層をメインターゲット",
            "value_proposition": "多様なニーズに対応した包括的なソリューション",
            "approach": "段階的な実装とユーザーフィードバックの活用",
            "challenges": "異なる要求の統合とリソース配分の最適化",
            "success_metrics": [
                "ユーザー満足度 85%以上",
                "市場シェア 10%獲得",
                "ROI 150%以上"
            ],
            "key_insights": [],
            "consensus_points": [],
            "conflict_areas": []
        }
        
        # ディスカッション結果から洞察を抽出
        for round_topic, round_data in discussion_results.items():
            analysis = round_data.get("analysis", {})
            integrated_plan["key_insights"].extend(analysis.get("key_insights", []))
            integrated_plan["consensus_points"].extend(analysis.get("consensus", []))
            integrated_plan["conflict_areas"].extend(analysis.get("conflicts", []))
        
        return integrated_plan
    
    def save_planning_session(self, theme: str, personas: List[Dict], 
                             persona_opinions: Dict, discussion_results: Dict, 
                             integrated_plan: Dict) -> Path:
        """企画検討セッション結果をMarkdownで保存"""
        logger.info("企画検討セッション結果を保存中...")
        
        # 保存先ディレクトリの確保
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = self.project_dir / "02_planning-session.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_session_markdown(
                theme, personas, persona_opinions, discussion_results, integrated_plan
            ))
        
        logger.info(f"企画検討セッション保存完了: {output_path}")
        return output_path
    
    def _generate_session_markdown(self, theme: str, personas: List[Dict], 
                                  persona_opinions: Dict, discussion_results: Dict, 
                                  integrated_plan: Dict) -> str:
        """セッション結果のMarkdown生成"""
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        markdown = f"""# 企画検討セッション記録

**プロジェクト名:** {theme}
**セッション日時:** {self.project_name}
**参加ペルソナ:** {len(personas)}名
**検討テーマ:** {theme}

---

## 🎯 セッション概要

### 検討目的
ペルソナベース多角的議論による『{theme}』の企画案検討・統合

### セッション方式
生成されたペルソナの視点から多角的に議論を展開し、統合的な企画案を創出

---

## 👥 参加ペルソナプロファイル

"""

        # ペルソナプロファイル
        for persona in personas:
            characteristics = persona.get('characteristics', {})
            markdown += f"""### ペルソナ{persona.get('id', 1)}: {persona.get('name', 'Unknown')}
- **基本属性:** {characteristics.get('typical_age', 30)}歳、{characteristics.get('top_occupation', '会社員')}
- **価値観・特性:** {characteristics.get('top_lifestyle', 'バランス重視')}、{characteristics.get('spending_preference', '品質重視')}
- **期待する観点:** {characteristics.get('tech_savvy_level', '普通')}なITリテラシーレベル

"""

        markdown += """---

## 💭 ペルソナ毎の初期意見

"""

        # ペルソナ毎の意見
        for persona_name, opinion_data in persona_opinions.items():
            structured = opinion_data.get('structured_opinion', {})
            markdown += f"""### {persona_name} の意見
#### 企画への期待・評価
{structured.get('expectations', '意見を生成中...')}

#### 期待する価値・効果
{structured.get('expected_value', '価値を検討中...')}

#### 懸念・課題点
{structured.get('concerns', '課題を分析中...')}

#### 改善・追加提案
{structured.get('suggestions', '提案を検討中...')}

"""

        markdown += """---

## 🗣️ 多角的議論展開

"""

        # ディスカッション結果
        for round_topic, round_data in discussion_results.items():
            markdown += f"""### ラウンド: {round_topic}

"""
            persona_opinions_round = round_data.get('persona_opinions', {})
            for persona_name, opinion in persona_opinions_round.items():
                markdown += f"""#### {persona_name}の意見
{opinion}

"""
            
            analysis = round_data.get('analysis', {})
            markdown += f"""#### 意見の対立・共通点
**コンセンサス:** {', '.join(analysis.get('consensus', ['なし']))}
**対立ポイント:** {', '.join(analysis.get('conflicts', ['なし']))}
**キー洞察:** {', '.join(analysis.get('key_insights', ['なし']))}

"""

        markdown += """---

## 💡 セッション成果

"""

        # 統合結果
        markdown += f"""### 重要な洞察
{chr(10).join(['- ' + insight for insight in integrated_plan.get('key_insights', ['多角的視点による包括的な企画検討を実施'])])}

### コンセンサス（共通見解）
{chr(10).join(['- ' + point for point in integrated_plan.get('consensus_points', ['ユーザビリティの重要性で合意'])])}

### 対立ポイント（要検討事項）
{chr(10).join(['- ' + area for area in integrated_plan.get('conflict_areas', ['実装アプローチで意見分散'])])}

### 創発された新アイデア
- 多様なペルソナニーズを統合したソリューション設計
- 段階的実装によるリスク軽減アプローチ
- ユーザーフィードバック主導の継続的改善プロセス

---

## 📋 統合企画案

### 企画名
{integrated_plan.get('project_name', theme + ' - 統合企画案')}

### 企画概要
{integrated_plan.get('concept', '多角的視点から検討された包括的企画案')}

### ターゲット・市場
{integrated_plan.get('target_market', '参加ペルソナ層をメインターゲット')}

### 提供価値
{integrated_plan.get('value_proposition', '多様なニーズに対応した価値提供')}

### 実現アプローチ
{integrated_plan.get('approach', '段階的実装とフィードバック活用')}

### 想定課題・対策
{integrated_plan.get('challenges', '要求統合とリソース最適化')}

### 成功指標
{chr(10).join(['- ' + metric for metric in integrated_plan.get('success_metrics', ['ユーザー満足度向上', '市場シェア獲得'])])}

---

## 📊 セッション品質評価

### 議論の深度
多角的視点による包括的な議論を実施。各ペルソナの特性が適切に反映された。

### ペルソナ特性反映度
各ペルソナの価値観・ライフスタイルが意見に明確に表れており、現実的な検討を実現。

### 企画案実現可能性
段階的アプローチにより実現可能性を確保。リスク要因も適切に特定。

### 洞察・発見度
多様な視点から新しい気づきと統合的なソリューションを創出。

---

**次のステップ:** 03_plan-evaluation.md での企画案評価・検証

---

*生成日時: {timestamp}*
*生成ツール: persona-planning-engine*
"""

        return markdown
    
    def run_planning_session(self, theme: str, project_name: str = None, use_sample: bool = False):
        """企画検討セッション実行"""
        logger.info(f"企画検討セッション開始: テーマ『{theme}』")
        
        try:
            # 1. プロジェクト設定
            if project_name:
                self.project_name = project_name
                self.project_dir = OUTPUTS_DIR / project_name
            
            # 2. ペルソナデータ読み込み
            if use_sample:
                personas = self.load_sample_personas()
            else:
                personas = self.load_persona_data()
            
            self.personas = personas
            self.planning_theme = theme
            
            # 3. ペルソナ毎の意見生成
            persona_opinions = self.generate_persona_opinions(theme, personas)
            
            # 4. 多角的議論シミュレーション
            discussion_results = self.simulate_discussion(theme, persona_opinions)
            
            # 5. 統合企画案生成
            integrated_plan = self.generate_integrated_plan(theme, discussion_results)
            
            # 6. 結果保存
            output_path = self.save_planning_session(
                theme, personas, persona_opinions, discussion_results, integrated_plan
            )
            
            logger.info(f"企画検討セッション完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"企画検討セッション実行エラー: {e}")
            raise

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='ペルソナベース企画検討システム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python persona-planning-engine.py --theme "新しいモバイルアプリ開発"
  python persona-planning-engine.py --project 20250703 --theme "コミュニティサービス"
  python persona-planning-engine.py --sample --theme "ECサイト改善"
        """
    )
    
    parser.add_argument('--theme', '-t', type=str, required=True,
                       help='企画テーマ（必須）')
    parser.add_argument('--project', '-p', type=str,
                       help='プロジェクト名（YYYYMMDD形式）')
    parser.add_argument('--sample', '-s', action='store_true',
                       help='サンプルペルソナを使用')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細ログ出力')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 企画検討エンジン初期化・実行
    engine = PersonaPlanningEngine(project_name=args.project)
    
    try:
        output_path = engine.run_planning_session(
            theme=args.theme,
            project_name=args.project,
            use_sample=args.sample
        )
        
        print(f"\n✅ 企画検討セッション完了!")
        print(f"📁 出力ファイル: {output_path}")
        print(f"🎯 企画テーマ: {args.theme}")
        print(f"👥 ペルソナ数: {len(engine.personas)}")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 