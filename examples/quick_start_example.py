#!/usr/bin/env python3
"""
リファクタリング後システムのクイックスタート例

このサンプルでは、新しく構築されたシステムの主要機能を
実際に使用する方法を示します。

実行前の準備:
1. .env ファイルに OPENAI_API_KEY を設定
2. pip install -r requirements.txt
3. common/knowledge/ にナレッジデータを配置
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from common.utils import (
    search_knowledge, 
    get_output_manager,
    OutputManager
)

def example_knowledge_search():
    """ナレッジベース検索の例"""
    print("🔍 ナレッジベース検索の例")
    print("=" * 50)
    
    # 1. 基本的な検索
    print("\n1. 基本的な検索:")
    results = search_knowledge(
        query="API統合に関する顧客相談事例",
        categories=["customer-support"],
        limit=3
    )
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata'].get('file_name', '不明')}")
        print(f"     関連度: {result.get('similarity', 0):.2f}")
        print(f"     カテゴリ: {result['metadata'].get('category', '不明')}")
    
    # 2. 製品情報の検索
    print("\n2. 製品情報の検索:")
    product_results = search_knowledge(
        query="SaaS プラットフォーム 機能 価格",
        categories=["company/products"],
        limit=2
    )
    
    for result in product_results:
        print(f"  - {result['metadata'].get('product_name', '製品名不明')}")
        print(f"    ファイル: {result['metadata'].get('file_name', '不明')}")

def example_output_management():
    """成果物管理の例"""
    print("\n📁 成果物管理の例")
    print("=" * 50)
    
    # OutputManagerの初期化
    manager = get_output_manager("example-agent", "20241215")
    
    print(f"プロジェクトパス: {manager.project_path}")
    
    # 中間成果物の保存
    print("\n1. 中間成果物の保存:")
    intermediate_content = """
# 市場調査 - 中間結果

## 調査概要
SaaS市場の競合分析を実施中...

## 暫定結果
- 市場規模: 約1000億円
- 主要プレイヤー: A社、B社、C社
- 成長率: 年15%

## 次のステップ
- 詳細な機能比較
- 価格戦略の分析
"""
    
    saved_path = manager.save_intermediate(
        "market_research_draft",
        intermediate_content,
        metadata={
            "task": "市場調査",
            "status": "進行中",
            "completion": 0.6
        }
    )
    print(f"  保存先: {saved_path}")
    
    # データの保存
    print("\n2. 分析データの保存:")
    analysis_data = {
        "market_size": 100000000000,
        "growth_rate": 0.15,
        "competitors": [
            {"name": "A社", "share": 0.3},
            {"name": "B社", "share": 0.25},
            {"name": "C社", "share": 0.2}
        ]
    }
    
    data_path = manager.save_data("market_analysis_20241215", analysis_data)
    print(f"  保存先: {data_path}")
    
    # プロジェクト状況の確認
    print("\n3. プロジェクト状況:")
    status = manager.get_project_status()
    print(f"  プロジェクトID: {status['project_id']}")
    print(f"  作成日時: {status['created_at']}")
    print(f"  中間ファイル数: {len(status['intermediate_files'])}")
    print(f"  データファイル数: {len(status['data_files'])}")

def main():
    """メイン実行関数"""
    print("🚀 リファクタリング後システム - クイックスタート例")
    print("=" * 60)
    
    try:
        # 各機能の例を実行
        example_knowledge_search()
        example_output_management()
        
        print("\n✅ すべての例が正常に実行されました！")
        print("\n📚 詳細な使用方法:")
        print("  - ナレッジベース: common/knowledge/README.md")
        print("  - 成果物管理: products/persona/templates/README.md")
        print("  - エージェント設定: agents/persona/config.yml")
        print("  - リファクタリング詳細: docs/REFACTORING_SUMMARY.md")
        
    except ImportError as e:
        print(f"❌ 必要なライブラリがインストールされていません: {e}")
        print("pip install -r requirements.txt を実行してください")
    except FileNotFoundError as e:
        print(f"❌ ファイルが見つかりません: {e}")
        print("プロジェクトのセットアップを確認してください")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 