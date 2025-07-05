#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テンプレート更新ツール
既存プロジェクトのテンプレートを最新版に更新します。

使用方法:
    python update-templates.py --project 20250703_persona
    python update-templates.py --project 20250703_persona --backup
    python update-templates.py --all --backup
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

def find_projects():
    """既存プロジェクトを検索"""
    if not OUTPUT_DIR.exists():
        return []
    
    projects = []
    for item in OUTPUT_DIR.iterdir():
        if item.is_dir() and item.name != "templates":
            # YYYYMMDD_prefix 形式のチェック
            parts = item.name.split('_')
            if len(parts) >= 2 and len(parts[0]) == 8 and parts[0].isdigit():
                projects.append(item.name)
    
    return sorted(projects)

def backup_project(project_dir):
    """プロジェクトのバックアップを作成"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{project_dir.name}_backup_{timestamp}"
    backup_dir = project_dir.parent / backup_name
    
    try:
        shutil.copytree(project_dir, backup_dir)
        print(f"📦 バックアップを作成しました: {backup_name}")
        return backup_dir
    except Exception as e:
        print(f"❌ バックアップ作成失敗: {e}")
        return None

def get_todo_markers(file_path):
    """ファイルからTODOマーカーを抽出"""
    if not file_path.exists():
        return set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        todo_pattern = r'<!-- TODO_([A-Z0-9_]+) -->'
        markers = set(re.findall(todo_pattern, content))
        return markers
    except Exception as e:
        print(f"⚠️  TODOマーカー抽出エラー: {file_path.name} - {e}")
        return set()

def preserve_content(old_file, new_file, output_file):
    """既存の内容を保持しながらテンプレートを更新"""
    if not old_file.exists():
        # 既存ファイルがない場合は新しいテンプレートをそのままコピー
        shutil.copy2(new_file, output_file)
        return True, "新規作成"
    
    if not new_file.exists():
        print(f"⚠️  新しいテンプレートが見つかりません: {new_file.name}")
        return False, "テンプレートなし"
    
    try:
        # 既存ファイルの内容を読み込み
        with open(old_file, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        # 新しいテンプレートを読み込み
        with open(new_file, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        # TODOマーカーの置換マップを作成
        import re
        todo_pattern = r'<!-- TODO_([A-Z0-9_]+) -->'
        
        # 既存ファイルから置換済みの内容を抽出
        old_replacements = {}
        for match in re.finditer(todo_pattern, old_content):
            marker = match.group(0)
            marker_name = match.group(1)
            
            # マーカーの前後の文脈を使って実際の内容を特定
            start_pos = match.end()
            
            # 次のマーカーまたは特定のパターンまでを内容とする
            next_marker = re.search(todo_pattern, old_content[start_pos:])
            if next_marker:
                end_pos = start_pos + next_marker.start()
                actual_content = old_content[start_pos:end_pos].strip()
            else:
                # ファイル末尾まで、または特定のパターンまで
                section_end = re.search(r'\n\n##|\n---|\Z', old_content[start_pos:])
                if section_end:
                    end_pos = start_pos + section_end.start()
                    actual_content = old_content[start_pos:end_pos].strip()
                else:
                    actual_content = old_content[start_pos:].strip()
            
            # マーカーが実際の内容に置換されているかチェック
            if actual_content and not actual_content.startswith('<!-- TODO_'):
                old_replacements[marker] = actual_content
        
        # 新しいテンプレートに既存の内容を適用
        updated_content = new_content
        replacement_count = 0
        
        for marker, content in old_replacements.items():
            if marker in updated_content:
                updated_content = updated_content.replace(marker, content)
                replacement_count += 1
        
        # 更新されたファイルを書き込み
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, f"{replacement_count}項目を保持"
        
    except Exception as e:
        print(f"❌ ファイル更新エラー: {old_file.name} - {e}")
        return False, f"エラー: {e}"

def update_project_templates(project_name, create_backup=False):
    """プロジェクトのテンプレートを更新"""
    project_dir = OUTPUT_DIR / project_name
    
    if not project_dir.exists():
        print(f"❌ プロジェクトが見つかりません: {project_name}")
        return False
    
    print(f"\n🔄 プロジェクト更新開始: {project_name}")
    
    # バックアップ作成
    if create_backup:
        backup_dir = backup_project(project_dir)
        if not backup_dir:
            return False
    
    # テンプレートファイルリスト
    template_files = [
        "01_persona-analysis.md",
        "02_planning-session.md",
        "03_plan-evaluation.md", 
        "04_final-proposal.md",
        "05_completion-report.md",
        "06_presentation.md"
    ]
    
    update_results = {}
    
    for template_file in template_files:
        old_file = project_dir / template_file
        new_template = TEMPLATES_DIR / template_file
        
        success, message = preserve_content(old_file, new_template, old_file)
        update_results[template_file] = (success, message)
        
        if success:
            print(f"✅ {template_file}: {message}")
        else:
            print(f"❌ {template_file}: {message}")
    
    # プロジェクト情報を更新
    project_info_file = project_dir / "project-info.json"
    if project_info_file.exists():
        try:
            with open(project_info_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
            
            project_info['last_template_update'] = datetime.now().isoformat()
            project_info['template_version'] = datetime.now().strftime("%Y%m%d")
            
            with open(project_info_file, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, ensure_ascii=False, indent=2)
            
            print(f"📄 プロジェクト情報を更新しました")
        except Exception as e:
            print(f"⚠️  プロジェクト情報更新エラー: {e}")
    
    # 結果サマリー
    success_count = sum(1 for success, _ in update_results.values() if success)
    total_count = len(update_results)
    
    print(f"\n📊 更新結果: {success_count}/{total_count} ファイル成功")
    
    return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description='既存プロジェクトのテンプレートを更新します')
    parser.add_argument('--project', help='更新するプロジェクト名 (例: 20250703_persona)')
    parser.add_argument('--all', action='store_true', help='全プロジェクトを更新')
    parser.add_argument('--backup', action='store_true', help='更新前にバックアップを作成')
    parser.add_argument('--list', action='store_true', help='既存プロジェクト一覧を表示')
    
    args = parser.parse_args()
    
    # テンプレートディレクトリの存在確認
    if not TEMPLATES_DIR.exists():
        print(f"❌ テンプレートディレクトリが見つかりません: {TEMPLATES_DIR}")
        sys.exit(1)
    
    # 既存プロジェクトの検索
    projects = find_projects()
    
    if args.list:
        print("📋 既存プロジェクト一覧:")
        if not projects:
            print("   プロジェクトが見つかりませんでした")
        else:
            for project in projects:
                project_dir = OUTPUT_DIR / project
                project_info_file = project_dir / "project-info.json"
                
                if project_info_file.exists():
                    try:
                        with open(project_info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                        title = info.get('title', project)
                        status = info.get('status', 'unknown')
                        print(f"   - {project}: {title} ({status})")
                    except:
                        print(f"   - {project}: (情報読み込みエラー)")
                else:
                    print(f"   - {project}: (プロジェクト情報なし)")
        return
    
    if not args.project and not args.all:
        print("❌ --project または --all オプションを指定してください")
        print("   使用例: python update-templates.py --project 20250703_persona")
        print("   使用例: python update-templates.py --all --backup")
        sys.exit(1)
    
    if not projects:
        print("❌ 更新対象のプロジェクトが見つかりませんでした")
        sys.exit(1)
    
    # 更新対象の決定
    if args.all:
        target_projects = projects
        print(f"🎯 全プロジェクト ({len(projects)}件) を更新します")
    else:
        if args.project not in projects:
            print(f"❌ プロジェクトが見つかりません: {args.project}")
            print(f"利用可能なプロジェクト: {', '.join(projects)}")
            sys.exit(1)
        target_projects = [args.project]
        print(f"🎯 プロジェクト '{args.project}' を更新します")
    
    if args.backup:
        print("📦 バックアップを作成します")
    
    # 確認
    if len(target_projects) > 1:
        response = input(f"{len(target_projects)}件のプロジェクトを更新します。続行しますか？ (y/N): ")
        if response.lower() != 'y':
            print("❌ 処理を中止しました")
            sys.exit(0)
    
    # 更新実行
    success_count = 0
    for project in target_projects:
        if update_project_templates(project, args.backup):
            success_count += 1
    
    print(f"\n🎉 更新完了: {success_count}/{len(target_projects)} プロジェクト成功")
    
    if success_count < len(target_projects):
        sys.exit(1)

if __name__ == "__main__":
    main() 