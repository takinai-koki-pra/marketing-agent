# マーケティング・ペルソナエージェント アーキテクチャ設計書

## 📋 概要

本プロジェクトは、企業独自のナレッジベースを活用したAIエージェントシステムです。
ペルソナ分析・企画検討・評価・プレゼンテーション生成を中心に、製品企画・事業企画など幅広い用途に対応可能な拡張性を持つ設計となっています。

## 🏗️ ディレクトリ構成

```
010_marketing_agent/
├─ agents/                        # エージェント実装
│   └─ persona/                   # ペルソナベースAIエージェント
│       ├─ config.yml            # 🔧 プロンプト設定（自然言語）
│       ├─ prompts/              # エージェント固有プロンプト
│       ├─ workflows/            # ワークフロースクリプト
│       └─ src/                  # コードファイル
├─ common/                       # 共通リソース
│   ├─ knowledge/               # 📚 ナレッジベース
│   │   ├─ industry/           # 業界別ナレッジ
│   │   ├─ customer-support/   # 顧客対応データ
│   │   └─ templates/          # 共通テンプレート
│   ├─ prompts/                # 全エージェント共通プロンプト
│   ├─ scripts/                # 汎用ユーティリティ
│   └─ models/                 # AI モデル設定
├─ products/                    # 📊 成果物格納
│   └─ persona/                # ペルソナ分析成果物
│       ├─ YYYYMMDD/          # 日付別フォルダ
│       │   ├─ reports/       # 最終成果物
│       │   ├─ assets/        # 画像・図表
│       │   └─ temp/          # 中間生成物
│       └─ templates/         # 出力テンプレート
├─ docs/                       # 📖 ドキュメント
│   ├─ README.md              # ドキュメント一覧・ナビゲーション
│   ├─ 要件定義書.md
│   ├─ 開発ルール.md
│   ├─ ARCHITECTURE.md        # アーキテクチャ設計書
│   ├─ CHANGELOG.md           # 変更履歴
│   └─ todo.md               # 開発進捗・タスク管理
├─ scripts/                    # Windows用セットアップスクリプト
├─ .env                       # 環境変数設定
├─ requirements.txt           # Python依存関係
├─ package.json              # Node.js依存関係
└─ README.md                 # プロジェクト概要
```

## 🎯 設計原則

### 1. 分離の原則
- **エージェント固有** vs **共通リソース** の明確な分離
- **成果物** vs **テンプレート** vs **中間生成物** の区別
- **設定** vs **実装** の分離

### 2. 拡張性の原則
- 新しいエージェント追加時の影響最小化
- 共通リソースの再利用促進
- プラグイン的なエージェント構成

### 3. 運用効率の原則
- 自然言語でのプロンプトチューニング
- 日付ベースの成果物管理
- 中間成果物の適切な保存

## 🔧 コンポーネント詳細

### エージェント層 (`agents/`)
各エージェントは独立したモジュールとして設計：

**config.yml の役割**
- システムプロンプト（自然言語）
- ユーザープロンプトテンプレート
- AI処理パラメータ
- 出力設定

**フォルダ構成**
- `prompts/`: エージェント固有のプロンプト素材
- `workflows/`: 自動化スクリプト
- `src/`: Python/TypeScript等のコード

### 共通リソース層 (`common/`)
全エージェントで共有するリソース：

**knowledge/ の管理方針**
- `industry/`: 業界別ナレッジ（競合分析、市場データ等）
- `customer-support/`: 過去の顧客問い合わせ・対応データ
- `templates/`: 汎用テンプレート

**scripts/ の役割**
- データ前処理ユーティリティ
- ナレッジベース検索・埋め込み
- 共通ワークフロー

### 成果物層 (`products/`)
日付ベースの成果物管理：

**フォルダ分類**
- `reports/`: 最終成果物（md, pdf, html）
- `assets/`: 画像・図表・データファイル
- `temp/`: 中間生成物（.gitignore対象）

## 🚀 実行フロー

### 1. ナレッジ取り込み
```
common/scripts/ingest_knowledge.py
└─ common/knowledge/ から Vector DB へ取り込み
```

### 2. エージェント実行
```
agents/persona/workflows/run_analysis.py
├─ config.yml からプロンプト読み込み
├─ common/knowledge/ から関連ナレッジ検索
└─ products/persona/YYYYMMDD/ へ出力
```

### 3. 成果物管理
```
products/persona/YYYYMMDD/
├─ temp/ で中間生成物作成
├─ reports/ へ最終成果物昇格
└─ assets/ へ必要な図表保存
```

## 🔄 拡張方法

### 新しいエージェント追加
1. `agents/[new_agent]/` フォルダ作成
2. `config.yml` でプロンプト設定
3. `workflows/` にワークフロー実装
4. `products/[new_agent]/` で成果物管理

### ナレッジベース拡張
1. `common/knowledge/[category]/` に新カテゴリ追加
2. Markdown/JSON形式でデータ格納
3. `common/scripts/` でインデックス更新

## ⚙️ 技術仕様

### 対応環境
- **OS**: Windows 10/11
- **シェル**: PowerShell
- **Python**: 3.8+
- **Node.js**: 16+ (MARP用)

### 依存関係
- OpenAI API
- Vector DB (Chroma/FAISS等)
- YAML解析ライブラリ
- Markdown処理ライブラリ

### セキュリティ
- API キーは環境変数管理
- 顧客データは暗号化推奨
- Git管理対象外ファイルの適切な設定

## 📝 運用ガイドライン

### プロンプトチューニング
1. `agents/[agent]/config.yml` を編集
2. 自然言語で直接記述
3. テンプレート変数 `{{variable}}` を活用

### 成果物管理
- 日付フォルダで自動整理
- `temp/` は定期的にクリーンアップ
- 重要な中間成果物は `reports/` へ昇格

### ナレッジメンテナンス
- 定期的な `common/knowledge/` 更新
- 顧客対応データの継続的な蓄積
- 業界動向の最新情報反映

## 🔍 トラブルシューティング

### よくある問題
1. **プロンプトが効かない** → config.yml の YAML 構文確認
2. **ナレッジが参照されない** → パス設定・権限確認
3. **成果物が見つからない** → 日付フォルダ・ファイル名確認

### ログ確認
- エージェント実行ログ: `agents/[agent]/logs/`
- システムログ: `common/logs/`
- エラーログ: コンソール出力確認 