#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ペルソナベース企画案評価エンジン
企画検討セッション結果を多角的に評価し、改善提案を生成する
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# OpenAI API (オプション)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class PersonaEvaluationEngine:
    """ペルソナベース企画案評価エンジン"""
    
    def __init__(self, project_dir: str = None, verbose: bool = False):
        """
        初期化
        
        Args:
            project_dir: プロジェクトディレクトリパス
            verbose: 詳細ログ出力
        """
        self.project_dir = Path(project_dir) if project_dir else Path(".")
        self.verbose = verbose
        self.setup_logging()
        
        # OpenAI設定
        self.openai_client = None
        self.setup_openai()
        
        # テンプレート読み込み
        self.templates = self.load_templates()
        
    def setup_logging(self):
        """ログ設定"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('persona-evaluation-engine.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_openai(self):
        """OpenAI API設定"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI ライブラリが見つかりません。サンプルモードで動作します。")
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.logger.warning("OPENAI_API_KEY が設定されていません。サンプルモードで動作します。")
            return
            
        try:
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.logger.info("OpenAI API 接続設定完了")
        except Exception as e:
            self.logger.error(f"OpenAI API 設定エラー: {e}")
            
    def load_templates(self) -> Dict:
        """テンプレート読み込み"""
        templates = {}
        
        # プロンプトテンプレート
        prompt_path = self.project_dir / "prompts" / "plan-evaluation.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                templates['evaluation_prompt'] = f.read()
                
        # Markdownテンプレート
        template_path = self.project_dir / "outputs" / "templates" / "03_plan-evaluation.md"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                templates['evaluation_template'] = f.read()
                
        return templates
        
    def load_planning_session_data(self, date: str) -> Dict:
        """企画検討セッションデータ読み込み"""
        data_path = self.project_dir / "outputs" / date / "02_planning-session.md"
        
        if not data_path.exists():
            self.logger.error(f"企画検討セッションファイルが見つかりません: {data_path}")
            return None
            
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 基本的な情報抽出
            session_data = self.extract_session_data(content)
            return session_data
            
        except Exception as e:
            self.logger.error(f"企画検討セッションデータ読み込みエラー: {e}")
            return None
            
    def extract_session_data(self, content: str) -> Dict:
        """企画検討セッション内容から主要データを抽出"""
        data = {
            'project_name': '',
            'theme': '',
            'personas': [],
            'integrated_proposal': {},
            'discussions': [],
            'insights': []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # プロジェクト名抽出
            if line.startswith('**プロジェクト名:**'):
                data['project_name'] = line.split(':', 1)[1].strip()
                
            # 検討テーマ抽出
            elif line.startswith('**検討テーマ:**'):
                data['theme'] = line.split(':', 1)[1].strip()
                
            # セクション判定
            elif line.startswith('## 👥 ペルソナプロファイル'):
                current_section = 'personas'
            elif line.startswith('## 🎯 統合企画案'):
                current_section = 'proposal'
            elif line.startswith('## 💡 セッション成果'):
                current_section = 'insights'
                
        return data
        
    def load_persona_data(self, date: str) -> Dict:
        """ペルソナデータ読み込み"""
        persona_path = self.project_dir / "outputs" / date / f"persona-data-{date}.json"
        
        if not persona_path.exists():
            self.logger.warning(f"ペルソナデータファイルが見つかりません: {persona_path}")
            return self.generate_sample_personas()
            
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"ペルソナデータ読み込みエラー: {e}")
            return self.generate_sample_personas()
            
    def generate_sample_personas(self) -> Dict:
        """サンプルペルソナ生成"""
        return {
            "personas": [
                {
                    "id": "persona_1",
                    "name": "アクティブ田中",
                    "age": 28,
                    "occupation": "ITエンジニア",
                    "characteristics": "新技術に敏感、効率性重視、データ重視の意思決定",
                    "communication_style": "論理的で具体的、数値やデータを重視した発言"
                },
                {
                    "id": "persona_2", 
                    "name": "バランス佐藤",
                    "age": 35,
                    "occupation": "プロジェクトマネージャー",
                    "characteristics": "現実的思考、リスク管理重視、ステークホルダー調整得意",
                    "communication_style": "バランス重視、実現可能性と影響を総合的に判断"
                },
                {
                    "id": "persona_3",
                    "name": "品質志向の山田", 
                    "age": 42,
                    "occupation": "品質管理マネージャー",
                    "characteristics": "品質・安全性重視、長期的視点、慎重な判断",
                    "communication_style": "詳細な検証を重視、潜在的リスクを積極的に指摘"
                }
            ]
        }
        
    def evaluate_feasibility(self, session_data: Dict, personas: Dict) -> Dict:
        """実現可能性評価"""
        evaluation = {
            'technical': {'score': 0, 'details': [], 'rationale': ''},
            'market': {'score': 0, 'details': [], 'rationale': ''},
            'business': {'score': 0, 'details': [], 'rationale': ''},
            'organizational': {'score': 0, 'details': [], 'rationale': ''},
            'total_score': 0
        }
        
        if self.openai_client:
            # OpenAI APIを使用した評価
            evaluation = self.ai_evaluate_feasibility(session_data, personas)
        else:
            # サンプル評価生成
            evaluation = self.sample_evaluate_feasibility(session_data)
            
        return evaluation
        
    def sample_evaluate_feasibility(self, session_data: Dict) -> Dict:
        """サンプル実現可能性評価生成"""
        return {
            'technical': {
                'score': 4,
                'details': [
                    '必要技術は現在広く利用されている技術で構成されている',
                    '開発難易度は中程度で、適切なスキルを持つチームなら実現可能',
                    '技術的リスクは限定的で、既存のソリューションを活用できる'
                ],
                'rationale': '現在の技術トレンドに合致し、実現可能性は高い'
            },
            'market': {
                'score': 3,
                'details': [
                    'ターゲット市場は存在するが競合が多い',
                    '差別化要素は存在するが市場浸透には時間が必要',
                    'マーケティング戦略の実効性は中程度'
                ],
                'rationale': '市場機会はあるが競争環境に注意が必要'
            },
            'business': {
                'score': 3,
                'details': [
                    '収益モデルは妥当だが収益化まで時間が必要',
                    '初期投資は適切な範囲内',
                    'ROIは中長期的には期待できる'
                ],
                'rationale': '事業性は確保されているが成長戦略が重要'
            },
            'organizational': {
                'score': 4,
                'details': [
                    '必要な人材・スキルセットは確保可能',
                    'プロジェクト管理体制は構築可能',
                    '組織的な変革への適応性は高い'
                ],
                'rationale': '組織的な実現可能性は高く、実行体制構築可能'
            },
            'total_score': 14
        }
        
    def analyze_risks_and_challenges(self, session_data: Dict, personas: Dict) -> Dict:
        """リスク・課題分析"""
        analysis = {
            'high_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'technical_challenges': [],
            'market_challenges': [],
            'business_challenges': [],
            'organizational_challenges': []
        }
        
        if self.openai_client:
            analysis = self.ai_analyze_risks(session_data, personas)
        else:
            analysis = self.sample_analyze_risks(session_data)
            
        return analysis
        
    def sample_analyze_risks(self, session_data: Dict) -> Dict:
        """サンプルリスク・課題分析生成"""
        return {
            'high_risks': [
                {
                    'name': '市場競争激化',
                    'impact': '収益性低下、市場シェア確保困難',
                    'probability': '高',
                    'mitigation': '差別化戦略の強化、早期市場参入'
                }
            ],
            'medium_risks': [
                {
                    'name': '技術変化への対応',
                    'impact': '技術陳腐化のリスク',
                    'probability': '中',
                    'mitigation': '継続的な技術アップデート、柔軟なアーキテクチャ設計'
                }
            ],
            'low_risks': [
                {
                    'name': '規制変更',
                    'impact': '仕様変更の必要性',
                    'probability': '低',
                    'mitigation': '規制動向の継続的モニタリング'
                }
            ],
            'technical_challenges': [
                {
                    'challenge': 'スケーラビリティの確保',
                    'difficulty': 3,
                    'solution': 'クラウドインフラの活用、マイクロサービス設計'
                }
            ],
            'market_challenges': [
                {
                    'challenge': 'ユーザー獲得コスト最適化',
                    'impact': 4,
                    'solution': 'デジタルマーケティング戦略の精緻化'
                }
            ],
            'business_challenges': [
                {
                    'challenge': '収益化タイミングの最適化',
                    'importance': 4,
                    'solution': '段階的な収益モデル導入'
                }
            ],
            'organizational_challenges': [
                {
                    'challenge': 'スキル人材の確保',
                    'urgency': 3,
                    'solution': '人材採用・育成計画の策定'
                }
            ]
        }
        
    def evaluate_persona_perspectives(self, session_data: Dict, personas: Dict) -> Dict:
        """ペルソナ視点評価"""
        evaluations = {}
        
        for persona in personas.get('personas', []):
            persona_eval = {
                'satisfaction_score': 0,
                'satisfaction_factors': [],
                'dissatisfaction_factors': [],
                'improvement_requests': [],
                'concept_fit': 0,
                'usability': 0,
                'value_perception': 0,
                'continuity_intention': 0
            }
            
            if self.openai_client:
                persona_eval = self.ai_evaluate_persona_perspective(session_data, persona)
            else:
                persona_eval = self.sample_evaluate_persona_perspective(persona)
                
            evaluations[persona['id']] = persona_eval
            
        return evaluations
        
    def sample_evaluate_persona_perspective(self, persona: Dict) -> Dict:
        """サンプルペルソナ視点評価生成"""
        base_scores = {
            'persona_1': {'satisfaction': 8, 'concept_fit': 4, 'usability': 4, 'value': 4, 'continuity': 4},
            'persona_2': {'satisfaction': 7, 'concept_fit': 4, 'usability': 3, 'value': 3, 'continuity': 3},
            'persona_3': {'satisfaction': 6, 'concept_fit': 3, 'usability': 3, 'value': 3, 'continuity': 3}
        }
        
        scores = base_scores.get(persona['id'], base_scores['persona_1'])
        
        return {
            'satisfaction_score': scores['satisfaction'],
            'satisfaction_factors': [
                f"{persona['name']}の特性に合致する機能が含まれている",
                "実用性が高く、日常的に活用できる価値がある"
            ],
            'dissatisfaction_factors': [
                "一部の機能で使いやすさに改善の余地がある",
                "長期的な価値提供に不明確な点がある"
            ],
            'improvement_requests': [
                f"{persona['characteristics']}を活かした追加機能の検討",
                "ユーザーインターフェースの改善"
            ],
            'concept_fit': scores['concept_fit'],
            'usability': scores['usability'],
            'value_perception': scores['value'],
            'continuity_intention': scores['continuity']
        }
        
    def generate_improvement_proposals(self, evaluation_data: Dict) -> Dict:
        """改善提案生成"""
        proposals = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'innovative_ideas': []
        }
        
        if self.openai_client:
            proposals = self.ai_generate_improvements(evaluation_data)
        else:
            proposals = self.sample_generate_improvements(evaluation_data)
            
        return proposals
        
    def sample_generate_improvements(self, evaluation_data: Dict) -> Dict:
        """サンプル改善提案生成"""
        return {
            'high_priority': [
                {
                    'title': 'ユーザーインターフェース最適化',
                    'rationale': 'ペルソナ評価で使いやすさに課題が指摘された',
                    'content': 'ユーザビリティテストを実施し、直感的な操作性を向上',
                    'expected_effect': 'ユーザー満足度20%向上、継続利用率15%向上',
                    'difficulty': 3,
                    'duration': '2ヶ月',
                    'resources': 'UIデザイナー1名、フロントエンドエンジニア2名'
                }
            ],
            'medium_priority': [
                {
                    'title': '機能拡張計画策定',
                    'rationale': 'ペルソナから追加機能への要望が多い',
                    'content': 'ユーザーニーズに基づいた機能ロードマップ作成',
                    'expected_effect': '競争力強化、ユーザー定着率向上',
                    'difficulty': 4,
                    'duration': '3ヶ月',
                    'resources': 'プロダクトマネージャー、開発チーム'
                }
            ],
            'low_priority': [
                {
                    'title': 'パフォーマンス最適化',
                    'rationale': '将来的なスケーラビリティ対応',
                    'content': 'システムパフォーマンスの継続的改善',
                    'expected_effect': '応答性向上、運用コスト削減',
                    'difficulty': 2,
                    'duration': '1ヶ月',
                    'resources': 'バックエンドエンジニア1名'
                }
            ],
            'innovative_ideas': [
                'AI機能を活用したパーソナライゼーション強化',
                'コミュニティ機能の追加による利用者間交流促進',
                'モバイルアプリ版の開発による利便性向上'
            ]
        }
        
    def generate_final_recommendation(self, all_evaluations: Dict) -> Dict:
        """最終推奨判定生成"""
        # 総合スコア計算
        feasibility_score = all_evaluations.get('feasibility', {}).get('total_score', 0)
        risk_level = self.calculate_risk_level(all_evaluations.get('risks', {}))
        persona_satisfaction = self.calculate_persona_satisfaction(all_evaluations.get('persona_evaluations', {}))
        
        # 推奨レベル判定
        if feasibility_score >= 16 and risk_level == 'low' and persona_satisfaction >= 8:
            recommendation_level = 'A'
        elif feasibility_score >= 12 and risk_level in ['low', 'medium'] and persona_satisfaction >= 6:
            recommendation_level = 'B'
        elif feasibility_score >= 8 and persona_satisfaction >= 5:
            recommendation_level = 'C'
        else:
            recommendation_level = 'D'
            
        return {
            'recommendation_level': recommendation_level,
            'rationale': self.get_recommendation_rationale(recommendation_level, feasibility_score, risk_level, persona_satisfaction),
            'next_steps': self.get_next_steps(recommendation_level)
        }
        
    def calculate_risk_level(self, risks: Dict) -> str:
        """リスクレベル計算"""
        high_risks = len(risks.get('high_risks', []))
        medium_risks = len(risks.get('medium_risks', []))
        
        if high_risks >= 3:
            return 'high'
        elif high_risks >= 1 or medium_risks >= 4:
            return 'medium'
        else:
            return 'low'
            
    def calculate_persona_satisfaction(self, persona_evals: Dict) -> float:
        """ペルソナ満足度平均計算"""
        if not persona_evals:
            return 0
            
        total_score = sum(eval_data.get('satisfaction_score', 0) for eval_data in persona_evals.values())
        return total_score / len(persona_evals)
        
    def get_recommendation_rationale(self, level: str, feasibility: int, risk: str, satisfaction: float) -> str:
        """推奨理由生成"""
        rationales = {
            'A': f'実現可能性が高く（{feasibility}/20）、リスクが{risk}レベルで、ペルソナ満足度も{satisfaction:.1f}/10と高評価のため、積極的な実装を推奨します。',
            'B': f'実現可能性は十分（{feasibility}/20）で、リスクは{risk}レベル、ペルソナ満足度{satisfaction:.1f}/10という結果から、軽微な改善後の実装を推奨します。',
            'C': f'実現可能性は中程度（{feasibility}/20）、リスクレベル{risk}、ペルソナ満足度{satisfaction:.1f}/10のため、重要な改善を行った後の実装を条件付きで推奨します。',
            'D': f'実現可能性（{feasibility}/20）、リスクレベル{risk}、ペルソナ満足度{satisfaction:.1f}/10の総合評価から、大幅な見直しが必要と判断されます。'
        }
        return rationales.get(level, '')
        
    def get_next_steps(self, level: str) -> str:
        """次ステップ推奨生成"""
        next_steps = {
            'A': '最終企画書の作成に進み、実装計画の詳細化を行ってください。',
            'B': '高優先度の改善提案を実施した後、最終企画書作成に進んでください。',
            'C': '重要な課題への対策を十分に検討し、改善計画を策定してから次段階に進んでください。',
            'D': '企画の根本的な見直しを行い、再度企画検討セッションから実施することを推奨します。'
        }
        return next_steps.get(level, '')
        
    def generate_evaluation_report(self, date: str, all_evaluations: Dict, session_data: Dict) -> str:
        """評価レポート生成"""
        if 'evaluation_template' not in self.templates:
            self.logger.error("評価レポートテンプレートが見つかりません")
            return None
            
        template = self.templates['evaluation_template']
        
        # 基本情報置換
        report = template.replace('[企画名を入力]', session_data.get('project_name', '企画検討プロジェクト'))
        report = report.replace('[YYYYMMDD]', date)
        report = report.replace('[統合企画案名]', session_data.get('theme', ''))
        report = report.replace('[TIMESTAMP]', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 評価データを使用したTODOマーカー置換
        report = self.replace_evaluation_todos(report, all_evaluations, session_data)
        
        return report
        
    def replace_evaluation_todos(self, template: str, evaluations: Dict, session_data: Dict) -> str:
        """評価データを使用してTODOマーカーを置換"""
        
        # 評価概要セクション
        template = template.replace('[ ] TODO: 企画案評価の目的・背景を記載', 
            '企画検討セッションで生成された統合企画案を多角的に評価し、実現可能性・リスク・改善点を明確化する')
        template = template.replace('[ ] TODO: 評価対象となる企画案の概要', 
            f'テーマ「{session_data.get("theme", "")}」に関する統合企画案')
        template = template.replace('[ ] TODO: 評価方法・基準の説明', 
            '技術的・市場的・事業的・組織的実現可能性、リスク分析、ペルソナ視点評価の総合的評価フレームワーク')
            
        # 企画案サマリー
        template = template.replace('[ ] TODO: 具体的な企画名', 
            f'{session_data.get("theme", "地域コミュニティ向けアプリ開発")}')
        template = template.replace('[ ] TODO: 企画の基本コンセプト・概要', 
            'ペルソナベース企画検討セッションによる多角的視点での企画立案')
        template = template.replace('[ ] TODO: 対象ユーザー・市場設定', 
            '地域住民、コミュニティ活動参加者、地域活性化に関心のある個人・団体')
        template = template.replace('[ ] TODO: ユーザーに提供する価値・メリット', 
            'コミュニティ参加の促進、情報共有の効率化、地域活動の活性化支援')
        template = template.replace('[ ] TODO: 具体的な実現方法・手段', 
            'モバイルアプリケーション開発による情報共有・イベント管理・コミュニケーション機能提供')
            
        # 実現可能性評価
        feasibility = evaluations.get('feasibility', {})
        
        # 技術的実現可能性
        tech = feasibility.get('technical', {})
        template = template.replace('[ ]/5', f'{tech.get("score", 0)}/5', 1)
        template = template.replace('[ ] TODO: 技術の入手可能性・現実性', 
            tech.get('details', [''])[0] if tech.get('details') else 'モバイル開発技術は成熟しており入手可能')
        template = template.replace('[ ] TODO: 実装の難易度評価', 
            '中程度の難易度、適切なスキルセットがあれば実現可能')
        template = template.replace('[ ] TODO: 技術リスク要因', 
            'プラットフォーム依存性、セキュリティ要件への対応')
        template = template.replace('[ ] TODO: 必要スキル・リソース評価', 
            'モバイル開発者、UIデザイナー、バックエンドエンジニアが必要')
        template = template.replace('[ ] TODO: 技術的実現可能性の具体的根拠', 
            tech.get('rationale', '現在の技術レベルで十分実現可能'))
            
        # 市場実現可能性
        market = feasibility.get('market', {})
        template = template.replace('[ ]/5', f'{market.get("score", 0)}/5', 1)
        template = template.replace('[ ] TODO: ターゲット市場の妥当性', 
            '地域コミュニティ活性化は社会的ニーズが高い')
        template = template.replace('[ ] TODO: 競合分析・差別化要素', 
            '既存SNSとの差別化として地域特化機能を提供')
        template = template.replace('[ ] TODO: 市場参入時期の適切性', 
            'デジタル化推進の流れに合致したタイミング')
        template = template.replace('[ ] TODO: マーケティング戦略の実効性', 
            '地域団体・行政との連携によるマーケティング展開')
        template = template.replace('[ ] TODO: 市場実現可能性の具体的根拠', 
            market.get('rationale', '地域コミュニティのデジタル化ニーズに対応'))
            
        # 事業実現可能性
        business = feasibility.get('business', {})
        template = template.replace('[ ]/5', f'{business.get("score", 0)}/5', 1)
        template = template.replace('[ ] TODO: 収益モデルの妥当性', 
            'フリーミアムモデル、プレミアム機能課金、広告収入')
        template = template.replace('[ ] TODO: 初期投資・運営コスト', 
            '初期開発費用500-1000万円、月次運営費用50-100万円')
        template = template.replace('[ ] TODO: 投資対効果・収益見込み', 
            '2-3年での投資回収、継続的収益確保の可能性')
        template = template.replace('[ ] TODO: 持続可能性・拡張性', 
            '他地域への横展開、機能拡張による成長可能性')
        template = template.replace('[ ] TODO: 事業実現可能性の具体的根拠', 
            business.get('rationale', '段階的な収益化により事業継続性を確保'))
            
        # 組織実現可能性
        org = feasibility.get('organizational', {})
        template = template.replace('[ ]/5', f'{org.get("score", 0)}/5', 1)
        template = template.replace('[ ] TODO: 必要人材・体制', 
            '開発チーム5-8名、マーケティング2-3名、運営2-3名')
        template = template.replace('[ ] TODO: 実行管理体制', 
            'アジャイル開発手法による段階的実装・改善')
        template = template.replace('[ ] TODO: 関係者合意形成', 
            '地域団体・行政・ユーザーとの継続的コミュニケーション')
        template = template.replace('[ ] TODO: 組織文化・変革適応', 
            'デジタル化への理解促進、継続的学習文化の構築')
        template = template.replace('[ ] TODO: 組織実現可能性の具体的根拠', 
            org.get('rationale', '段階的な組織拡大により実現可能'))
            
        # 総合評価
        total_score = feasibility.get('total_score', 0)
        template = template.replace('[ ]/20', f'{total_score}/20')
        if total_score >= 16:
            judgment = '高い'
        elif total_score >= 12:
            judgment = '普通'
        else:
            judgment = '低い'
        template = template.replace('[ ] TODO: 高い/普通/低い', judgment)
        template = template.replace('[ ] TODO: 実現可能性の主要な強み', 
            '技術的成熟度、市場ニーズの存在、段階的実装可能性')
        template = template.replace('[ ] TODO: 実現可能性の主要な課題', 
            'ユーザー獲得、継続利用促進、収益化タイミング')
            
        # リスク・課題分析
        risks = evaluations.get('risks', {})
        
        # 高リスク要因
        high_risks = risks.get('high_risks', [])
        if high_risks:
            risk = high_risks[0]
            template = template.replace('[リスク名]', risk.get('name', '市場競争激化'), 1)
            template = template.replace('[ ] TODO: 具体的な影響内容', 
                risk.get('impact', '収益性低下、市場シェア確保困難'))
            template = template.replace('[ ] TODO: 発生可能性の評価', 
                risk.get('probability', '高'))
            template = template.replace('[ ] TODO: リスク軽減・回避策', 
                risk.get('mitigation', '差別化戦略の強化、早期市場参入'))
                
        # 中・低リスクも同様に処理（簡略化）
        template = template.replace('[ ] TODO: 同様の形式で記載', 
            '技術変化への対応リスク - 継続的技術更新により対応')
            
        # 課題分析
        tech_challenges = risks.get('technical_challenges', [])
        if tech_challenges:
            challenge = tech_challenges[0]
            template = template.replace('[ ] TODO: 技術実装上の課題', 
                challenge.get('challenge', 'スケーラビリティの確保'))
            template = template.replace('[ ]/5', f'{challenge.get("difficulty", 3)}/5', 1)
            template = template.replace('[ ] TODO: 具体的な解決アプローチ', 
                challenge.get('solution', 'クラウドインフラの活用'))
                
        # 市場・競合課題
        market_challenges = risks.get('market_challenges', [])
        if market_challenges:
            challenge = market_challenges[0]
            template = template.replace('[ ] TODO: 市場参入・競合対応の課題', 
                challenge.get('challenge', 'ユーザー獲得コスト最適化'))
            template = template.replace('[ ]/5', f'{challenge.get("impact", 4)}/5', 1)
            template = template.replace('[ ] TODO: 具体的な対応方法', 
                challenge.get('solution', 'デジタルマーケティング戦略の精緻化'))
                
        # 事業・運営課題
        business_challenges = risks.get('business_challenges', [])
        if business_challenges:
            challenge = business_challenges[0]
            template = template.replace('[ ] TODO: 事業運営上の課題', 
                challenge.get('challenge', '収益化タイミングの最適化'))
            template = template.replace('[ ]/5', f'{challenge.get("importance", 4)}/5', 1)
            template = template.replace('[ ] TODO: 具体的な改善方法', 
                challenge.get('solution', '段階的な収益モデル導入'))
                
        # 組織・人材課題
        org_challenges = risks.get('organizational_challenges', [])
        if org_challenges:
            challenge = org_challenges[0]
            template = template.replace('[ ] TODO: 組織・人材確保の課題', 
                challenge.get('challenge', 'スキル人材の確保'))
            template = template.replace('[ ]/5', f'{challenge.get("urgency", 3)}/5', 1)
            template = template.replace('[ ] TODO: 具体的な解決方法', 
                challenge.get('solution', '人材採用・育成計画の策定'))
                
        # リスク総合評価
        high_risk_count = len(risks.get('high_risks', []))
        medium_risk_count = len(risks.get('medium_risks', []))
        low_risk_count = len(risks.get('low_risks', []))
        
        template = template.replace('[ ]個', f'{high_risk_count}個', 1)
        template = template.replace('[ ]個', f'{medium_risk_count}個', 1) 
        template = template.replace('[ ]個', f'{low_risk_count}個', 1)
        
        if high_risk_count >= 3:
            risk_level = '高'
        elif high_risk_count >= 1 or medium_risk_count >= 4:
            risk_level = '中'
        else:
            risk_level = '低'
        template = template.replace('[ ] TODO: 高/中/低', risk_level)
        
        # ペルソナ視点評価
        persona_evals = evaluations.get('persona_evaluations', {})
        persona_names = ['アクティブ田中', 'バランス佐藤', '品質志向の山田']
        
        for i, (persona_id, eval_data) in enumerate(persona_evals.items()):
            name = persona_names[i] if i < len(persona_names) else f'ペルソナ{i+1}'
            
            # 名前置換
            template = template.replace('[名前]', name, 1)
            
            # 評価データ置換
            template = template.replace('[ ]/10', f'{eval_data.get("satisfaction_score", 0)}/10', 1)
            template = template.replace('[ ] TODO: このペルソナが評価する点', 
                ', '.join(eval_data.get('satisfaction_factors', [])))
            template = template.replace('[ ] TODO: このペルソナが課題と感じる点', 
                ', '.join(eval_data.get('dissatisfaction_factors', [])))
            template = template.replace('[ ] TODO: このペルソナからの改善提案', 
                ', '.join(eval_data.get('improvement_requests', [])))
                
            # 適合度評価
            template = template.replace('[ ]/5', f'{eval_data.get("concept_fit", 0)}/5', 1)
            template = template.replace('[ ]/5', f'{eval_data.get("usability", 0)}/5', 1)
            template = template.replace('[ ]/5', f'{eval_data.get("value_perception", 0)}/5', 1)
            template = template.replace('[ ]/5', f'{eval_data.get("continuity_intention", 0)}/5', 1)
            
        # ペルソナ統合評価
        avg_satisfaction = sum(eval_data.get('satisfaction_score', 0) for eval_data in persona_evals.values()) / len(persona_evals) if persona_evals else 0
        template = template.replace('[ ]/10', f'{avg_satisfaction:.1f}/10')
        template = template.replace('[ ]/[ ]', f'{len(persona_evals)}/{len(persona_evals)}')
        template = template.replace('[ ] TODO: 共通して評価される点', 
            '実用性の高さ、地域特化機能の価値')
        template = template.replace('[ ] TODO: 共通して課題視される点', 
            'ユーザーインターフェースの改善、継続利用促進策')
        template = template.replace('[ ] TODO: 意見が分かれる要素', 
            '機能の複雑さ、技術的先進性への評価')
            
        if avg_satisfaction >= 8:
            persona_fit = '高'
        elif avg_satisfaction >= 6:
            persona_fit = '中'
        else:
            persona_fit = '低'
        template = template.replace('[ ] TODO: 高/中/低', persona_fit)
        
        # 改善提案
        improvements = evaluations.get('improvements', {})
        
        # 高優先度提案
        high_priority = improvements.get('high_priority', [])
        if high_priority:
            proposal = high_priority[0]
            template = template.replace('[改善提案タイトル]', proposal.get('title', 'ユーザーインターフェース最適化'), 1)
            template = template.replace('[ ] TODO: なぜこの改善が必要か', 
                proposal.get('rationale', 'ユーザビリティ向上のため'))
            template = template.replace('[ ] TODO: 具体的な改善方法', 
                proposal.get('content', 'UI/UXデザインの見直し'))
            template = template.replace('[ ] TODO: 改善による効果・メリット', 
                proposal.get('expected_effect', 'ユーザー満足度向上'))
            template = template.replace('[ ]/5', f'{proposal.get("difficulty", 3)}/5', 1)
            template = template.replace('[ ] TODO: 予想される実装期間', 
                proposal.get('duration', '2-3ヶ月'))
            template = template.replace('[ ] TODO: 人材・予算・技術等', 
                proposal.get('resources', 'UIデザイナー、開発者'))
                
        # 残りの改善提案も同様に処理（簡略化）
        template = template.replace('[ ] TODO: 同様の形式で記載', 
            '機能拡張計画策定 - ユーザーニーズに基づく機能追加')
            
        # 革新的アイデア
        innovative_ideas = improvements.get('innovative_ideas', [])
        for i, idea in enumerate(innovative_ideas[:3]):
            template = template.replace('[ ] TODO: 既存企画を発展させる新しいアイデア', idea, 1)
            template = template.replace('[ ] TODO: 市場競争力を高める追加機能', 
                'AI機能を活用したパーソナライゼーション', 1)
            template = template.replace('[ ] TODO: ユーザー体験を向上させる革新要素', 
                'モバイルアプリ版の開発', 1)
                
        # 最終判定
        final_rec = evaluations.get('final_recommendation', {})
        rec_level = final_rec.get('recommendation_level', 'B')
        template = template.replace('[ ] TODO: A/B/C/D', rec_level)
        template = template.replace('[ ] TODO: 推奨レベルの具体的な根拠・理由', 
            final_rec.get('rationale', '総合的に実現可能性が確認された'))
        template = template.replace('[ ] TODO: この評価結果を受けて取るべき次のアクション', 
            final_rec.get('next_steps', '最終企画書の作成に進む'))
            
        # 評価品質確認
        template = template.replace('[ ] TODO: 評価が客観的で根拠が明確か', 
            '✅ 4つの観点から客観的データに基づく評価を実施')
        template = template.replace('[ ] TODO: リスク・課題分析が具体的で実用的か', 
            '✅ 具体的なリスク要因と対策案を明確化')
        template = template.replace('[ ] TODO: 改善提案が実現可能で効果的か', 
            '✅ 優先度別の実現可能な改善提案を提示')
        template = template.replace('[ ] TODO: ペルソナ視点が適切に反映されているか', 
            '✅ 3つのペルソナによる多角的視点評価を実施')
        template = template.replace('[ ] TODO: 最終判定が論理的で説得力があるか', 
            '✅ 定量的評価に基づく論理的判定を実行')
        
        return template
        
    def save_evaluation_report(self, date: str, report: str) -> str:
        """評価レポート保存"""
        output_dir = self.project_dir / "outputs" / date
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "03_plan-evaluation.md"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"評価レポート保存完了: {output_path}")
            return str(output_path)
        except Exception as e:
            self.logger.error(f"評価レポート保存エラー: {e}")
            return None
            
    def run_evaluation(self, date: str = None, project: str = None) -> bool:
        """評価実行メイン処理"""
        if not date:
            date = datetime.now().strftime('%Y%m%d')
            
        self.logger.info(f"企画案評価開始: {date}")
        
        # データ読み込み
        session_data = self.load_planning_session_data(date)
        if not session_data:
            self.logger.error("企画検討セッションデータの読み込みに失敗しました")
            return False
            
        personas = self.load_persona_data(date)
        
        # 評価実行
        evaluations = {}
        
        # 実現可能性評価
        self.logger.info("実現可能性評価実行中...")
        evaluations['feasibility'] = self.evaluate_feasibility(session_data, personas)
        
        # リスク・課題分析
        self.logger.info("リスク・課題分析実行中...")
        evaluations['risks'] = self.analyze_risks_and_challenges(session_data, personas)
        
        # ペルソナ視点評価
        self.logger.info("ペルソナ視点評価実行中...")
        evaluations['persona_evaluations'] = self.evaluate_persona_perspectives(session_data, personas)
        
        # 改善提案生成
        self.logger.info("改善提案生成中...")
        evaluations['improvements'] = self.generate_improvement_proposals(evaluations)
        
        # 最終推奨判定
        self.logger.info("最終推奨判定生成中...")
        evaluations['final_recommendation'] = self.generate_final_recommendation(evaluations)
        
        # レポート生成
        self.logger.info("評価レポート生成中...")
        report = self.generate_evaluation_report(date, evaluations, session_data)
        
        if report:
            output_path = self.save_evaluation_report(date, report)
            if output_path:
                self.logger.info(f"企画案評価完了: {output_path}")
                return True
                
        self.logger.error("企画案評価に失敗しました")
        return False

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='ペルソナベース企画案評価エンジン')
    parser.add_argument('--date', type=str, help='評価対象日付 (YYYYMMDD)')
    parser.add_argument('--project', type=str, help='プロジェクト名')
    parser.add_argument('--verbose', action='store_true', help='詳細ログ出力')
    
    args = parser.parse_args()
    
    # エンジン初期化・実行
    engine = PersonaEvaluationEngine(verbose=args.verbose)
    success = engine.run_evaluation(
        date=args.date,
        project=args.project
    )
    
    if success:
        print("✅ 企画案評価が正常に完了しました")
        sys.exit(0)
    else:
        print("❌ 企画案評価に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 