#!/usr/bin/env python3
"""
ナレッジベース検索ユーティリティ

企業独自のナレッジベースから関連情報を効率的に検索し、
AIエージェントが活用できる形で提供します。

使用例:
    from common.utils.knowledge_search import search_knowledge
    
    results = search_knowledge(
        query="顧客からのAPI統合相談事例",
        categories=["customer-support", "company/products"],
        limit=5
    )
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeSearcher:
    """ナレッジベース検索クラス"""
    
    def __init__(self, knowledge_base_path: str = "common/knowledge"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.index_path = Path(knowledge_base_path) / ".index"
        
        # Vector DB設定（環境変数から取得）
        self.vector_db_type = os.getenv("VECTOR_DB_TYPE", "local")
        self.use_vector_db = self.vector_db_type != "local"
        
        logger.info(f"KnowledgeSearcher初期化 - Vector DB: {self.vector_db_type}")

    def search(self, query: str, categories: Optional[List[str]] = None,
               limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        ナレッジベースを検索
        
        Args:
            query: 検索クエリ
            categories: 検索対象カテゴリ（None=全体）
            limit: 最大結果数
            similarity_threshold: 類似度閾値
            
        Returns:
            検索結果のリスト
        """
        if self.use_vector_db:
            return self._vector_search(query, categories, limit, similarity_threshold)
        else:
            return self._text_search(query, categories, limit)

    def _vector_search(self, query: str, categories: Optional[List[str]], 
                      limit: int, similarity_threshold: float) -> List[Dict[str, Any]]:
        """Vector DBを使用した検索"""
        try:
            if self.vector_db_type == "chroma":
                return self._chroma_search(query, categories, limit, similarity_threshold)
            else:
                logger.warning(f"未対応のVector DB: {self.vector_db_type}")
                return self._text_search(query, categories, limit)
        except Exception as e:
            logger.error(f"Vector DB検索エラー: {e}")
            return self._text_search(query, categories, limit)

    def _chroma_search(self, query: str, categories: Optional[List[str]], 
                      limit: int, similarity_threshold: float) -> List[Dict[str, Any]]:
        """ChromaDBを使用した検索"""
        try:
            import chromadb
            client = chromadb.Client()
            collection = client.get_collection("knowledge_base")
            
            # カテゴリフィルタ
            where_filter = None
            if categories:
                where_filter = {"category": {"$in": categories}}
            
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            
            search_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                similarity = 1 - distance  # 距離を類似度に変換
                if similarity >= similarity_threshold:
                    search_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "rank": i + 1
                    })
            
            return search_results
            
        except ImportError:
            logger.warning("chromadbライブラリがインストールされていません")
            return []
        except Exception as e:
            logger.error(f"ChromaDB検索エラー: {e}")
            return []

    def _text_search(self, query: str, categories: Optional[List[str]], 
                    limit: int) -> List[Dict[str, Any]]:
        """テキストベースの検索（フォールバック）"""
        logger.info("テキストベース検索を実行")
        
        # ローカルインデックスから検索
        index_file = self.index_path / "knowledge_index.json"
        if index_file.exists():
            return self._search_from_index(query, categories, limit, index_file)
        
        # インデックスがない場合はファイル直接検索
        return self._search_files_directly(query, categories, limit)

    def _search_from_index(self, query: str, categories: Optional[List[str]], 
                          limit: int, index_file: Path) -> List[Dict[str, Any]]:
        """インデックスファイルから検索"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            results = []
            query_terms = self._extract_search_terms(query)
            
            for chunk_id, chunk_data in index.items():
                content = chunk_data.get("content", "")
                metadata = chunk_data.get("metadata", {})
                
                # カテゴリフィルタ
                if categories and metadata.get("category") not in categories:
                    continue
                
                # スコア計算
                score = self._calculate_text_score(content, metadata, query_terms)
                
                if score > 0:
                    results.append({
                        "content": content,
                        "metadata": metadata,
                        "similarity": score,
                        "rank": 0  # 後でソート後に設定
                    })
            
            # スコア順でソート
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # ランク設定
            for i, result in enumerate(results[:limit]):
                result["rank"] = i + 1
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"インデックス検索エラー: {e}")
            return []

    def _search_files_directly(self, query: str, categories: Optional[List[str]], 
                              limit: int) -> List[Dict[str, Any]]:
        """ファイル直接検索"""
        results = []
        query_terms = self._extract_search_terms(query)
        
        # 検索対象パスを決定
        search_paths = []
        if categories:
            for category in categories:
                category_path = self.knowledge_base_path / category
                if category_path.exists():
                    search_paths.append(category_path)
        else:
            search_paths = [self.knowledge_base_path]
        
        # ファイル検索
        for search_path in search_paths:
            for file_path in search_path.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    metadata = self._extract_metadata_from_file(file_path, content)
                    
                    score = self._calculate_text_score(content, metadata, query_terms)
                    
                    if score > 0:
                        results.append({
                            "content": content,
                            "metadata": metadata,
                            "similarity": score,
                            "rank": 0
                        })
                        
                except Exception as e:
                    logger.warning(f"ファイル読み込みエラー {file_path}: {e}")
        
        # スコア順でソート
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # ランク設定
        for i, result in enumerate(results[:limit]):
            result["rank"] = i + 1
        
        return results[:limit]

    def _extract_search_terms(self, query: str) -> List[str]:
        """検索クエリからキーワードを抽出"""
        # 日本語・英語の単語を抽出
        terms = re.findall(r'[ぁ-んァ-ヶ一-龠a-zA-Z0-9]+', query)
        
        # 重複除去・小文字化
        unique_terms = list(set([term.lower() for term in terms if len(term) > 1]))
        
        return unique_terms

    def _calculate_text_score(self, content: str, metadata: Dict[str, Any], 
                             query_terms: List[str]) -> float:
        """テキストベースのスコア計算"""
        score = 0.0
        content_lower = content.lower()
        
        # コンテンツマッチング
        for term in query_terms:
            count = content_lower.count(term.lower())
            score += count * 1.0
        
        # メタデータマッチング（重み付け）
        metadata_text = " ".join([str(v) for v in metadata.values()]).lower()
        for term in query_terms:
            if term.lower() in metadata_text:
                score += 2.0  # メタデータマッチは高スコア
        
        # タイトル・見出しマッチング（重み付け）
        title_pattern = r'^#+ (.+)$'
        titles = re.findall(title_pattern, content, re.MULTILINE)
        title_text = " ".join(titles).lower()
        for term in query_terms:
            if term.lower() in title_text:
                score += 3.0  # タイトルマッチは最高スコア
        
        # 正規化（コンテンツ長で調整）
        content_length = len(content)
        if content_length > 0:
            score = score / (content_length / 1000)  # 1000文字あたりのスコア
        
        return min(score, 1.0)  # 最大1.0に制限

    def _extract_metadata_from_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """ファイルからメタデータを抽出"""
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "category": self._extract_category_from_path(file_path),
            "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # YAML Front Matterを抽出
        yaml_metadata = self._extract_yaml_frontmatter(content)
        metadata.update(yaml_metadata)
        
        return metadata

    def _extract_category_from_path(self, file_path: Path) -> str:
        """ファイルパスからカテゴリを抽出"""
        try:
            relative_path = file_path.relative_to(self.knowledge_base_path)
            return str(relative_path.parent).replace(os.sep, "/")
        except ValueError:
            return "unknown"

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

    def get_related_documents(self, document_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """関連文書を取得"""
        try:
            file_path = Path(document_path)
            if not file_path.exists():
                return []
            
            content = file_path.read_text(encoding='utf-8')
            metadata = self._extract_metadata_from_file(file_path, content)
            
            # タイトルとタグから関連文書を検索
            search_terms = []
            if "tags" in metadata:
                search_terms.extend(metadata["tags"])
            if "category" in metadata:
                search_terms.append(metadata["category"])
            
            query = " ".join(search_terms)
            
            results = self.search(query, limit=limit + 1)  # 自分自身を除くため+1
            
            # 自分自身を除外
            filtered_results = [r for r in results if r["metadata"].get("file_path") != document_path]
            
            return filtered_results[:limit]
            
        except Exception as e:
            logger.error(f"関連文書取得エラー: {e}")
            return []

# グローバル検索関数
_searcher = None

def search_knowledge(query: str, categories: Optional[List[str]] = None,
                    limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    ナレッジベース検索のグローバル関数
    
    Args:
        query: 検索クエリ
        categories: 検索対象カテゴリ
        limit: 最大結果数
        similarity_threshold: 類似度閾値
        
    Returns:
        検索結果のリスト
    """
    global _searcher
    if _searcher is None:
        _searcher = KnowledgeSearcher()
    
    return _searcher.search(query, categories, limit, similarity_threshold)

def get_related_documents(document_path: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    関連文書取得のグローバル関数
    
    Args:
        document_path: 基準文書のパス
        limit: 最大結果数
        
    Returns:
        関連文書のリスト
    """
    global _searcher
    if _searcher is None:
        _searcher = KnowledgeSearcher()
    
    return _searcher.get_related_documents(document_path, limit) 