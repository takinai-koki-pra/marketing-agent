#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プロジェクトセットアップツール
新しいプロジェクトディレクトリを作成し、テンプレートをコピーします。

使用方法:
    python setup-project.py --date 20250703 --prefix persona
    python setup-project.py --date 20250704 --prefix marketing --title "マーケティング企画プロジェクト"
"""

import os
import sys
import shutil
import argparse
import json
from datetime import datetime
from pathlib import Path

# プロジェクトルートの設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = OUTPUT_DIR / "templates"

def create_project_directory(date_str, prefix):
    """プロジェクトディレクトリを作成"""
    project_name = f"{date_str}_{prefix}"
    project_dir = OUTPUT_DIR / project_name
    
    if project_dir.exists():
        print(f"⚠️  プロジェクトディレクトリが既に存在します: {project_dir}")
        response = input("上書きしますか？ (y/N): ")
        if response.lower() != 'y':
            print("❌ 処理を中止しました")
            return None
        shutil.rmtree(project_dir)
    
    # ディレクトリ構造を作成
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "data").mkdir(exist_ok=True)
    (project_dir / "visualizations").mkdir(exist_ok=True)
    (project_dir / "presentation-files").mkdir(exist_ok=True)
    (project_dir / "presentation-files" / "assets").mkdir(exist_ok=True)
    
    print(f"✅ プロジェクトディレクトリを作成しました: {project_dir}")
    return project_dir

def copy_templates(project_dir, project_info):
    """テンプレートファイルをコピー"""
    if not TEMPLATES_DIR.exists():
        print(f"❌ テンプレートディレクトリが見つかりません: {TEMPLATES_DIR}")
        return False
    
    template_files = [
        "01_persona-analysis.md",
        "02_planning-session.md", 
        "03_plan-evaluation.md",
        "04_final-proposal.md",
        "05_completion-report.md",
        "06_presentation.md"
    ]
    
    copied_files = []
    
    for template_file in template_files:
        src_file = TEMPLATES_DIR / template_file
        dst_file = project_dir / template_file
        
        if src_file.exists():
            try:
                shutil.copy2(src_file, dst_file)
                copied_files.append(template_file)
                print(f"📄 コピー完了: {template_file}")
            except Exception as e:
                print(f"❌ コピー失敗: {template_file} - {e}")
        else:
            print(f"⚠️  テンプレートファイルが見つかりません: {template_file}")
    
    # プロジェクト情報ファイルを作成
    project_info_file = project_dir / "project-info.json"
    try:
        with open(project_info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        print(f"📄 プロジェクト情報ファイルを作成: project-info.json")
    except Exception as e:
        print(f"❌ プロジェクト情報ファイル作成失敗: {e}")
    
    return len(copied_files) > 0

def create_readme(project_dir, project_info):
    """プロジェクト用READMEを作成"""
    readme_content = f"""# {project_info['title']}

## 📊 プロジェクト情報
- **プロジェクト名**: {project_info['title']}
- **作成日**: {project_info['date']}
- **接頭辞**: {project_info['prefix']}
- **プロジェクトID**: {project_info['project_id']}

## 📁 ディレクトリ構造
```
{project_info['project_id']}/
├── 01_persona-analysis.md      # ペルソナ分析レポート
├── 02_planning-session.md      # 企画検討セッション記録
├── 03_plan-evaluation.md       # 企画評価・改善提案
├── 04_final-proposal.md        # 最終企画書
├── 05_completion-report.md     # プロジェクト完了レポート
├── 06_presentation.md          # プレゼンテーション資料（MARP用）
├── data/                       # 分析データ・統計情報
├── visualizations/             # グラフ・チャート画像
├── presentation-files/         # プレゼンテーション関連
│   └── assets/                # 画像・素材
├── project-info.json          # プロジェクト情報
└── README.md                   # このファイル
```

## 🔄 ワークフロー

### 1. ペルソナ分析実行
```powershell
python workflows/persona-analyzer.py --project {project_info['project_id']}
```

