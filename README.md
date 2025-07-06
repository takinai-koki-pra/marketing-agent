# 🤖 ペルソナベースAIエージェント

**統計データ分析 + CursorAI活用による実用的なマーケティング支援システム**

## 📋 概要

このプロジェクトは、顧客データを分析してペルソナを生成し、Cursor上でAIを活用してマーケティング戦略を立案する統合システムです。

### 🔧 システム構成

- **データ分析エンジン**: Python（pandas、scikit-learn）でペルソナを自動生成
- **可視化機能**: matplotlib、seabornで統計グラフを生成
- **AI活用**: Cursor上でClaude/GPTを使った戦略立案
- **環境**: Docker統合環境（Python + Node.js）

## 🎯 主要機能

### ✅ 完全自動化（OpenAI APIキー不要）
1. **ペルソナ分析**: 顧客データからペルソナを自動生成
2. **統計分析**: 年齢、収入、職業、地域、ライフスタイル分析
3. **データ可視化**: 分布グラフ、ペルソナ比較チャート
4. **レポート生成**: JSON形式での詳細データ出力

### 💡 Cursor AI活用（手動・対話型）
5. **企画立案**: 生成されたペルソナデータを元にした戦略策定
6. **マーケティング設計**: ペルソナ別アプローチ設計
7. **ユーザーテスト設計**: テストシナリオとフィードバック設計
8. **収益モデル検討**: 購買行動に基づく収益構造設計

## 🔧 セットアップ（初回のみ）

### 🤖 Claude Code機能セットアップ（推奨）

```powershell
# 1. プロジェクトディレクトリに移動
cd marketing-agent

# 2. Claude API依存関係インストール
pip install anthropic==0.7.7

# 3. 環境変数設定
# PowerShellで環境変数を設定
$env:ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# または.envファイルを作成
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
```

### 🐳 Docker環境セットアップ（従来通り）

```powershell
# 1. プロジェクトディレクトリに移動
cd marketing-agent

# 2. Docker環境起動
docker-compose up -d --build

# 3. 動作確認
docker-compose ps
```

### 🖥️ ローカル環境（オプション）

```powershell
# Python環境構築
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements-basic.txt

# Node.js依存関係
npm install
```

## 🎯 使用方法

### 🤖 Claude Code機能を使用した分析（推奨）

```powershell
# Claude Code機能でペルソナ分析実行
python agents/persona/workflows/claude_code_analyzer.py --date $(Get-Date -Format "yyyyMMdd") --verbose

# 特定の日付で実行
python agents/persona/workflows/claude_code_analyzer.py --date 20250129 --verbose
```

**Claude Code機能の特徴:**
- 🔥 **リアルタイムコード実行**: データ分析・可視化を即座に実行
- 📊 **インタラクティブ分析**: グラフ・チャートを生成しながら分析
- 🎯 **高度な統計分析**: 機械学習・クラスタリング・相関分析
- 🚀 **AI駆動分析**: Claudeが分析結果を解釈・提案

### 📊 従来のペルソナ分析実行

```powershell
# Docker環境でペルソナ分析実行
docker-compose exec persona-agent python agents/persona/workflows/setup_project.py --date $(Get-Date -Format "yyyyMMdd")
docker-compose exec persona-agent python agents/persona/workflows/persona_analyzer.py --project $(Get-Date -Format "yyyyMMdd") --sample
```

**出力ファイル:**
- `agents/persona/outputs/YYYYMMDD/persona-analysis-YYYYMMDD.json` - 詳細分析結果
- `agents/persona/outputs/YYYYMMDD/visualizations/` - 可視化グラフ

### 💡 Step 2: Cursor AIで戦略立案

生成されたペルソナデータを元に、Cursor上でAIと対話しながら戦略を立案：

1. **ペルソナデータ確認**
   ```powershell
   # 生成されたペルソナデータをCursorで開く
   code agents/persona/outputs/YYYYMMDD/persona-analysis-YYYYMMDD.json
   ```

2. **AI活用例**
   - 「このペルソナデータを元に、モバイルアプリの企画を立案して」
   - 「各ペルソナに効果的なマーケティング戦略を提案して」
   - 「ユーザーテストのシナリオを作成して」

### 📋 Step 3: 成果物作成

