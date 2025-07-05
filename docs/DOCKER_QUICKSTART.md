# 🐳 Docker クイックスタートガイド

## 概要
ペルソナベースAIエージェントをDocker環境で実行し、統計データ分析とCursor AIを活用してマーケティング戦略を立案するガイドです。

**🔑 重要**: OpenAI APIキーは不要！統計分析は自動化、戦略立案はCursor AIで実行

## 前提条件
- Windows 10/11
- Docker Desktop for Windows（インストール済み）
- PowerShell
- Cursor（AI機能有効）

## 🚀 5分で開始する手順

### 1. Docker環境起動（30秒）
```powershell
# プロジェクトディレクトリに移動
cd 010_marketing_agent

# Docker環境起動（初回は3-5分、2回目以降は30秒）
docker-compose up -d --build

# 起動確認
docker-compose ps
```

### 2. ペルソナ分析実行（2分）
```powershell
# 今日の日付でプロジェクト作成
$today = Get-Date -Format "yyyyMMdd"
docker-compose exec persona-agent python agents/persona/workflows/setup-project.py --date $today

# サンプルデータでペルソナ分析実行
docker-compose exec persona-agent python agents/persona/workflows/persona-analyzer.py --project $today --sample
```

### 3. 生成結果確認（1分）
```powershell
# 生成されたファイル確認
docker-compose exec persona-agent ls -la agents/persona/outputs/$today/

# 可視化ファイル確認
docker-compose exec persona-agent ls -la agents/persona/outputs/$today/visualizations/
```

### 4. Cursor AIで戦略立案（10分〜）
```powershell
# 分析結果をCursorで開く
code agents/persona/outputs/$today/persona-analysis-$today.json
```

## 📊 実行結果例

### 生成されるファイル
```
agents/persona/outputs/20250129/
├── persona-analysis-20250129.json    # 詳細分析結果
├── persona-data-20250129.json        # 基本データ
├── 01_persona-analysis.md             # テンプレート
└── visualizations/                    # 可視化グラフ
    ├── age_distribution.png           # 年齢分布
    ├── income_distribution.png        # 収入分布
    └── persona_distribution.png       # ペルソナ分布
```

### 生成されるペルソナ例
```json
{
  "personas": [
    {
      "name": "アクティブ田中",
      "characteristics": {
        "typical_age": 26,
        "top_occupation": "会社員",
        "top_region": "関東",
        "top_lifestyle": "家庭重視"
      },
      "detailed_profile": {
        "pain_points": [
          "品質の不安定さや信頼性の欠如",
          "家族との時間を奪われること"
        ],
        "motivations": [
          "家族の幸せ・安心"
        ]
      }
    }
  ]
}
```

## 💡 Cursor AI活用方法

### 1. データ分析・解釈
```
# Cursor AIに質問する例
「このペルソナ分析結果から、どのような傾向が読み取れますか？」
「3つのペルソナの主要な違いを教えてください」
```

### 2. 企画立案
```
# 具体的な企画立案の例
「このペルソナデータを元に、モバイルアプリの企画を立案してください」
「各ペルソナのペインポイントを解決するサービスを提案してください」
```

### 3. マーケティング戦略
```
# マーケティング戦略の例
「田中さん、佐藤さん、山田さんそれぞれに効果的なマーケティングアプローチを設計してください」
「各ペルソナの購買行動に基づいた収益モデルを検討してください」
```

### 4. ユーザーテスト設計
```
# ユーザーテストの例
「この3つのペルソナを対象としたユーザーテストシナリオを作成してください」
「各ペルソナの特徴を活かしたフィードバック項目を設計してください」
```

## 🔧 Docker環境管理

### 基本コマンド
```powershell
# コンテナ状態確認
docker-compose ps

# コンテナ再起動
docker-compose restart

# コンテナ停止
docker-compose down

# ログ確認
docker-compose logs persona-agent
```

### データ確認
```powershell
# 生成されたプロジェクト一覧
docker-compose exec persona-agent ls -la agents/persona/outputs/

# 特定プロジェクトの詳細
docker-compose exec persona-agent ls -la agents/persona/outputs/20250129/

# JSONファイルの内容確認
docker-compose exec persona-agent cat agents/persona/outputs/20250129/persona-analysis-20250129.json
```

