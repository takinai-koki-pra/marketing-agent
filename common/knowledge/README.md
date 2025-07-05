# 📚 ナレッジベース - 企業独自データ管理

## 🎯 概要

このフォルダは企業独自のナレッジベースを格納し、AIエージェントが参照できる形で管理します。
顧客対応データ、業界情報、テンプレートなどを体系的に整理し、高精度な企画・分析を支援します。

## 📁 ディレクトリ構成

```
common/knowledge/
├─ customer-support/          # 🎧 顧客対応データ
│   ├─ inquiries/            # 問い合わせ履歴
│   ├─ solutions/            # 解決事例
│   ├─ feedback/             # 顧客フィードバック
│   └─ personas/             # 顧客ペルソナデータ
├─ industry/                 # 🏢 業界・市場データ
│   ├─ market-research/      # 市場調査レポート
│   ├─ competitor-analysis/  # 競合分析
│   ├─ trends/              # 業界トレンド
│   └─ regulations/         # 法規制情報
├─ company/                  # 🏛️ 自社情報
│   ├─ products/            # 製品・サービス情報
│   ├─ organization/        # 組織・人員情報
│   ├─ strategy/            # 戦略・方針
│   └─ performance/         # 業績・KPI
└─ templates/               # 📋 共通テンプレート
    ├─ marp-themes/         # プレゼンテーションテーマ
    ├─ documents/           # 文書テンプレート
    └─ formats/             # データ形式定義
```

## 📝 データ形式ガイドライン

### 基本原則
- **Markdown形式**: 可読性とAI処理の両立
- **JSON形式**: 構造化データ（メタデータ・統計情報）
- **統一命名規則**: `YYYY-MM-DD_category_title.md`

### ファイル構造例

#### 顧客問い合わせデータ
```markdown
---
date: "2024-12-15"
category: "product-inquiry"
priority: "high"
customer_segment: "enterprise"
resolution_status: "resolved"
tags: ["pricing", "integration", "api"]
---

# 顧客問い合わせ: API統合に関する価格相談

## 問い合わせ内容
大手企業からのAPI統合に関する価格体系の相談...

## 対応内容
技術担当者との打ち合わせを設定し...

## 解決結果
カスタム価格プランを提案し、契約締結...

## 学んだこと・改善点
- 初期ヒアリングでの技術要件確認が重要
- 価格提示前の価値説明が効果的
```

#### 業界トレンドデータ
```markdown
---
date: "2024-12-01"
industry: "fintech"
source: "業界レポート2024"
reliability: "high"
impact_level: "significant"
---

# フィンテック業界トレンド: AI活用の加速

## トレンド概要
2024年下半期、フィンテック業界では...

## 市場への影響
- 従来サービスの自動化加速
- 新規参入企業の増加
- 規制対応の複雑化

## 自社への示唆
当社製品への影響と対応策...
```

## 🔍 検索・活用方法

### 1. Vector DB統合（推奨）
```python
# common/scripts/ingest_knowledge.py で自動インデックス化
python common/scripts/ingest_knowledge.py --update-all
```

### 2. 手動検索
```python
# agents 内でのナレッジ参照例
from common.utils.knowledge_search import search_knowledge

results = search_knowledge(
    query="顧客からのAPI統合相談事例",
    categories=["customer-support", "company/products"],
    limit=5
)
```

### 3. プロンプト内での参照
```yaml
# agents/*/config.yml での設定例
knowledge_base:
  priority_sources:
    - "customer-support/inquiries"
    - "industry/trends" 
    - "company/products"
  search_context: "製品企画に関連する顧客フィードバックと市場トレンド"
```

## 📊 データ品質管理

### 定期メンテナンス
- **月次**: 古いデータのアーカイブ
- **四半期**: カテゴリ分類の見直し
- **年次**: 全体構造の最適化

### 品質チェックポイント
1. **完全性**: 必要なメタデータが揃っているか
2. **正確性**: 情報の信頼性・最新性
3. **一貫性**: 命名規則・フォーマットの統一
4. **関連性**: AIエージェントでの活用可能性

## 🚀 データ追加手順

### 新規データ追加
1. **カテゴリ判定**: 適切なフォルダを選択
2. **ファイル作成**: 命名規則に従ってMarkdown作成
3. **メタデータ設定**: YAML Front Matterで属性定義
4. **インデックス更新**: `ingest_knowledge.py` 実行

### バッチ処理
```powershell
# 複数ファイル一括追加
python common/scripts/batch_import.py --source "path/to/data" --category "customer-support"
```

## 🔒 セキュリティ・プライバシー

### 機密情報の取り扱い
- **個人情報**: 仮名化・匿名化処理
- **企業秘密**: アクセス制御設定
- **第三者情報**: 利用許諾の確認

### ファイル暗号化（オプション）
```powershell
# 機密データの暗号化
python common/scripts/encrypt_knowledge.py --category "confidential"
```

## 📈 活用効果測定

### KPI例
- **検索精度**: 関連データのヒット率
- **応答品質**: AIエージェントの回答精度向上
- **作業効率**: 企画・分析作業の時間短縮

### ログ分析
```python
# ナレッジ活用状況の分析
python common/scripts/analyze_usage.py --period "last-month"
```

---

**最終更新**: 2024年12月15日  
**管理者**: プロジェクトチーム  
**次回見直し**: 2025年3月15日 