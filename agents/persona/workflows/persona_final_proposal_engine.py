#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ペルソナベース最終企画書生成エンジン
全工程結果を統合して最終企画書を生成する
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# OpenAI API (オプション)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class PersonaFinalProposalEngine:
    """ペルソナベース最終企画書生成エンジン"""
    
    def __init__(self, project_dir: str = None, verbose: bool = False):
        self.project_dir = Path(project_dir) if project_dir else Path(".")
        self.verbose = verbose
        self.setup_logging()
        
        # OpenAI設定
        if OPENAI_AVAILABLE:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.openai_enabled = True
            else:
                self.openai_enabled = False
                self.logger.warning("OPENAI_API_KEY が設定されていません。サンプルモードで動作します。")
        else:
            self.openai_enabled = False
            self.logger.warning("OpenAI ライブラリが見つかりません。サンプルモードで動作します。")
            
        # テンプレート読み込み
        self.templates = {}
        self.load_templates()
        
    def setup_logging(self):
        """ログ設定"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('persona-final-proposal-engine.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_templates(self):
        """テンプレート読み込み"""
        template_files = {
            'final_proposal_template': 'outputs/templates/04_final-proposal.md'
        }
        
        for key, file_path in template_files.items():
            full_path = self.project_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        self.templates[key] = f.read()
                    self.logger.debug(f"{key} テンプレート読み込み完了: {full_path}")
                except Exception as e:
                    self.logger.error(f"{key} テンプレート読み込みエラー: {e}")
            else:
                self.logger.warning(f"{key} テンプレートが見つかりません: {full_path}")
                
    def load_previous_results(self, date: str) -> Dict:
        """前工程結果の読み込み"""
        results = {}
        outputs_dir = self.project_dir / f"outputs/{date}"
        
        files_to_load = [
            ('persona_analysis', '01_persona-analysis.md'),
            ('planning_session', '02_planning-session.md'),
            ('plan_evaluation', '03_plan-evaluation.md'),
            ('persona_data', f'persona-data-{date}.json')
        ]
        
        for key, filename in files_to_load:
            file_path = outputs_dir / filename
            if file_path.exists():
                try:
                    if filename.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            results[key] = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            results[key] = f.read()
                    self.logger.info(f"{key} 読み込み完了: {filename}")
                except Exception as e:
                    self.logger.error(f"{key} 読み込みエラー: {e}")
            else:
                self.logger.warning(f"{key} が見つかりません: {filename}")
                
        return results
        
    def generate_final_proposal(self, date: str, previous_results: Dict) -> Dict:
        """最終企画書生成"""
        self.logger.info("最終企画書生成中...")
        
        # 統合分析
        integrated_analysis = self.integrate_analysis(previous_results)
        
        # エグゼクティブサマリー生成
        executive_summary = self.generate_executive_summary(integrated_analysis)
        
        # 市場・ニーズ分析
        market_analysis = self.generate_market_analysis(integrated_analysis)
        
        # 企画詳細仕様
        detailed_specs = self.generate_detailed_specs(integrated_analysis)
        
        # 実行計画・投資分析
        execution_plan = self.generate_execution_plan(integrated_analysis)
        
        # 最終推奨・次ステップ
        final_recommendation = self.generate_final_recommendation(integrated_analysis)
        
        return {
            'integrated_analysis': integrated_analysis,
            'executive_summary': executive_summary,
            'market_analysis': market_analysis,
            'detailed_specs': detailed_specs,
            'execution_plan': execution_plan,
            'final_recommendation': final_recommendation
        }
        
    def integrate_analysis(self, results: Dict) -> Dict:
        """全工程結果の統合分析"""
        # サンプル統合分析データ
        return {
            'project_theme': '地域コミュニティ向けアプリ開発',
            'target_personas': ['アクティブ田中', 'バランス佐藤', '品質志向の山田'],
            'key_insights': [
                'ユーザビリティとシンプルさのバランスが重要',
                '地域特化機能への高いニーズ',
                '段階的な機能拡張戦略が効果的'
            ],
            'feasibility_score': 14,
            'risk_level': '中',
            'recommendation_level': 'B'
        }
        
    def generate_executive_summary(self, analysis: Dict) -> Dict:
        """エグゼクティブサマリー生成"""
        return {
            'project_concept': f"{analysis['project_theme']}によるコミュニティ活性化支援",
            'value_propositions': [
                'コミュニティ参加の促進',
                '情報共有の効率化',
                '地域活動の活性化',
                '既存SNSとの差別化'
            ],
            'roi_prediction': '25%',
            'payback_period': '2.5年',
            'feasibility_summary': f"総合スコア {analysis['feasibility_score']}/20",
            'main_risks': ['市場競争激化', 'ユーザー獲得コスト', '継続利用促進'],
            'recommendation': analysis['recommendation_level']
        }
        
    def generate_market_analysis(self, analysis: Dict) -> Dict:
        """市場・ニーズ分析生成"""
        return {
            'primary_target': '地域住民・コミュニティ活動参加者',
            'market_size': '中規模（地域特化型）',
            'growth_potential': '高（デジタル化推進により）',
            'competitive_advantage': '地域特化機能・行政連携',
            'differentiation': 'コミュニティ特化・地域密着型機能'
        }
        
    def generate_detailed_specs(self, analysis: Dict) -> Dict:
        """企画詳細仕様生成"""
        return {
            'core_functions': [
                'コミュニティ情報共有機能',
                'イベント管理・参加機能',
                '地域住民間コミュニケーション機能'
            ],
            'extended_functions': [
                'プッシュ通知機能',
                'カレンダー連携機能'
            ],
            'technology_stack': 'React Native, Node.js, MongoDB',
            'security_requirements': 'SSL/TLS暗号化、ユーザー認証',
            'scalability': 'クラウドインフラによる柔軟なスケーリング'
        }
        
    def generate_execution_plan(self, analysis: Dict) -> Dict:
        """実行計画・投資分析生成"""
        return {
            'phase1_duration': '6ヶ月',
            'phase1_cost': '800万円',
            'phase2_duration': '6ヶ月',
            'phase2_cost': '600万円',
            'monthly_operating_cost': '80万円',
            'break_even': '18ヶ月目',
            'team_requirements': {
                'developers': '5名',
                'designers': '2名',
                'marketing': '2名'
            }
        }
        
    def generate_final_recommendation(self, analysis: Dict) -> Dict:
        """最終推奨・次ステップ生成"""
        return {
            'overall_score': f"{analysis['feasibility_score']}/20",
            'risk_level': analysis['risk_level'],
            'recommendation_level': analysis['recommendation_level'],
            'rationale': '総合的に実現可能性が確認され、改善提案を実装後の推進を推奨',
            'immediate_actions': [
                'UIデザイン最適化の検討',
                '技術スタック最終決定',
                '開発チーム体制構築'
            ],
            'success_metrics': [
                'ユーザー満足度8/10以上',
                '月間アクティブユーザー1000名以上',
                '18ヶ月での損益分岐点達成'
            ]
        }
        
    def generate_final_proposal_report(self, date: str, proposal_data: Dict, previous_results: Dict) -> str:
        """最終企画書レポート生成"""
        if 'final_proposal_template' not in self.templates:
            self.logger.error("最終企画書テンプレートが見つかりません")
            return None
            
        template = self.templates['final_proposal_template']
        
        # 基本情報置換
        report = template.replace('[企画名を入力]', proposal_data['integrated_analysis']['project_theme'])
        report = report.replace('[YYYYMMDD]', date)
        report = report.replace('[統合企画案名]', proposal_data['integrated_analysis']['project_theme'])
        report = report.replace('[TIMESTAMP]', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # TODOマーカー置換
        report = self.replace_final_proposal_todos(report, proposal_data)
        
        return report
        
    def replace_final_proposal_todos(self, template: str, data: Dict) -> str:
        """最終企画書TODOマーカー置換"""
        exec_summary = data['executive_summary']
        market = data['market_analysis']
        specs = data['detailed_specs']
        execution = data['execution_plan']
        recommendation = data['final_recommendation']
        
        # エグゼクティブサマリー
        template = template.replace('[ ] TODO: A/B/C/D', exec_summary['recommendation'])
        template = template.replace('[ ] TODO: 企画名・基本コンセプト・ターゲット・提供価値・実現方法の要約（200文字以内）',
            exec_summary['project_concept'])
        template = template.replace('[ ] TODO: ユーザーへの具体的価値', exec_summary['value_propositions'][0])
        template = template.replace('[ ] TODO: 事業・組織への価値', exec_summary['value_propositions'][1])
        template = template.replace('[ ] TODO: 社会・市場への価値', exec_summary['value_propositions'][2])
        template = template.replace('[ ] TODO: 差別化点・独自価値', exec_summary['value_propositions'][3])
        
        # ROI情報
        template = template.replace('[ ]年', f"{exec_summary['payback_period']}")
        template = template.replace('[ ]%', f"{exec_summary['roi_prediction']}")
        
        # 実現可能性
        template = template.replace('[ ]/20', f"{recommendation['overall_score']}")
        
        # 市場分析
        template = template.replace('[ ] TODO: メインペルソナ特性', market['primary_target'])
        template = template.replace('[ ] TODO: 市場セグメント・規模', market['market_size'])
        template = template.replace('[ ] TODO: 競合優位性', market['competitive_advantage'])
        
        # 詳細仕様
        template = template.replace('[ ] TODO: 機能名・詳細説明・ユーザー価値', specs['core_functions'][0], 1)
        template = template.replace('[ ] TODO: 機能名・詳細説明・ユーザー価値', specs['core_functions'][1], 1)
        template = template.replace('[ ] TODO: 機能名・詳細説明・ユーザー価値', specs['core_functions'][2] if len(specs['core_functions']) > 2 else 'その他の機能', 1)
        
        # 実行計画
        template = template.replace('[ ]ヶ月', f"{execution['phase1_duration']}", 1)
        template = template.replace('[ ]万円', f"{execution['phase1_cost']}", 1)
        template = template.replace('[ ]名', f"{execution['team_requirements']['developers']}", 1)
        
        # 最終推奨
        template = template.replace('[ ] TODO: 企画評価結果に基づく具体的・論理的根拠', recommendation['rationale'])
        template = template.replace('[ ] TODO: アクション1', recommendation['immediate_actions'][0], 1)
        template = template.replace('[ ] TODO: アクション2', recommendation['immediate_actions'][1] if len(recommendation['immediate_actions']) > 1 else 'チーム体制構築', 1)
        template = template.replace('[ ] TODO: アクション3', recommendation['immediate_actions'][2] if len(recommendation['immediate_actions']) > 2 else '予算確保', 1)
        
        return template
        
    def save_final_proposal_report(self, date: str, report: str) -> str:
        """最終企画書レポート保存"""
        output_dir = self.project_dir / f"outputs/{date}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "04_final-proposal.md"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"最終企画書保存完了: {output_file}")
            return str(output_file)
        except Exception as e:
            self.logger.error(f"最終企画書保存エラー: {e}")
            return None
            
    def run(self, date: str = None):
        """最終企画書生成実行"""
        if not date:
            date = datetime.now().strftime('%Y%m%d')
            
        self.logger.info(f"最終企画書生成開始: {date}")
        
        # 前工程結果読み込み
        previous_results = self.load_previous_results(date)
        
        # 最終企画書生成
        proposal_data = self.generate_final_proposal(date, previous_results)
        
        # レポート生成
        report = self.generate_final_proposal_report(date, proposal_data, previous_results)
        
        if report:
            # レポート保存
            output_file = self.save_final_proposal_report(date, report)
            if output_file:
                print("✅ 最終企画書が正常に生成されました")
                print(f"📄 ファイル: {output_file}")
            else:
                print("❌ 最終企画書の保存に失敗しました")
        else:
            print("❌ 最終企画書の生成に失敗しました")

def main():
    parser = argparse.ArgumentParser(description='ペルソナベース最終企画書生成エンジン')
    parser.add_argument('--date', help='処理対象日付 (YYYYMMDD)')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細ログ出力')
    
    args = parser.parse_args()
    
    # エンジン実行
    engine = PersonaFinalProposalEngine(verbose=args.verbose)
    engine.run(args.date)

if __name__ == "__main__":
    main() 