### 2. 企画検討セッション実行
```powershell
python workflows/planning-session.py --project {project_info['project_id']}
```

### 3. 企画評価実行
```powershell
python workflows/plan-evaluation.py --project {project_info['project_id']}
```

### 4. 進捗確認
```powershell
python workflows/check-progress.py --project {project_info['project_id']}
```

## ✅ 完了チェックリスト

### Phase 1: ペルソナ分析
- [ ] データ収集完了
- [ ] ペルソナプロファイル作成完了
- [ ] 統計分析完了
- [ ] 可視化資料作成完了
- [ ] `01_persona-analysis.md` 完成

### Phase 2: 企画検討
- [ ] セッション実施完了
- [ ] 各ペルソナ視点での検討完了
- [ ] 企画案収束完了
- [ ] `02_planning-session.md` 完成

### Phase 3: 企画評価
- [ ] 定量評価完了
- [ ] 定性評価完了
- [ ] 改善提案作成完了
- [ ] `03_plan-evaluation.md` 完成

### Phase 4: 最終企画書
- [ ] 企画書作成完了
- [ ] 財務計画作成完了
- [ ] 実行計画作成完了
- [ ] `04_final-proposal.md` 完成

### Phase 5: プレゼンテーション
- [ ] MARP資料作成完了
- [ ] プレゼンテーション実施完了
- [ ] `06_presentation.md` 完成

### Phase 6: プロジェクト完了
- [ ] 完了レポート作成完了
- [ ] アーカイブ整理完了
- [ ] `05_completion-report.md` 完成

## 📊 品質基準

### 必須要件
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

*このプロジェクトは {project_info['created_at']} に作成されました*
*最終更新: {project_info['created_at']}*
"""
    
    readme_file = project_dir / "README.md"
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"📄 README.mdを作成しました")
        return True
    except Exception as e:
        print(f"❌ README.md作成失敗: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='新しいプロジェクトを作成し、テンプレートをコピーします')
    parser.add_argument('--date', required=True, help='プロジェクト日付 (YYYYMMDD形式)')
    parser.add_argument('--prefix', required=True, help='プロジェクト接頭辞')
    parser.add_argument('--title', help='プロジェクトタイトル')
    parser.add_argument('--description', help='プロジェクト説明')
    
    args = parser.parse_args()
    
    # 日付形式の検証
    try:
        datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        print("❌ 日付は YYYYMMDD 形式で入力してください")
        sys.exit(1)
    
    # プロジェクト情報の準備
    project_id = f"{args.date}_{args.prefix}"
    project_info = {
        'project_id': project_id,
        'date': args.date,
        'prefix': args.prefix,
        'title': args.title or f"{args.prefix.title()}プロジェクト",
        'description': args.description or f"{args.date}に作成された{args.prefix}プロジェクト",
        'created_at': datetime.now().isoformat(),
        'status': 'created',
        'phase': 'Phase 1: ペルソナ分析',
        'completion_rate': 0
    }
    
    print(f"🚀 プロジェクトセットアップを開始します")
    print(f"   プロジェクトID: {project_id}")
    print(f"   タイトル: {project_info['title']}")
    
    # プロジェクトディレクトリ作成
    project_dir = create_project_directory(args.date, args.prefix)
    if not project_dir:
        sys.exit(1)
    
    # テンプレートコピー
    if not copy_templates(project_dir, project_info):
        print("❌ テンプレートのコピーに失敗しました")
        sys.exit(1)
    
    # README作成
    create_readme(project_dir, project_info)
    
    print(f"\n✅ プロジェクトセットアップが完了しました！")
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    print(f"\n🔄 次のステップ:")
    print(f"   1. cd {project_dir}")
    print(f"   2. python ../workflows/persona-analyzer.py --project {project_id}")
    print(f"   3. 各mdファイルのTODOマーカーを実際の内容に置換")

if __name__ == "__main__":
    main() 