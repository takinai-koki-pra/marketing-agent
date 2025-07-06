#!/usr/bin/env python3
"""
製品企画エージェント

市場調査・競合分析・製品仕様策定・ロードマップ作成を行う
製品企画専門AIエージェントの実装。

使用例:
    from agents.product_planning.workflows.product_planning_agent import ProductPlanningAgent
    
    agent = ProductPlanningAgent()
    result = agent.analyze_market("SaaS市場", "マーケティングオートメーション")
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from common.utils.agent_base import OpenAIAgentBase
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ProductPlanningAgent(OpenAIAgentBase):
    """製品企画エージェント実装クラス"""
    
    def __init__(self):
        super().__init__(
            agent_name="product-planning",
            display_name="製品企画エージェント"
        )

    def analyze_market(self, target_market: str, product_category: str,
                      additional_context: Optional[str] = None) -> str:
        """
        市場調査・分析を実行
        
        Args:
            target_market: 対象市場
            product_category: 製品カテゴリ
            additional_context: 追加コンテキスト
            
        Returns:
            市場分析結果
        """
        # 要件の明確化
        requirements = {
            "target_market": target_market,
            "product_category": product_category,
            "objective": "市場調査・分析",
            "scope": "市場規模・競合・顧客セグメント分析"
        }
        
        if additional_context:
            requirements["additional_context"] = additional_context
        
        # 不明点の確認
        clarified_requirements = self.clarify_requirements(requirements)
        
        # テンプレートを使用してプロンプト構築
        template = self.config["user_prompt_templates"]["market_research"]
        prompt = template.format(
            target_market=clarified_requirements["target_market"],
            product_category=clarified_requirements["product_category"]
        )
        
        # ナレッジベースを活用して実行
        knowledge_query = f"{target_market} {product_category} 市場調査 競合分析"
        result = self.execute_with_knowledge(
            task_name="市場調査分析",
            user_input=prompt,
            knowledge_query=knowledge_query
        )
        
        return result

    def create_product_concept(self, market_research_data: str, 
                             target_customers: str, problem_statement: str) -> str:
        """
        製品コンセプトを策定
        
        Args:
            market_research_data: 市場調査結果
            target_customers: ターゲット顧客
            problem_statement: 解決したい課題
            
        Returns:
            製品コンセプト
        """
        # テンプレートを使用してプロンプト構築
        template = self.config["user_prompt_templates"]["product_concept"]
        prompt = template.format(
            market_research_data=market_research_data,
            target_customers=target_customers,
            problem_statement=problem_statement
        )
        
        # ナレッジベースを活用して実行
        knowledge_query = f"製品企画 コンセプト策定 {target_customers}"
        result = self.execute_with_knowledge(
            task_name="製品コンセプト策定",
            user_input=prompt,
            knowledge_query=knowledge_query
        )
        
        return result

    def create_product_specification(self, product_concept: str,
                                   technical_constraints: str,
                                   development_timeline: str) -> str:
        """
        製品仕様を策定
        
        Args:
            product_concept: 製品コンセプト
            technical_constraints: 技術制約
            development_timeline: 開発期間
            
        Returns:
            製品仕様書
        """
        # テンプレートを使用してプロンプト構築
        template = self.config["user_prompt_templates"]["product_specification"]
        prompt = template.format(
            product_concept=product_concept,
            technical_constraints=technical_constraints,
            development_timeline=development_timeline
        )
        
        # ナレッジベースを活用して実行
        knowledge_query = "製品仕様 技術要件 開発プロセス"
        result = self.execute_with_knowledge(
            task_name="製品仕様策定",
            user_input=prompt,
            knowledge_query=knowledge_query
        )
        
        return result

    def create_product_roadmap(self, product_specifications: str,
                             development_resources: str,
                             launch_target: str) -> str:
        """
        製品ロードマップを作成
        
        Args:
            product_specifications: 製品仕様
            development_resources: 開発リソース
            launch_target: 市場投入目標
            
        Returns:
            製品ロードマップ
        """
        # テンプレートを使用してプロンプト構築
        template = self.config["user_prompt_templates"]["product_roadmap"]
        prompt = template.format(
            product_specifications=product_specifications,
            development_resources=development_resources,
            launch_target=launch_target
        )
        
        # ナレッジベースを活用して実行
        knowledge_query = "製品ロードマップ 開発計画 リリース戦略"
        result = self.execute_with_knowledge(
            task_name="製品ロードマップ作成",
            user_input=prompt,
            knowledge_query=knowledge_query
        )
        
        return result

    def analyze_competitors(self, competitors_list: str, product_category: str) -> str:
        """
        競合分析を実行
        
        Args:
            competitors_list: 競合他社リスト
            product_category: 製品カテゴリ
            
        Returns:
            競合分析結果
        """
        # テンプレートを使用してプロンプト構築
        template = self.config["user_prompt_templates"]["competitive_analysis"]
        prompt = template.format(
            competitors_list=competitors_list,
            product_category=product_category
        )
        
        # ナレッジベースを活用して実行
        knowledge_query = f"競合分析 {competitors_list} {product_category}"
        result = self.execute_with_knowledge(
            task_name="競合分析",
            user_input=prompt,
            knowledge_query=knowledge_query
        )
        
        return result

    def execute_full_planning_process(self, initial_brief: str) -> Dict[str, str]:
        """
        製品企画の全プロセスを実行
        
        Args:
            initial_brief: 初期ブリーフィング
            
        Returns:
            各段階の成果物を含む辞書
        """
        print(f"\n🚀 {self.display_name}による製品企画プロセスを開始します")
        print("=" * 60)
        
        results = {}
        
        # 1. 要件明確化
        print("\n📋 Step 1: 要件明確化")
        requirements = self._parse_initial_brief(initial_brief)
        clarified_requirements = self.clarify_requirements(requirements)
        
        # 2. 市場調査
        print("\n📊 Step 2: 市場調査・分析")
        market_analysis = self.analyze_market(
            clarified_requirements.get("target_market", ""),
            clarified_requirements.get("product_category", ""),
            clarified_requirements.get("additional_context", "")
        )
        results["market_analysis"] = market_analysis
        self.save_final_result("01_market-analysis", market_analysis)
        
        # 3. 製品コンセプト策定
        print("\n💡 Step 3: 製品コンセプト策定")
        target_customers = self.ask_user_input(
            "ターゲット顧客について詳しく教えてください（ペルソナ・属性など）"
        )
        problem_statement = self.ask_user_input(
            "解決したい課題・ペインポイントを具体的に教えてください"
        )
        
        product_concept = self.create_product_concept(
            market_analysis, target_customers, problem_statement
        )
        results["product_concept"] = product_concept
        self.save_final_result("02_product-concept", product_concept)
        
        # 4. 製品仕様策定
        print("\n🏗️ Step 4: 製品仕様策定")
        technical_constraints = self.ask_user_input(
            "技術的制約があれば教えてください（技術スタック・インフラ・予算など）",
            required=False
        )
        development_timeline = self.ask_user_input(
            "希望する開発期間・リリース時期を教えてください"
        )
        
        product_spec = self.create_product_specification(
            product_concept, technical_constraints, development_timeline
        )
        results["product_specification"] = product_spec
        self.save_final_result("03_product-specification", product_spec)
        
        # 5. 製品ロードマップ作成
        print("\n🗓️ Step 5: 製品ロードマップ作成")
        development_resources = self.ask_user_input(
            "開発リソースについて教えてください（チーム規模・スキル・予算など）"
        )
        launch_target = self.ask_user_input(
            "市場投入の目標・戦略について教えてください"
        )
        
        roadmap = self.create_product_roadmap(
            product_spec, development_resources, launch_target
        )
        results["product_roadmap"] = roadmap
        self.save_final_result("04_product-roadmap", roadmap)
        
        # 6. 競合分析（オプション）
        do_competitive_analysis = self.ask_user_confirmation(
            "競合分析も実行しますか？",
            ["はい", "いいえ"]
        )
        
        if do_competitive_analysis == "はい":
            print("\n⚖️ Step 6: 競合分析")
            competitors = self.ask_user_input(
                "主要な競合他社を教えてください（カンマ区切り）"
            )
            
            competitive_analysis = self.analyze_competitors(
                competitors, clarified_requirements.get("product_category", "")
            )
            results["competitive_analysis"] = competitive_analysis
            self.save_final_result("05_competitive-analysis", competitive_analysis)
        
        # 7. 最終レポート生成
        print("\n📝 Step 7: 最終レポート生成")
        final_report = self._generate_final_report(results)
        self.save_final_result("06_final-report", final_report)
        
        print("\n✅ 製品企画プロセス完了！")
        print(f"📁 成果物は以下に保存されました: products/{self.agent_name}/{self._current_project_date}/reports/")
        
        return results

    def _parse_initial_brief(self, brief: str) -> Dict[str, str]:
        """初期ブリーフィングを解析"""
        # 簡単なキーワード抽出（実際はより高度な自然言語処理を使用）
        requirements = {
            "target": brief,
            "objective": "製品企画",
            "scope": "市場調査から製品仕様まで"
        }
        
        # キーワードベースの抽出
        if "市場" in brief or "マーケット" in brief:
            requirements["target_market"] = brief
        
        if any(keyword in brief for keyword in ["SaaS", "アプリ", "システム", "プラットフォーム"]):
            requirements["product_category"] = "ソフトウェア製品"
        
        return requirements

    def _generate_final_report(self, results: Dict[str, str]) -> str:
        """最終レポートを生成"""
        report_sections = [
            "# 📋 製品企画 最終レポート",
            f"\n**作成日**: {self.get_project_status()['last_updated']}",
            f"**作成者**: {self.display_name}",
            "\n---\n"
        ]
        
        # 各セクションを追加
        section_titles = {
            "market_analysis": "## 📊 市場調査・分析",
            "product_concept": "## 💡 製品コンセプト",
            "product_specification": "## 🏗️ 製品仕様",
            "product_roadmap": "## 🗓️ 製品ロードマップ",
            "competitive_analysis": "## ⚖️ 競合分析"
        }
        
        for key, title in section_titles.items():
            if key in results:
                report_sections.extend([
                    title,
                    results[key],
                    "\n---\n"
                ])
        
        # 次のアクション提案
        report_sections.extend([
            "## 🎯 次のアクション",
            "- プロトタイプ開発の開始",
            "- ステークホルダーとの仕様レビュー",
            "- 開発チームとの技術検討",
            "- 予算・リソース確保の検討",
            "- 市場投入戦略の詳細化"
        ])
        
        return "\n".join(report_sections)

def main():
    """メイン実行関数"""
    agent = ProductPlanningAgent()
    
    print("🚀 製品企画エージェントへようこそ！")
    print("新しい製品・サービスの企画をお手伝いします。\n")
    
    initial_brief = agent.ask_user_input(
        "企画したい製品・サービスについて教えてください（市場・課題・アイデアなど）"
    )
    
    try:
        results = agent.execute_full_planning_process(initial_brief)
        
        print("\n🎉 製品企画が完了しました！")
        print("詳細な成果物をご確認ください。")
        
    except KeyboardInterrupt:
        print("\n⏸️ 処理が中断されました。")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        logger.error(f"製品企画プロセスエラー: {e}")

if __name__ == "__main__":
    main() 