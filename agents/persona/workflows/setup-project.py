#!/usr/bin/env python3
"""
ペルソナベースAIエージェント - プロジェクト自動セットアップツール

このスクリプトは、新しい企画案生成プロジェクトを自動的にセットアップします。
- 日付別プロジェクトディレクトリの作成
- テンプレートファイルの配置
- 必要なディレクトリ構造の生成
- 初期データファイルの作成

使用方法:
    python setup-project.py                    # 今日の日付でプロジェクト作成
    python setup-project.py --date 20240125    # 指定日付でプロジェクト作成
    python setup-project.py --help             # ヘルプ表示
"""

import os
import sys
import argparse
import datetime
import json
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup-project.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TEMPLATES_DIR = OUTPUTS_DIR / "templates"

def create_directory_structure(project_dir: Path):
    """プロジェクトディレクトリ構造を作成"""
    directories = [
        project_dir,
        project_dir / "presentation-files",
        project_dir / "presentation-files" / "assets",
        project_dir / "research-data"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ディレクトリ作成: {dir_path}")

def create_template_files(project_dir: Path, date_str: str):
    """テンプレートファイルを作成"""
    template_content = f"""# ペルソナ分析レポート

**プロジェクト名:** [企画名を入力]
**分析日時:** {date_str}
**分析者:** AI Agent

---

## 📊 分析概要

### 分析目的
- [ ] TODO: 分析の目的・背景を記載

### 対象データ
- [ ] TODO: 分析対象のリサーチデータを記載

---

## 👥 ペルソナ分析結果

### ペルソナ1: [名前]
- **基本属性:**
  - [ ] TODO: 年齢、性別、職業等
- **心理属性:**
  - [ ] TODO: 価値観、ライフスタイル等
- **行動パターン:**
  - [ ] TODO: 購買行動、情報収集方法等

---

**次のステップ:** 02_planning-session.md での企画検討セッション
"""
    
    # 01_persona-analysis.md作成
    file_path = project_dir / "01_persona-analysis.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    logger.info(f"テンプレートファイル作成: {file_path}")

def create_data_files(project_dir: Path, date_str: str):
    """初期データファイルを作成"""
    # ペルソナデータJSONファイル
    persona_data = {
        "project_info": {
            "project_name": "未設定",
            "creation_date": date_str,
            "status": "初期化完了"
        },
        "personas": [],
        "analysis_results": {},
        "metadata": {
            "version": "1.0",
            "created_by": "setup-project.py"
        }
    }
    
    persona_file = project_dir / f"persona-data-{date_str}.json"
    with open(persona_file, 'w', encoding='utf-8') as f:
        json.dump(persona_data, f, ensure_ascii=False, indent=2)
    logger.info(f"ペルソナデータファイル作成: {persona_file}")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='ペルソナベースAIエージェント プロジェクト自動セットアップツール'
    )
    
    parser.add_argument(
        '--date', 
        type=str, 
        help='プロジェクト日付 (YYYYMMDD形式)'
    )
    
    args = parser.parse_args()
    
    # 日付設定
    if args.date:
        try:
            datetime.datetime.strptime(args.date, '%Y%m%d')
            date_str = args.date
        except ValueError:
            logger.error("日付形式が不正です。YYYYMMDD形式で入力してください。")
            sys.exit(1)
    else:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
    
    # プロジェクトディレクトリパス
    project_dir = OUTPUTS_DIR / date_str
    
    try:
        logger.info(f"プロジェクトセットアップ開始: {date_str}")
        
        # ディレクトリ構造作成
        create_directory_structure(project_dir)
        
        # テンプレートファイル作成
        create_template_files(project_dir, date_str)
        
        # データファイル作成
        create_data_files(project_dir, date_str)
        
        logger.info(f"プロジェクトセットアップ完了: {project_dir}")
        print(f"\n✅ プロジェクト '{date_str}' のセットアップが完了しました！")
        print(f"📁 プロジェクトディレクトリ: {project_dir}")
        
    except Exception as e:
        logger.error(f"プロジェクトセットアップ中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 