Cursor AIとの対話結果を整理・文書化：

```powershell
# 成果物ディレクトリ作成
mkdir products/YYYYMMDD
cd products/YYYYMMDD

# 以下のファイルを作成（Cursor AIで支援）
# - 01_persona-analysis.md      # ペルソナ分析結果
# - 02_planning-session.md      # 企画立案セッション
# - 03_marketing-strategy.md    # マーケティング戦略
# - 04_user-test-scenario.md    # ユーザーテストシナリオ
# - 05_business-model.md        # ビジネスモデル
```

## 📁 プロジェクト構造

```
010_marketing_agent/
├── agents/persona/
│   ├── workflows/           # 自動化スクリプト
│   │   ├── setup-project.py
│   │   └── persona-analyzer.py
│   └── outputs/            # 分析結果
│       └── YYYYMMDD/
│           ├── persona-analysis-YYYYMMDD.json
│           └── visualizations/
├── products/               # 最終成果物
│   └── YYYYMMDD/
│       ├── 01_persona-analysis.md
│       ├── 02_planning-session.md
│       └── ...
├── common/knowledge/       # ナレッジベース
├── docker-compose.yml      # Docker環境設定
└── README.md
```

## 🔄 ワークフロー

### 自動化部分（技術的処理）
1. **データ収集・前処理** → 統計分析 → ペルソナ生成
2. **可視化** → JSON出力 → 基礎データ完成

### AI活用部分（戦略立案）
3. **Cursor AI対話** → 企画立案 → 戦略策定
4. **文書化** → レビュー → 最終成果物

## 🚀 実行例

### 基本的な実行フロー

```powershell
# 1. 今日の日付でプロジェクト作成
$today = Get-Date -Format "yyyyMMdd"
docker-compose exec persona-agent python agents/persona/workflows/setup-project.py --date $today

# 2. サンプルデータでペルソナ分析
docker-compose exec persona-agent python agents/persona/workflows/persona-analyzer.py --project $today --sample

# 3. 結果確認
docker-compose exec persona-agent ls -la agents/persona/outputs/$today/

# 4. 分析結果をCursorで開く
code agents/persona/outputs/$today/persona-analysis-$today.json
```

## 🔧 トラブルシューティング

### Docker関連
```powershell
# コンテナ状態確認
docker-compose ps

# コンテナ再起動
docker-compose restart

# ログ確認
docker-compose logs persona-agent
```

### データ確認
```powershell
# 生成されたファイル確認
docker-compose exec persona-agent find agents/persona/outputs -name "*.json"

# 可視化ファイル確認
docker-compose exec persona-agent ls -la agents/persona/outputs/*/visualizations/
```

## 💡 Cursor AIとの効果的な対話例

```
「このペルソナデータから、どんなモバイルアプリが求められているか分析して」
「田中さんと佐藤さんの違いを踏まえて、異なるマーケティングアプローチを提案して」
「この3つのペルソナを対象としたユーザーテストを設計して」
```

## 🔧 Claude Code機能の詳細設定

### 🎯 AIプロバイダー選択

プロジェクトは以下のAIプロバイダーをサポートします：

1. **Claude API（推奨）**: コード実行機能対応
2. **OpenAI API**: 従来通りの対話機能
3. **両方使用**: 結果比較分析

### 📝 設定ファイルの編集

`agents/persona/config.yml`で使用するAIプロバイダーを設定：

```yaml
ai_parameters:
  # 使用するAIプロバイダーを選択: "openai", "claude", "both"
  provider: "claude"
  
  # Claude設定
  claude:
    model: "claude-3-sonnet-20240229"
    temperature: 0.7
    max_tokens: 2000
    # Claude Code実行機能を使用
    use_code_execution: true
```

### 🔑 API キーの設定

```powershell
# Claude API Key設定
$env:ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# OpenAI API Key設定（オプション）
$env:OPENAI_API_KEY = "your_openai_api_key_here"
```

### 🚀 実行例

```powershell
# Claude Code機能でコード実行付き分析
python agents/persona/workflows/claude-code-analyzer.py --verbose

# 従来のサンプル分析
python agents/persona/workflows/persona-analyzer.py --sample
```

---

**🚀 統計分析（自動）+ Claude Code実行 + AI対話（手動）で効率的なマーケティング戦略立案！**