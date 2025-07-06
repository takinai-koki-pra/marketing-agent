#!/usr/bin/env python3
"""
ペルソナベースAIエージェント - 進捗確認・品質チェックツール

このスクリプトは、プロジェクトの進捗状況と品質を自動的にチェックします。
- TODOマーカーの残存チェック
- 完了率の算出・表示
- 品質基準の自動チェック
- 進捗レポートの出力

使用方法:
    python check-progress.py                          # 全プロジェクトの進捗確認
    python check-progress.py --project 20250703       # 特定プロジェクトの進捗確認
    python check-progress.py --summary                # サマリー表示のみ
"""

import os
import sys
import argparse
import datetime
import json
import re
from pathlib import Path
from collections import defaultdict
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('check-progress.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# TODO/DONEマーカーパターン
TODO_PATTERNS = [
    r'\[\s*\]\s*TODO:',  # [ ] TODO:
    r'\[\s*\]\s*FIXME:',  # [ ] FIXME:
    r'\[\s*\]\s*XXX:',    # [ ] XXX:
    r'\[\s*\]\s*HACK:',   # [ ] HACK:
]

DONE_PATTERNS = [
    r'\[x\]\s*DONE:',     # [x] DONE:
    r'\[x\]\s*TODO:',     # [x] TODO: (完了済み)
    r'\[x\]\s*FIXME:',    # [x] FIXME: (完了済み)
    r'\[x\]\s*XXX:',      # [x] XXX: (完了済み)
    r'\[x\]\s*HACK:',     # [x] HACK: (完了済み)
]

class ProgressChecker:
    """プロジェクト進捗チェッククラス"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.project_name = project_dir.name
        self.results = {
            'project_name': self.project_name,
            'total_files': 0,
            'todo_count': 0,
            'done_count': 0,
            'completion_rate': 0.0,
            'files_analysis': {},
            'quality_issues': [],
            'recommendations': []
        }
    
    def scan_markdown_files(self):
        """MarkdownファイルをスキャンしてTODO/DONEマーカーを検出"""
        md_files = list(self.project_dir.glob('*.md'))
        self.results['total_files'] = len(md_files)
        
        for md_file in md_files:
            file_analysis = self._analyze_file(md_file)
            self.results['files_analysis'][md_file.name] = file_analysis
            self.results['todo_count'] += file_analysis['todo_count']
            self.results['done_count'] += file_analysis['done_count']
    
    def _analyze_file(self, file_path: Path) -> dict:
        """個別ファイルの分析"""
        analysis = {
            'todo_count': 0,
            'done_count': 0,
            'todo_items': [],
            'done_items': [],
            'quality_issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # TODOマーカーチェック
                    for pattern in TODO_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            analysis['todo_count'] += 1
                            analysis['todo_items'].append({
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'TODO'
                            })
                    
                    # DONEマーカーチェック
                    for pattern in DONE_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            analysis['done_count'] += 1
                            analysis['done_items'].append({
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'DONE'
                            })
                
                # 品質チェック
                analysis['quality_issues'] = self._check_quality(content, file_path.name)
                
        except Exception as e:
            logger.warning(f"ファイル読み込みエラー: {file_path}: {e}")
            analysis['quality_issues'].append(f"ファイル読み込みエラー: {e}")
        
        return analysis
    
    def _check_quality(self, content: str, filename: str) -> list:
        """品質チェック"""
        issues = []
        
        # 基本的な品質チェック
        if len(content.strip()) < 100:
            issues.append("ファイル内容が短すぎます（100文字未満）")
        
        if '[企画名を入力]' in content:
            issues.append("プロジェクト名が設定されていません")
        
        # ファイル別の特定チェック
        if filename == '01_persona-analysis.md':
            if 'ペルソナ1' not in content or 'ペルソナ2' not in content:
                issues.append("ペルソナが設定されていません")
        
        elif filename == '04_final-proposal.md':
            if 'ROI予測' in content and 'TODO' in content:
                issues.append("ROI予測が未完了です")
        
        return issues
    
    def calculate_completion_rate(self):
        """完了率を計算"""
        total_tasks = self.results['todo_count'] + self.results['done_count']
        if total_tasks > 0:
            self.results['completion_rate'] = (self.results['done_count'] / total_tasks) * 100
        else:
            self.results['completion_rate'] = 0.0
    
    def generate_recommendations(self):
        """改善提案を生成"""
        recommendations = []
        
        # 完了率に基づく提案
        completion_rate = self.results['completion_rate']
        if completion_rate < 25:
            recommendations.append("🔴 プロジェクト開始段階です。01_persona-analysis.mdから開始してください")
        elif completion_rate < 50:
            recommendations.append("🟡 分析段階です。ペルソナ分析を完了させましょう")
        elif completion_rate < 75:
            recommendations.append("🟡 企画検討段階です。02_planning-session.mdを進めましょう")
        elif completion_rate < 90:
            recommendations.append("🟢 仕上げ段階です。最終企画書を完成させましょう")
        else:
            recommendations.append("🎉 プロジェクト完了間近です！最終チェックを行いましょう")
        
        # ファイル別の提案
        for filename, analysis in self.results['files_analysis'].items():
            if analysis['todo_count'] > 0:
                recommendations.append(f"📝 {filename}: {analysis['todo_count']}個のTODOが残存")
        
        # 品質問題に基づく提案
        total_quality_issues = sum(len(analysis['quality_issues']) 
                                 for analysis in self.results['files_analysis'].values())
        if total_quality_issues > 0:
            recommendations.append(f"⚠️  品質問題が{total_quality_issues}件検出されました")
        
        self.results['recommendations'] = recommendations
    
    def run_analysis(self):
        """分析を実行"""
        logger.info(f"プロジェクト分析開始: {self.project_name}")
        
        self.scan_markdown_files()
        self.calculate_completion_rate()
        self.generate_recommendations()
        
        # 品質問題の集約
        for analysis in self.results['files_analysis'].values():
            self.results['quality_issues'].extend(analysis['quality_issues'])
        
        logger.info(f"プロジェクト分析完了: {self.project_name}")
        return self.results

def print_progress_report(results: dict):
    """進捗レポートを表示"""
    print(f"\n" + "="*60)
    print(f"📊 プロジェクト進捗レポート: {results['project_name']}")
    print(f"="*60)
    
    # 基本統計
    print(f"\n📈 基本統計:")
    print(f"  - 対象ファイル数: {results['total_files']}")
    print(f"  - 未完了タスク: {results['todo_count']}")
    print(f"  - 完了タスク: {results['done_count']}")
    print(f"  - 完了率: {results['completion_rate']:.1f}%")
    
    # 進捗バー
    progress_bar_length = 40
    completed_length = int(progress_bar_length * results['completion_rate'] / 100)
    progress_bar = "█" * completed_length + "░" * (progress_bar_length - completed_length)
    print(f"  - 進捗: [{progress_bar}] {results['completion_rate']:.1f}%")
    
    # ファイル別詳細
    if results['files_analysis']:
        print(f"\n📋 ファイル別詳細:")
        for filename, analysis in results['files_analysis'].items():
            status = "🟢" if analysis['todo_count'] == 0 else "🔴"
            print(f"  {status} {filename}: TODO={analysis['todo_count']}, DONE={analysis['done_count']}")
    
    # 品質問題
    if results['quality_issues']:
        print(f"\n⚠️  品質問題:")
        for issue in results['quality_issues'][:5]:  # 最大5件表示
            print(f"  - {issue}")
        if len(results['quality_issues']) > 5:
            print(f"  - ... 他{len(results['quality_issues'])-5}件")
    
    # 推奨アクション
    if results['recommendations']:
        print(f"\n💡 推奨アクション:")
        for rec in results['recommendations']:
            print(f"  {rec}")
    
    print(f"\n" + "="*60)

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='ペルソナベースAIエージェント 進捗確認・品質チェックツール'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='特定プロジェクトの進捗確認 (YYYYMMDD形式)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='サマリー表示のみ'
    )
    
    args = parser.parse_args()
    
    if not OUTPUTS_DIR.exists():
        logger.error("outputsディレクトリが存在しません。")
        sys.exit(1)
    
    # プロジェクト一覧取得
    projects = [d for d in OUTPUTS_DIR.iterdir() 
               if d.is_dir() and d.name.isdigit() and len(d.name) == 8]
    
    if not projects:
        print("プロジェクトが見つかりません。")
        return
    
    # 特定プロジェクトのチェック
    if args.project:
        project_dir = OUTPUTS_DIR / args.project
        if not project_dir.exists():
            logger.error(f"プロジェクト {args.project} が見つかりません。")
            sys.exit(1)
        
        checker = ProgressChecker(project_dir)
        results = checker.run_analysis()
        print_progress_report(results)
        return
    
    # 全プロジェクトのチェック
    if args.summary:
        print(f"\n📊 プロジェクト一覧 (全{len(projects)}件)")
        print("-" * 50)
        for project_dir in sorted(projects):
            checker = ProgressChecker(project_dir)
            results = checker.run_analysis()
            status = "🟢" if results['completion_rate'] >= 90 else "🔴"
            print(f"{status} {project_dir.name}: {results['completion_rate']:.1f}% "
                  f"(TODO: {results['todo_count']}, DONE: {results['done_count']})")
    else:
        # 最新プロジェクトの詳細チェック
        latest_project = max(projects, key=lambda x: x.name)
        checker = ProgressChecker(latest_project)
        results = checker.run_analysis()
        print_progress_report(results)

if __name__ == "__main__":
    main() 