#!/usr/bin/env python3
"""
成果物・中間成果物管理ユーティリティ

AIエージェントの出力を体系的に管理し、テンプレート駆動での品質保証、
中間成果物の自動保存、成果物のバージョン管理を提供します。

使用例:
    from common.utils.output_manager import OutputManager
    
    manager = OutputManager("persona", "20241215")
    manager.save_intermediate("draft_analysis", content)
    manager.save_final_report("01_persona-analysis", content)
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
import logging

logger = logging.getLogger(__name__)

class OutputManager:
    """成果物・中間成果物管理クラス"""
    
    def __init__(self, agent_name: str, project_date: str):
        """
        OutputManager初期化
        
        Args:
            agent_name: エージェント名 (persona, product-planning等)
            project_date: プロジェクト日付 (YYYYMMDD形式)
        """
        self.agent_name = agent_name
        self.project_date = project_date
        self.project_id = f"{project_date}_{agent_name}"
        
        # パス設定
        self.base_path = Path("products") / agent_name
        self.templates_path = self.base_path / "templates"
        self.project_path = self.base_path / project_date
        
        # プロジェクト内ディレクトリ
        self.reports_path = self.project_path / "reports"
        self.temp_path = self.project_path / "temp"
        self.data_path = self.project_path / "data"
        self.assets_path = self.project_path / "assets"
        
        # ディレクトリ作成
        self._ensure_directories()
        
        logger.info(f"OutputManager初期化: {self.project_id}")

    def _ensure_directories(self) -> None:
        """必要なディレクトリを作成"""
        directories = [
            self.project_path,
            self.reports_path,
            self.temp_path,
            self.data_path,
            self.assets_path,
            self.assets_path / "charts",
            self.assets_path / "diagrams",
            self.assets_path / "presentation-files"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"ディレクトリ作成完了: {self.project_path}")

    def save_intermediate(self, filename: str, content: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        中間成果物を保存
        
        Args:
            filename: ファイル名（拡張子なし）
            content: 保存するコンテンツ
            metadata: メタデータ（オプション）
            
        Returns:
            保存されたファイルのパス
        """
        timestamp = datetime.now().strftime("%H%M%S")
        file_path = self.temp_path / f"{filename}_{timestamp}.md"
        
        # メタデータ付きでコンテンツを保存
        full_content = self._add_metadata_header(content, metadata, "intermediate")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logger.info(f"中間成果物保存: {file_path}")
        return file_path

    def save_final_report(self, template_name: str, content: str,
                         metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        最終成果物を保存
        
        Args:
            template_name: テンプレート名（01_persona-analysis等）
            content: 保存するコンテンツ
            metadata: メタデータ（オプション）
            
        Returns:
            保存されたファイルのパス
        """
        file_path = self.reports_path / f"{template_name}.md"
        
        # メタデータ付きでコンテンツを保存
        full_content = self._add_metadata_header(content, metadata, "final")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # バックアップ作成
        self._create_backup(file_path)
        
        logger.info(f"最終成果物保存: {file_path}")
        return file_path

    def save_data(self, filename: str, data: Union[Dict, List], 
                  format: str = "json") -> Path:
        """
        分析データを保存
        
        Args:
            filename: ファイル名（拡張子なし）
            data: 保存するデータ
            format: データ形式 (json, yaml)
            
        Returns:
            保存されたファイルのパス
        """
        if format == "json":
            file_path = self.data_path / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == "yaml":
            file_path = self.data_path / f"{filename}.yml"
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f"サポートされていない形式: {format}")
        
        logger.info(f"データ保存: {file_path}")
        return file_path

    def save_asset(self, filename: str, content: bytes, 
                   category: str = "charts") -> Path:
        """
        アセット（画像・ファイル）を保存
        
        Args:
            filename: ファイル名（拡張子含む）
            content: バイナリコンテンツ
            category: カテゴリ (charts, diagrams, presentation-files)
            
        Returns:
            保存されたファイルのパス
        """
        file_path = self.assets_path / category / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"アセット保存: {file_path}")
        return file_path

    def load_template(self, template_name: str) -> str:
        """
        テンプレートを読み込み
        
        Args:
            template_name: テンプレート名（01_persona-analysis等）
            
        Returns:
            テンプレートコンテンツ
        """
        template_path = self.templates_path / f"{template_name}.md"
        
        if not template_path.exists():
            raise FileNotFoundError(f"テンプレートが見つかりません: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"テンプレート読み込み: {template_path}")
        return content

    def get_project_status(self) -> Dict[str, Any]:
        """
        プロジェクトの進捗状況を取得
        
        Returns:
            進捗情報の辞書
        """
        status = {
            "project_id": self.project_id,
            "created_at": self._get_creation_time(),
            "last_updated": self._get_last_update_time(),
            "reports": self._scan_reports(),
            "intermediate_files": self._scan_intermediate_files(),
            "data_files": self._scan_data_files(),
            "assets": self._scan_assets(),
            "completion_rate": self._calculate_completion_rate()
        }
        
        return status

    def cleanup_intermediate(self, keep_latest: int = 3) -> List[Path]:
        """
        中間成果物のクリーンアップ
        
        Args:
            keep_latest: 保持する最新ファイル数
            
        Returns:
            削除されたファイルのリスト
        """
        intermediate_files = list(self.temp_path.glob("*.md"))
        intermediate_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        deleted_files = []
        for file_path in intermediate_files[keep_latest:]:
            file_path.unlink()
            deleted_files.append(file_path)
        
        logger.info(f"中間成果物クリーンアップ: {len(deleted_files)}個削除")
        return deleted_files

    def export_project(self, export_path: str, format: str = "zip") -> Path:
        """
        プロジェクト全体をエクスポート
        
        Args:
            export_path: エクスポート先パス
            format: エクスポート形式 (zip, tar)
            
        Returns:
            エクスポートファイルのパス
        """
        export_file = Path(export_path)
        
        if format == "zip":
            import zipfile
            with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in self.project_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.project_path)
                        zf.write(file_path, arcname)
        else:
            raise ValueError(f"サポートされていない形式: {format}")
        
        logger.info(f"プロジェクトエクスポート: {export_file}")
        return export_file

    def _add_metadata_header(self, content: str, metadata: Optional[Dict[str, Any]], 
                           output_type: str) -> str:
        """メタデータヘッダーを追加"""
        if metadata is None:
            metadata = {}
        
        # デフォルトメタデータ
        default_metadata = {
            "project_id": self.project_id,
            "agent_name": self.agent_name,
            "output_type": output_type,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # メタデータをマージ
        full_metadata = {**default_metadata, **metadata}
        
        # YAML Front Matterとして追加
        yaml_header = "---\n" + yaml.dump(full_metadata, allow_unicode=True) + "---\n\n"
        
        return yaml_header + content

    def _create_backup(self, file_path: Path) -> None:
        """ファイルのバックアップを作成"""
        if file_path.exists():
            backup_dir = file_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.copy2(file_path, backup_path)
            logger.debug(f"バックアップ作成: {backup_path}")

    def _get_creation_time(self) -> str:
        """プロジェクト作成時刻を取得"""
        if self.project_path.exists():
            return datetime.fromtimestamp(self.project_path.stat().st_ctime).isoformat()
        return datetime.now().isoformat()

    def _get_last_update_time(self) -> str:
        """最終更新時刻を取得"""
        latest_time = 0
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                latest_time = max(latest_time, file_path.stat().st_mtime)
        
        if latest_time > 0:
            return datetime.fromtimestamp(latest_time).isoformat()
        return datetime.now().isoformat()

    def _scan_reports(self) -> List[Dict[str, Any]]:
        """レポートファイルをスキャン"""
        reports = []
        for file_path in self.reports_path.glob("*.md"):
            reports.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        return reports

    def _scan_intermediate_files(self) -> List[Dict[str, Any]]:
        """中間ファイルをスキャン"""
        files = []
        for file_path in self.temp_path.glob("*.md"):
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        return files

    def _scan_data_files(self) -> List[Dict[str, Any]]:
        """データファイルをスキャン"""
        files = []
        for file_path in self.data_path.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        return files

    def _scan_assets(self) -> Dict[str, List[Dict[str, Any]]]:
        """アセットをスキャン"""
        assets = {}
        for category in ["charts", "diagrams", "presentation-files"]:
            category_path = self.assets_path / category
            if category_path.exists():
                files = []
                for file_path in category_path.glob("*"):
                    if file_path.is_file():
                        files.append({
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
                assets[category] = files
        return assets

    def _calculate_completion_rate(self) -> float:
        """完了率を計算"""
        expected_reports = [
            "01_persona-analysis.md",
            "02_planning-session.md", 
            "03_plan-evaluation.md",
            "04_final-proposal.md"
        ]
        
        completed = 0
        for report in expected_reports:
            if (self.reports_path / report).exists():
                completed += 1
        
        return (completed / len(expected_reports)) * 100

class ProjectManager:
    """複数プロジェクトの管理クラス"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.base_path = Path("products") / agent_name

    def list_projects(self) -> List[Dict[str, Any]]:
        """プロジェクト一覧を取得"""
        projects = []
        
        if not self.base_path.exists():
            return projects
        
        for project_dir in self.base_path.iterdir():
            if project_dir.is_dir() and project_dir.name != "templates":
                try:
                    manager = OutputManager(self.agent_name, project_dir.name)
                    status = manager.get_project_status()
                    projects.append(status)
                except Exception as e:
                    logger.warning(f"プロジェクト読み込みエラー {project_dir.name}: {e}")
        
        return sorted(projects, key=lambda x: x["created_at"], reverse=True)

    def create_project(self, project_date: str) -> OutputManager:
        """新しいプロジェクトを作成"""
        manager = OutputManager(self.agent_name, project_date)
        
        # プロジェクト情報ファイルを作成
        project_info = {
            "project_id": manager.project_id,
            "agent_name": self.agent_name,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        manager.save_data("project_info", project_info)
        
        logger.info(f"新規プロジェクト作成: {manager.project_id}")
        return manager

    def archive_project(self, project_date: str, archive_path: Optional[str] = None) -> Path:
        """プロジェクトをアーカイブ"""
        manager = OutputManager(self.agent_name, project_date)
        
        if archive_path is None:
            archive_path = f"archives/{manager.project_id}.zip"
        
        return manager.export_project(archive_path)

def get_output_manager(agent_name: str, project_date: Optional[str] = None) -> OutputManager:
    """OutputManagerのファクトリ関数"""
    if project_date is None:
        project_date = datetime.now().strftime("%Y%m%d")
    
    return OutputManager(agent_name, project_date) 