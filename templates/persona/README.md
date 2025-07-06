# 📁 成果物・テンプレート管理システム

## 🎯 概要

このシステムは、AIエージェントが生成する成果物を体系的に管理し、品質と再利用性を確保します。
テンプレート駆動で一貫した出力品質を保ち、中間成果物も含めて完全なトレーサビリティを提供します。

## 🏗️ ディレクトリ構造

```
products/
├── <agent_name>/                 # エージェント別管理
│   ├── templates/               # 📋 出力テンプレート
│   │   ├── README.md           # このファイル
│   │   ├── 01_persona-analysis.md    # ペルソナ分析テンプレート
│   │   ├── 02_planning-session.md    # 企画検討セッションテンプレート
│   │   ├── 03_plan-evaluation.md     # 企画評価テンプレート
│   │   ├── 04_final-proposal.md      # 最終企画書テンプレート
│   │   ├── 05_completion-report.md   # 完了レポートテンプレート
│   │   └── 06_presentation.md        # プレゼンテーションテンプレート
│   └── <YYYYMMDD>/             # 📅 日付別成果物
│       ├── reports/            # 📊 最終成果物
│       │   ├── 01_persona-analysis.md
│       │   ├── 04_final-proposal.md
│       │   └── 06_presentation.md
│       ├── temp/               # 🔄 中間成果物
│       │   ├── draft_analysis.md
│       │   ├── session_notes.md
│       │   └── evaluation_draft.md
│       ├── data/               # 📈 分析データ
│       │   ├── persona-data-YYYYMMDD.json
│       │   └── analysis-results-YYYYMMDD.json
│       └── assets/             # 🎨 画像・資料
│           ├── charts/
│           ├── diagrams/
│           └── presentation-files/
```

## 📋 ファイル命名規則

### プロジェクトディレクトリ
- **形式**: `YYYYMMDD_接頭辞`
- **例**: 
  - `20250703_persona` - ペルソナ分析プロジェクト
  - `20250704_marketing` - マーケティング企画プロジェクト
  - `20250705_product` - 商品企画プロジェクト

### 成果物ファイル
- **01_persona-analysis.md** - ペルソナ分析レポート
- **02_planning-session.md** - 企画検討セッション記録
- **03_plan-evaluation.md** - 企画評価・改善提案
- **04_final-proposal.md** - 最終企画書
- **05_completion-report.md** - プロジェクト完了レポート
- **06_presentation.md** - プレゼンテーション資料（MARP用）

### 補助ファイル
- **data/**: 分析データ・統計情報
  - `persona-data-YYYYMMDD.json`
  - `analysis-results-YYYYMMDD.json`
- **visualizations/**: グラフ・チャート画像
  - `age_distribution.png`
  - `income_distribution.png`
  - `persona_distribution.png`
- **presentation-files/**: プレゼンテーション関連
  - `slides.pptx`
  - `slides.html`
  - `assets/`

## 🔄 ワークフロー

### 1. プロジェクト開始
```powershell
# プロジェクト作成（自動でテンプレートコピー）
python workflows/setup-project.py --date 20250703 --prefix persona
```

### 2. 各プロセス実行
```powershell
# ペルソナ分析実行
python workflows/persona-analyzer.py --project 20250703_persona

# 企画検討セッション実行
python workflows/planning-session.py --project 20250703_persona

# 企画評価実行
python workflows/plan-evaluation.py --project 20250703_persona
```

### 3. 成果物確認
```powershell
# 進捗確認
python workflows/check-progress.py --project 20250703_persona

# 品質チェック
findstr /n "TODO" output/20250703_persona/*.md
```

## 📊 テンプレートシステム

### テンプレートの特徴
- **TODOマーカー**: `<!-- TODO_XXX -->` で置換箇所を明示
- **構造化**: 統一されたセクション構成
- **再利用性**: 業界・プロジェクト問わず使用可能
- **品質保証**: 必須項目・チェックポイント組み込み

### テンプレート更新
```powershell
# テンプレート更新後、既存プロジェクトに反映
python workflows/update-templates.py --project 20250703_persona
```

## 🎯 品質管理

### 完了条件
- [ ] 全TODOマーカーが実際の内容に置換済み
- [ ] 各セクションが適切に記入済み
- [ ] データファイル・画像が正常に生成済み
- [ ] プレゼンテーション資料が正常表示

### 品質チェックポイント
- **論理的整合性**: 前工程の結果を適切に参照
- **具体性**: 抽象的でなく実用的な内容
- **完全性**: 必須項目の漏れなし
- **実現可能性**: 現実的で実行可能な提案

---

**🎯 目標**: 統一された品質で、再利用可能な成果物を効率的に生成するシステムの構築

*最終更新: 2025年7月3日* 