## 🎯 実用的な活用パターン

### パターン1: 新規事業企画
1. **ペルソナ分析実行** → 対象顧客の理解
2. **Cursor AI対話** → 事業アイデア発想
3. **戦略立案** → 具体的な事業計画
4. **文書化** → 企画書作成

### パターン2: 既存サービス改善
1. **ペルソナ分析実行** → 現状の顧客分析
2. **Cursor AI対話** → 課題抽出・解決策発想
3. **改善提案** → 具体的な改善計画
4. **テスト設計** → 改善効果の検証方法

### パターン3: マーケティング最適化
1. **ペルソナ分析実行** → ターゲット明確化
2. **Cursor AI対話** → セグメント別戦略立案
3. **施策設計** → 具体的なマーケティング施策
4. **効果測定** → KPI設定・測定方法

## 🚨 トラブルシューティング

### Docker関連
```powershell
# Docker Desktop が起動していない場合
"Docker Desktop を起動してください"

# ポート競合エラー
docker-compose down
docker-compose up -d

# ビルドエラー
docker-compose up -d --build --force-recreate
```

### データ生成エラー
```powershell
# 依存関係エラー
docker-compose exec persona-agent pip list | grep pandas

# 権限エラー
docker-compose exec persona-agent ls -la agents/persona/outputs/

# ファイル確認
docker-compose exec persona-agent find agents/persona/outputs -name "*.json"
```

## 📈 効果測定

### 定量的効果
- **作業時間短縮**: 手動分析比較で80%短縮
- **データ精度向上**: 統計的手法による客観的分析
- **企画品質向上**: AI支援による多角的検討

### 定性的効果
- **顧客理解の深化**: データドリブンな洞察
- **戦略的思考**: 構造化された企画プロセス
- **実装可能性**: 具体的なアクションプラン

## 🎯 次のステップ提案

1. **定期実行**: 月次・四半期でのペルソナ分析実行
2. **データ蓄積**: 時系列での顧客傾向把握
3. **精度向上**: 実績フィードバックによる分析精度向上
4. **組織展開**: チーム全体でのワークフロー標準化

---

**🚀 データドリブンなマーケティング戦略を、今すぐ始めましょう！**

## 📂 ファイル構造（Docker環境）

```
010_marketing_agent/
├── Dockerfile                 # Docker環境定義
├── docker-compose.yml         # サービス構成
├── .dockerignore              # Docker除外ファイル
├── .env                       # 環境変数（要作成）
└── [既存のプロジェクト構造]
```

## 🔧 カスタマイズ

### 環境変数の追加
`.env`ファイルを編集：
```bash
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4
DEBUG=true
LOG_LEVEL=DEBUG
```

### ポート変更
`docker-compose.yml`を編集：
```yaml
ports:
  - "8080:8000"  # 外部8080ポートで接続
  - "3001:3000"  # MARP用ポート変更
```

### 追加パッケージのインストール
```bash
# コンテナ内で一時的インストール
docker-compose exec persona-agent pip install new-package

# 永続化する場合はrequirements.txtに追加後再ビルド
```

## 💻 VS Code + Docker連携

### Dev Containers拡張機能使用
1. VS Code Dev Containers拡張をインストール
2. プロジェクトを開く
3. `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

### 設定ファイル例
`.devcontainer/devcontainer.json`:
```json
{
    "name": "Persona AI Agent",
    "dockerComposeFile": "../docker-compose.yml",
    "service": "persona-agent",
    "workspaceFolder": "/app",
    "extensions": [
        "ms-python.python",
        "ms-python.black-formatter"
    ]
}
```

## 🛡️ セキュリティ注意事項

- `.env`ファイルは絶対にGitにコミットしない
- OpenAI APIキーは適切に管理する
- 本番環境では適切なネットワーク制限を設定する

## 📞 サポート

問題が発生した場合：
1. `docker-compose logs persona-agent`でログ確認
2. `docker-compose down && docker-compose up -d --build`で再構築
3. GitHubのIssuesで報告

---

**最終更新**: 2025年1月29日  
**Docker環境**: Python 3.11 + Node.js 18  
**対応OS**: Windows 10/11 + Docker Desktop 