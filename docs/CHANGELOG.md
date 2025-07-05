# 変更履歴 (CHANGELOG)

## [1.0.0] - 2025-07-03

### 🏗️ ディレクトリ構成大幅改善
#### Added
- 新しいディレクトリ構成の導入
  - `agents/` - エージェント実装の分離
  - `common/` - 共通リソースの統合
  - `products/` - 成果物の体系的管理
  - `docs/` - ドキュメントの集約
- `agents/persona/config.yml` - 自然言語プロンプト設定システム
- `docs/ARCHITECTURE.md` - アーキテクチャ設計書
- `docs/CHANGELOG.md` - 変更履歴管理

#### Changed
- ナレッジベースの統合
  - `003_marketing_tools/knowledge/` → `common/knowledge/industry/`
  - `004_persona_agent/knowledge/` → `common/knowledge/templates/`
- 成果物管理の改善
  - 日付別フォルダ構成 (`products/persona/YYYYMMDD/`)
  - 最終成果物・中間成果物・アセットの分離
- プロンプト管理の効率化
  - YAML形式での自然言語設定
  - エージェント固有 vs 共通プロンプトの分離

#### Removed
- `003_marketing_tools/` - 古いマーケティングツールフォルダ
- `004_persona_agent/` - 新構成への移行完了後削除
- `workflows/` - `common/scripts/` へ統合
- `output/` - `products/` へ統合

#### Fixed
- Windows PowerShell対応の強化
- パス設定の統一化
- ファイル移行時の重複問題解決

### 🎯 機能改善
#### Enhanced
- プロンプトチューニングの自然言語化
- ナレッジベース検索の効率化準備
- エージェント拡張性の向上
- 成果物バージョン管理の改善

---

## [0.9.0] - 2025-07-02 (移行前の最終版)

### 🎯 ペルソナベースAIエージェント完成
#### Added
- ペルソナ分析機能 (Phase 5)
- 企画検討・評価機能 (Phase 6)
- MARP プレゼンテーション生成基盤
- e-Stat API連携機能
- 統計データ可視化機能

#### Completed
- Phase 1: 基盤構築・環境セットアップ
- Phase 2: 自動化ツール群実装
- Phase 3: プロンプトテンプレート作成
- Phase 4: ナレッジベース構築
- Phase 5: データ分析・ペルソナ生成機能
- Phase 6: 企画検討・評価機能

---

## [0.8.0] - 2025-06-24

### 🚀 マーケティングツール完成
#### Added
- 競合分析エンジン
- SEO分析機能
- マーケティング戦略立案
- LP要件定義・制作機能
- SerpAPI連携

#### Completed
- 003_marketing_tools 全機能実装
- 実用レベルのLP制作完了
- 即座に公開可能な品質達成

---

## [今後の予定]

### [1.1.0] - 計画中
#### Planned
- Phase 8: プレゼンテーション生成機能完成
- MARP テンプレート新構成対応
- PowerPoint・HTML出力対応

### [1.2.0] - 計画中
#### Planned
- Phase 9: 新エージェント追加
- マーケティングエージェント復活
- 製品企画エージェント新規開発
- 事業企画エージェント新規開発

### [2.0.0] - 計画中
#### Planned
- Vector DB統合
- マルチエージェント連携
- API統合基盤
- 大量データ処理対応

---

## 🔍 移行ガイド

### v0.9.0 → v1.0.0 移行手順
1. **バックアップ作成**: 既存の `004_persona_agent/outputs/` をバックアップ
2. **新構成確認**: `docs/ARCHITECTURE.md` で新しい構成を確認
3. **パス更新**: 既存スクリプトのパス設定を新構成に合わせて更新
4. **設定移行**: `agents/persona/config.yml` でプロンプト設定を確認・調整
5. **動作確認**: `common/scripts/setup-project.py` で環境確認

### 互換性情報
- **API**: 既存のワークフロー呼び出しは要パス修正
- **データ**: 成果物は自動移行済み、パス変更のみ
- **設定**: プロンプト設定は新形式への手動移行推奨

### 注意事項
- Windows PowerShell環境での動作を前提
- `&&` 演算子は使用不可（`;` または個別実行）
- パス区切り文字は `\` を使用 