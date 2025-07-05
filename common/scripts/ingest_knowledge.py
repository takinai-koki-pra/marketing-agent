#!/usr/bin/env python3
"""
ナレッジベース取り込み・インデックス化スクリプト

企業独自のナレッジデータを処理し、AIエージェントが効率的に検索できる形に変換します。
Vector DB統合、メタデータ抽出、検索インデックス作成を自動化。

使用例:
    python ingest_knowledge.py --update-all
    python ingest_knowledge.py --category customer-support --force
    python ingest_knowledge.py --file path/to/document.md
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import hashlib
import re

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('common/logs/ingest_knowledge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KnowledgeIngestor:
    """ナレッジベース取り込み・処理クラス"""
    
    def __init__(self, config_path: str = "common/config/knowledge_config.yml"):
        self.config = self._load_config(config_path)
        self.knowledge_base_path = Path("common/knowledge")
        self.index_path = Path("common/knowledge/.index")
        self.index_path.mkdir(exist_ok=True)
        
        # Vector DB設定（環境変数から取得）
        self.vector_db_type = os.getenv("VECTOR_DB_TYPE", "chroma")  # chroma, pinecone, weaviate
        self.vector_db_url = os.getenv("VECTOR_DB_URL", "")
        self.vector_db_key = os.getenv("VECTOR_DB_API_KEY", "")
        
        # 埋め込みモデル設定
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        logger.info(f"KnowledgeIngestor初期化完了 - Vector DB: {self.vector_db_type}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"設定ファイルが見つかりません: {config_path}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "supported_formats": [".md", ".txt", ".json", ".yml", ".yaml"],
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "metadata_fields": [
                "date", "category", "tags", "priority", "status",
                "industry", "customer_segment", "product_name"
            ],
            "exclude_patterns": [
                "*.tmp", "*.log", ".*", "__pycache__",
                "node_modules", ".git"
            ]
        }

    def scan_knowledge_base(self, category: Optional[str] = None) -> List[Path]:
        """ナレッジベースのファイルスキャン"""
        logger.info("ナレッジベースのスキャンを開始")
        
        if category:
            scan_path = self.knowledge_base_path / category
            if not scan_path.exists():
                logger.error(f"カテゴリが見つかりません: {category}")
                return []
        else:
            scan_path = self.knowledge_base_path
        
        files = []
        supported_formats = self.config["supported_formats"]
        exclude_patterns = self.config["exclude_patterns"]
        
        for file_path in scan_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in supported_formats:
                # 除外パターンチェック
                if not any(file_path.match(pattern) for pattern in exclude_patterns):
                    files.append(file_path)
        
        logger.info(f"スキャン完了: {len(files)}個のファイルを発見")
        return files

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """ファイルからメタデータを抽出"""
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "category": self._extract_category_from_path(file_path),
            "file_hash": self._calculate_file_hash(file_path)
        }
        
        # ファイル内容からYAML Front Matterを抽出
        try:
            content = file_path.read_text(encoding='utf-8')
            yaml_metadata = self._extract_yaml_frontmatter(content)
            metadata.update(yaml_metadata)
        except Exception as e:
            logger.warning(f"メタデータ抽出エラー {file_path}: {e}")
        
        return metadata

    def _extract_category_from_path(self, file_path: Path) -> str:
        """ファイルパスからカテゴリを抽出"""
        relative_path = file_path.relative_to(self.knowledge_base_path)
        return str(relative_path.parent).replace(os.sep, "/")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """ファイルのハッシュ値を計算"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _extract_yaml_frontmatter(self, content: str) -> Dict[str, Any]:
        """YAML Front Matterを抽出"""
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError as e:
                logger.warning(f"YAML解析エラー: {e}")
        
        return {}

    def chunk_content(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """コンテンツをチャンクに分割"""
        chunk_size = self.config["chunk_size"]
        chunk_overlap = self.config["chunk_overlap"]
        
        # マークダウンの見出しベースで分割を試行
        chunks = self._split_by_headers(content)
        
        # サイズが大きい場合は更に分割
        final_chunks = []
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text) <= chunk_size:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_id": f"{metadata['file_hash']}_chunk_{i}",
                    "chunk_index": i,
                    "chunk_size": len(chunk_text)
                })
                final_chunks.append({
                    "content": chunk_text,
                    "metadata": chunk_metadata
                })
            else:
                # 大きなチャンクを更に分割
                sub_chunks = self._split_large_chunk(chunk_text, chunk_size, chunk_overlap)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_id": f"{metadata['file_hash']}_chunk_{i}_{j}",
                        "chunk_index": f"{i}.{j}",
                        "chunk_size": len(sub_chunk)
                    })
                    final_chunks.append({
                        "content": sub_chunk,
                        "metadata": chunk_metadata
                    })
        
        return final_chunks

    def _split_by_headers(self, content: str) -> List[str]:
        """マークダウンの見出しでコンテンツを分割"""
        # YAML Front Matterを除去
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # 見出しで分割
        header_pattern = r'^(#{1,6}\s+.+)$'
        parts = re.split(header_pattern, content, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if re.match(header_pattern, part):
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = part + "\n"
            else:
                current_chunk += part
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content]

    def _split_large_chunk(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """大きなチャンクを固定サイズで分割"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks

    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """チャンクの埋め込みベクトルを生成"""
        if not self.openai_api_key:
            logger.warning("OpenAI API Keyが設定されていません。埋め込み生成をスキップします。")
            return chunks
        
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            logger.info(f"{len(chunks)}個のチャンクの埋め込みを生成中...")
            
            for i, chunk in enumerate(chunks):
                try:
                    response = openai.Embedding.create(
                        model=self.embedding_model,
                        input=chunk["content"]
                    )
                    chunk["embedding"] = response["data"][0]["embedding"]
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"埋め込み生成進捗: {i + 1}/{len(chunks)}")
                        
                except Exception as e:
                    logger.error(f"埋め込み生成エラー (chunk {i}): {e}")
                    chunk["embedding"] = None
            
            logger.info("埋め込み生成完了")
            
        except ImportError:
            logger.warning("openaiライブラリがインストールされていません")
        except Exception as e:
            logger.error(f"埋め込み生成エラー: {e}")
        
        return chunks

    def save_to_vector_db(self, chunks: List[Dict[str, Any]]) -> bool:
        """Vector DBにデータを保存"""
        if self.vector_db_type == "chroma":
            return self._save_to_chroma(chunks)
        elif self.vector_db_type == "pinecone":
            return self._save_to_pinecone(chunks)
        else:
            logger.info("Vector DB未設定のため、ローカルインデックスに保存")
            return self._save_to_local_index(chunks)

    def _save_to_chroma(self, chunks: List[Dict[str, Any]]) -> bool:
        """ChromaDBに保存"""
        try:
            import chromadb
            client = chromadb.Client()
            collection = client.get_or_create_collection("knowledge_base")
            
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
            documents = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            embeddings = [chunk.get("embedding") for chunk in chunks if chunk.get("embedding")]
            
            if embeddings:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            
            logger.info(f"ChromaDBに{len(chunks)}個のチャンクを保存しました")
            return True
            
        except ImportError:
            logger.warning("chromadbライブラリがインストールされていません")
            return False
        except Exception as e:
            logger.error(f"ChromaDB保存エラー: {e}")
            return False

    def _save_to_local_index(self, chunks: List[Dict[str, Any]]) -> bool:
        """ローカルインデックスに保存"""
        try:
            index_file = self.index_path / "knowledge_index.json"
            
            # 既存インデックスの読み込み
            existing_index = {}
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            
            # 新しいチャンクを追加
            for chunk in chunks:
                chunk_id = chunk["metadata"]["chunk_id"]
                existing_index[chunk_id] = chunk
            
            # インデックスの保存
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(existing_index, f, ensure_ascii=False, indent=2)
            
            logger.info(f"ローカルインデックスに{len(chunks)}個のチャンクを保存しました")
            return True
            
        except Exception as e:
            logger.error(f"ローカルインデックス保存エラー: {e}")
            return False

    def process_file(self, file_path: Path, force: bool = False) -> bool:
        """単一ファイルの処理"""
        logger.info(f"ファイル処理開始: {file_path}")
        
        try:
            # メタデータ抽出
            metadata = self.extract_metadata(file_path)
            
            # 変更チェック（forceオプションがない場合）
            if not force and self._is_file_unchanged(metadata):
                logger.info(f"ファイル未変更のためスキップ: {file_path}")
                return True
            
            # コンテンツ読み込み
            content = file_path.read_text(encoding='utf-8')
            
            # チャンク分割
            chunks = self.chunk_content(content, metadata)
            
            # 埋め込み生成
            chunks = self.create_embeddings(chunks)
            
            # Vector DBに保存
            success = self.save_to_vector_db(chunks)
            
            if success:
                # 処理履歴の更新
                self._update_processing_history(metadata)
                logger.info(f"ファイル処理完了: {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"ファイル処理エラー {file_path}: {e}")
            return False

    def _is_file_unchanged(self, metadata: Dict[str, Any]) -> bool:
        """ファイルが未変更かチェック"""
        history_file = self.index_path / "processing_history.json"
        
        if not history_file.exists():
            return False
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            file_path = metadata["file_path"]
            if file_path in history:
                return history[file_path]["file_hash"] == metadata["file_hash"]
            
        except Exception as e:
            logger.warning(f"処理履歴チェックエラー: {e}")
        
        return False

    def _update_processing_history(self, metadata: Dict[str, Any]) -> None:
        """処理履歴の更新"""
        history_file = self.index_path / "processing_history.json"
        
        history = {}
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass
        
        history[metadata["file_path"]] = {
            "file_hash": metadata["file_hash"],
            "processed_at": datetime.now().isoformat(),
            "file_size": metadata["file_size"]
        }
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"処理履歴更新エラー: {e}")

    def process_category(self, category: str, force: bool = False) -> None:
        """カテゴリ単位での処理"""
        logger.info(f"カテゴリ処理開始: {category}")
        
        files = self.scan_knowledge_base(category)
        if not files:
            logger.warning(f"処理対象ファイルが見つかりません: {category}")
            return
        
        success_count = 0
        for file_path in files:
            if self.process_file(file_path, force):
                success_count += 1
        
        logger.info(f"カテゴリ処理完了: {category} ({success_count}/{len(files)} 成功)")

    def process_all(self, force: bool = False) -> None:
        """全ファイルの処理"""
        logger.info("全ファイル処理開始")
        
        files = self.scan_knowledge_base()
        if not files:
            logger.warning("処理対象ファイルが見つかりません")
            return
        
        success_count = 0
        for file_path in files:
            if self.process_file(file_path, force):
                success_count += 1
        
        logger.info(f"全ファイル処理完了 ({success_count}/{len(files)} 成功)")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="ナレッジベース取り込み・インデックス化ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 全ファイルを処理
  python ingest_knowledge.py --update-all
  
  # 特定カテゴリを処理
  python ingest_knowledge.py --category customer-support
  
  # 単一ファイルを処理
  python ingest_knowledge.py --file common/knowledge/company/products/sample.md
  
  # 強制再処理
  python ingest_knowledge.py --category customer-support --force
        """
    )
    
    parser.add_argument('--update-all', action='store_true',
                       help='全ナレッジファイルを処理')
    parser.add_argument('--category', type=str,
                       help='特定カテゴリのファイルを処理')
    parser.add_argument('--file', type=str,
                       help='単一ファイルを処理')
    parser.add_argument('--force', action='store_true',
                       help='変更チェックをスキップして強制処理')
    parser.add_argument('--config', type=str, default="common/config/knowledge_config.yml",
                       help='設定ファイルのパス')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細ログを出力')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 引数チェック
    if not any([args.update_all, args.category, args.file]):
        parser.print_help()
        sys.exit(1)
    
    try:
        # ログディレクトリ作成
        os.makedirs("common/logs", exist_ok=True)
        
        # インジェスター初期化
        ingestor = KnowledgeIngestor(args.config)
        
        # 処理実行
        if args.update_all:
            ingestor.process_all(args.force)
        elif args.category:
            ingestor.process_category(args.category, args.force)
        elif args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                logger.error(f"ファイルが見つかりません: {args.file}")
                sys.exit(1)
            ingestor.process_file(file_path, args.force)
        
        logger.info("処理完了")
        
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 