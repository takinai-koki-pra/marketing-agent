# 📋 OpenAI APIキー不要ワークフローガイド

## 概要
統計データ分析（自動化）+ Cursor AI（手動対話）を組み合わせた実用的なマーケティング戦略立案ワークフロー

## 🔄 ワークフロー全体像

### Phase 1: 自動化処理（5分）
**🔧 技術的処理 - Docker環境で実行**
1. データ収集・前処理
2. 統計分析・クラスタリング
3. ペルソナ自動生成
4. 可視化・JSON出力

### Phase 2: AI活用処理（30分〜）
**💡 戦略立案 - Cursor AIとの対話**
5. データ解釈・洞察抽出
6. 企画立案・戦略策定
7. 実装計画・テスト設計
8. 文書化・レビュー

## 🚀 実践的実行手順

### Step 1: 環境準備（初回のみ）
```powershell
# Docker環境起動
docker-compose up -d --build

# 動作確認
docker-compose ps
```

### Step 2: データ分析実行
```powershell
# 日付設定
$today = Get-Date -Format "yyyyMMdd"

# プロジェクト作成
docker-compose exec persona-agent python agents/persona/workflows/setup-project.py --date $today

# ペルソナ分析実行
docker-compose exec persona-agent python agents/persona/workflows/persona-analyzer.py --project $today --sample
```

### Step 3: 結果確認
```powershell
# 生成ファイル確認
docker-compose exec persona-agent ls -la agents/persona/outputs/$today/

# 分析結果をCursorで開く
code agents/persona/outputs/$today/persona-analysis-$today.json
```

## 💡 Cursor AI活用テンプレート

### 1. データ解釈・洞察抽出
```
【Cursor AIへの質問例】

「このペルソナ分析結果を解釈して、以下の観点で洞察を教えてください：
1. 3つのペルソナの主要な違いと特徴
2. 各ペルソナの課題とニーズ
3. 市場機会の可能性
4. 注意すべきリスク要因

[生成されたJSONデータをここに貼り付け]」
```

### 2. 企画立案
```
【具体的な企画立案】

「このペルソナデータを元に、新しいモバイルアプリの企画を立案してください：

対象ペルソナ：
- アクティブ田中（26歳・家庭重視・品質重視）
- バランス佐藤（37歳・キャリア重視・価格重視）
- 品質志向の山田（36歳・家庭重視・価格重視）

企画内容：
1. アプリのコンセプト
2. 主要機能
3. 各ペルソナへの価値提案
4. 差別化要素
5. 収益モデル
```

### 3. マーケティング戦略
```
【マーケティング戦略立案】

「各ペルソナに効果的なマーケティング戦略を設計してください：

田中さん向け：
- 課題：品質の不安定さ、家族との時間を奪われること
- 動機：家族の幸せ・安心
- 提案：どのようなアプローチが効果的か？

佐藤さん向け：
- 課題：コストパフォーマンスの低さ
- 動機：スキルアップ・キャリア向上
- 提案：どのようなアプローチが効果的か？

山田さん向け：
- 課題：コストパフォーマンスの低さ、家族との時間を奪われること
- 動機：家族の幸せ・安心
- 提案：どのようなアプローチが効果的か？
```

### 4. ユーザーテスト設計
```
【ユーザーテストシナリオ作成】

「この3つのペルソナを対象としたユーザーテストを設計してください：

テスト対象：[企画したサービス名]

各ペルソナの特徴を活かした：
1. テストシナリオ
2. 評価ポイント
3. 質問項目
4. 成功指標
5. 失敗リスク

実際のテスト実施時の注意点も含めて提案してください。」
```

## 📊 実際の実行結果例

### 生成されるデータ構造
```json
{
  "project_info": {
    "data_size": 1000,
    "persona_count": 3
  },
  "demographics": {
    "age_stats": {"mean": 34.7, "median": 35.0},
    "gender_distribution": {"女性": 538, "男性": 462},
    "occupation_distribution": {"会社員": 414, "自営業": 164}
  },
  "personas": [
    {
      "name": "アクティブ田中",
      "characteristics": {
        "typical_age": 26,
        "top_lifestyle": "家庭重視",
        "spending_preference": "品質重視"
      },
      "detailed_profile": {
        "pain_points": ["品質の不安定さ", "家族との時間を奪われること"],
        "motivations": ["家族の幸せ・安心"]
      }
    }
  ]
}
```

### Cursor AI活用結果例
```
【AIによる洞察例】

1. ペルソナ分析：
   - 田中さん：若い家庭重視層、品質を重視
   - 佐藤さん：キャリア志向、コスパ重視
   - 山田さん：家庭とコスパの両方重視

2. 市場機会：
   - 家庭向けサービスの需要が高い
   - 品質とコスパの両立が重要
   - 30代前後がメイン層

3. 企画提案：
   - 家族で使えるタスク管理アプリ
   - 品質保証と価格バランス
   - 時短機能の充実
```

## 📁 成果物テンプレート

### 作成すべきファイル
```
products/YYYYMMDD/
├── 01_persona-analysis.md      # ペルソナ分析結果
├── 02_insights-extraction.md   # AI洞察抽出
├── 03_planning-session.md      # 企画立案セッション
├── 04_marketing-strategy.md    # マーケティング戦略
├── 05_user-test-design.md      # ユーザーテスト設計
├── 06_business-model.md        # ビジネスモデル
└── 07_action-plan.md           # 実装アクションプラン
```

### 各ファイルの内容例
```markdown
# 01_persona-analysis.md

## ペルソナ分析結果

### 生成されたペルソナ
1. アクティブ田中（26歳・家庭重視・品質重視）
2. バランス佐藤（37歳・キャリア重視・価格重視）
3. 品質志向の山田（36歳・家庭重視・価格重視）

### 統計データ
- 対象データ：1,000件
- 年齢分布：平均34.7歳
- 性別比：女性54%、男性46%
- 職業：会社員41%、自営業16%

### 可視化データ
- 年齢分布グラフ
- 収入分布グラフ
- ペルソナ分布グラフ
```

## 🔧 効率化のコツ

### 1. データ解釈の効率化
```powershell
# JSONデータの要点抽出
docker-compose exec persona-agent python -c "
import json
with open('agents/persona/outputs/$today/persona-analysis-$today.json') as f:
    data = json.load(f)
    print('=== ペルソナ要約 ===')
    for p in data['personas']:
        print(f'{p[\"detailed_profile\"][\"name\"]}: {p[\"detailed_profile\"][\"summary\"]}')
"
```

### 2. Cursor AI対話の効率化
- **コンテキスト共有**: 一度にすべてのペルソナデータを共有
- **段階的深堀り**: 概要→詳細→具体化の順で質問
- **テンプレート活用**: 上記のテンプレートを活用

### 3. 文書化の効率化
- **Cursor AI支援**: 文書構造もAIに提案してもらう
- **段階的作成**: 概要→詳細→レビューの順で作成
- **テンプレート活用**: 成果物テンプレートを活用

## 🎯 品質向上のポイント

### 1. データドリブンな裏付け
- 統計データによる客観的分析
- 定量的な根拠の明示
- 仮説検証のプロセス

### 2. AI活用による多角的検討
- 複数の視点での分析
- 想定外の洞察発見
- 創造的なアイデア発想

### 3. 実装可能性の担保
- 具体的なアクションプラン
- リソース・スケジュール検討
- リスク・制約の明確化

## 🚀 継続的改善

### 1. 定期実行
```powershell
# 月次実行スクリプト例
$monthlyDate = Get-Date -Format "yyyyMM01"
docker-compose exec persona-agent python agents/persona/workflows/setup-project.py --date $monthlyDate
docker-compose exec persona-agent python agents/persona/workflows/persona-analyzer.py --project $monthlyDate --sample
```

### 2. 結果比較
- 前回結果との比較分析
- トレンドの把握
- 改善効果の測定

### 3. 手法改善
- AI質問テンプレートの改善
- 分析観点の追加
- 成果物品質の向上

---

**🎯 このワークフローで、データドリブンかつAI支援によるマーケティング戦略を効率的に立案できます！** 