#!/usr/bin/env python3
"""
AIエージェント共通基底クラス

製品企画・事業企画など、様々なエージェントで共通利用できる基盤機能を提供します。
ナレッジベース検索、プロンプト管理、成果物保存、ユーザー確認などを統一化。

使用例:
    from common.utils.agent_base import AgentBase
    
    class ProductPlanningAgent(AgentBase):
        def __init__(self):
            super().__init__("product-planning", "製品企画エージェント")
        
        def analyze_market(self, target_market):
            return self.execute_with_knowledge("市場分析", target_market)
"""

import os
import yaml
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from .output_manager import OutputManager, get_output_manager
from .knowledge_search import search_knowledge, get_related_documents

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    """AIエージェント共通基底クラス"""
    
    def __init__(self, agent_name: str, display_name: str, 
                 config_path: Optional[str] = None):
        """
        AgentBase初期化
        
        Args:
            agent_name: エージェント名（ディレクトリ名）
            display_name: 表示名
            config_path: 設定ファイルパス（None=自動推定）
        """
        self.agent_name = agent_name
        self.display_name = display_name
        
        # 設定ファイルパス
        if config_path is None:
            config_path = f"agents/{agent_name}/config.yml"
        self.config_path = config_path
        
        # 設定読み込み
        self.config = self._load_config()
        
        # 出力マネージャー（必要時に初期化）
        self._output_manager = None
        self._current_project_date = None
        
        # AIクライアント（必要時に初期化）
        self._ai_client = None
        
        logger.info(f"{self.display_name}初期化完了")

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"設定読み込み完了: {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"設定ファイルが見つかりません: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "agent_info": {
                "name": self.display_name,
                "version": "1.0.0"
            },
            "system_prompt": f"あなたは{self.display_name}です。",
            "ai_parameters": {
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "knowledge_base": {
                "priority_sources": ["common/knowledge"],
                "search_depth": "deep"
            }
        }

    def get_output_manager(self, project_date: Optional[str] = None) -> OutputManager:
        """出力マネージャーを取得"""
        if project_date is None:
            project_date = datetime.now().strftime("%Y%m%d")
        
        if self._output_manager is None or self._current_project_date != project_date:
            self._output_manager = get_output_manager(self.agent_name, project_date)
            self._current_project_date = project_date
        
        return self._output_manager

    def search_knowledge(self, query: str, categories: Optional[List[str]] = None,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        ナレッジベースを検索
        
        Args:
            query: 検索クエリ
            categories: 検索対象カテゴリ
            limit: 最大結果数
            
        Returns:
            検索結果のリスト
        """
        # 設定から優先ソースを取得
        if categories is None:
            categories = self.config.get("knowledge_base", {}).get("priority_sources", [])
        
        results = search_knowledge(query, categories, limit)
        
        logger.info(f"ナレッジ検索: '{query}' -> {len(results)}件")
        return results

    def ask_user_confirmation(self, message: str, options: Optional[List[str]] = None) -> str:
        """
        ユーザーに確認を求める
        
        Args:
            message: 確認メッセージ
            options: 選択肢（None=自由入力）
            
        Returns:
            ユーザーの回答
        """
        print(f"\n🤖 {self.display_name}からの確認:")
        print(f"📝 {message}")
        
        if options:
            print("\n選択肢:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = input("\n番号を選択してください: ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        return options[choice_num - 1]
                    else:
                        print("有効な番号を入力してください。")
                except ValueError:
                    print("数字を入力してください。")
        else:
            return input("\n回答を入力してください: ").strip()

    def ask_user_input(self, prompt: str, required: bool = True) -> str:
        """
        ユーザーに入力を求める
        
        Args:
            prompt: 入力プロンプト
            required: 必須入力かどうか
            
        Returns:
            ユーザーの入力
        """
        print(f"\n🤖 {self.display_name}:")
        print(f"📝 {prompt}")
        
        while True:
            user_input = input("\n入力してください: ").strip()
            
            if user_input or not required:
                return user_input
            else:
                print("入力が必要です。")

    def save_intermediate_result(self, filename: str, content: str,
                               metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        中間成果物を保存
        
        Args:
            filename: ファイル名
            content: コンテンツ
            metadata: メタデータ
            
        Returns:
            保存されたファイルのパス
        """
        output_manager = self.get_output_manager()
        return output_manager.save_intermediate(filename, content, metadata)

    def save_final_result(self, template_name: str, content: str,
                         metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        最終成果物を保存
        
        Args:
            template_name: テンプレート名
            content: コンテンツ
            metadata: メタデータ
            
        Returns:
            保存されたファイルのパス
        """
        output_manager = self.get_output_manager()
        return output_manager.save_final_report(template_name, content, metadata)

    def execute_with_knowledge(self, task_name: str, user_input: str,
                              knowledge_query: Optional[str] = None) -> str:
        """
        ナレッジベースを活用してタスクを実行
        
        Args:
            task_name: タスク名
            user_input: ユーザー入力
            knowledge_query: ナレッジ検索クエリ（None=user_inputを使用）
            
        Returns:
            実行結果
        """
        # ナレッジ検索
        if knowledge_query is None:
            knowledge_query = user_input
        
        knowledge_results = self.search_knowledge(knowledge_query)
        
        # 関連ナレッジをコンテキストに追加
        knowledge_context = self._format_knowledge_context(knowledge_results)
        
        # プロンプト構築
        system_prompt = self.config.get("system_prompt", "")
        
        # タスク実行（サブクラスで実装）
        result = self._execute_ai_task(
            task_name=task_name,
            user_input=user_input,
            system_prompt=system_prompt,
            knowledge_context=knowledge_context
        )
        
        # 中間成果物として保存
        self.save_intermediate_result(
            filename=f"{task_name.replace(' ', '_')}",
            content=result,
            metadata={
                "task_name": task_name,
                "knowledge_query": knowledge_query,
                "knowledge_results_count": len(knowledge_results)
            }
        )
        
        return result

    def _format_knowledge_context(self, knowledge_results: List[Dict[str, Any]]) -> str:
        """ナレッジ検索結果をコンテキスト形式に整形"""
        if not knowledge_results:
            return ""
        
        context_parts = ["## 📚 関連するナレッジベース情報\n"]
        
        for i, result in enumerate(knowledge_results[:3], 1):  # 上位3件
            metadata = result.get("metadata", {})
            content = result.get("content", "")
            
            # コンテンツを要約（長すぎる場合）
            if len(content) > 500:
                content = content[:500] + "..."
            
            context_parts.append(f"### {i}. {metadata.get('file_name', '不明')}")
            context_parts.append(f"**カテゴリ**: {metadata.get('category', '不明')}")
            context_parts.append(f"**関連度**: {result.get('similarity', 0):.2f}")
            context_parts.append(f"\n{content}\n")
        
        return "\n".join(context_parts)

    @abstractmethod
    def _execute_ai_task(self, task_name: str, user_input: str,
                        system_prompt: str, knowledge_context: str) -> str:
        """
        AIタスクを実行（サブクラスで実装）
        
        Args:
            task_name: タスク名
            user_input: ユーザー入力
            system_prompt: システムプロンプト
            knowledge_context: ナレッジコンテキスト
            
        Returns:
            AI応答
        """
        pass

    def get_template_content(self, template_name: str) -> str:
        """
        テンプレートコンテンツを取得
        
        Args:
            template_name: テンプレート名
            
        Returns:
            テンプレートコンテンツ
        """
        output_manager = self.get_output_manager()
        return output_manager.load_template(template_name)

    def get_project_status(self) -> Dict[str, Any]:
        """
        現在のプロジェクト状況を取得
        
        Returns:
            プロジェクト状況
        """
        output_manager = self.get_output_manager()
        return output_manager.get_project_status()

    def validate_requirements(self, requirements: Dict[str, Any]) -> List[str]:
        """
        要件を検証し、不明点を特定
        
        Args:
            requirements: 要件辞書
            
        Returns:
            不明点・確認事項のリスト
        """
        unclear_points = []
        
        # 基本的な検証ルール
        required_fields = ["target", "objective", "scope"]
        
        for field in required_fields:
            if field not in requirements or not requirements[field]:
                unclear_points.append(f"{field}が明確でありません。具体的に教えてください。")
        
        # 曖昧な表現をチェック
        ambiguous_keywords = ["なんとなく", "適当に", "よろしく", "いい感じに"]
        
        for key, value in requirements.items():
            if isinstance(value, str):
                for keyword in ambiguous_keywords:
                    if keyword in value:
                        unclear_points.append(f"{key}の内容が曖昧です。より具体的に教えてください。")
                        break
        
        return unclear_points

    def clarify_requirements(self, initial_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        要件を明確化（ユーザーとの対話）
        
        Args:
            initial_requirements: 初期要件
            
        Returns:
            明確化された要件
        """
        unclear_points = self.validate_requirements(initial_requirements)
        
        if not unclear_points:
            return initial_requirements
        
        print(f"\n🤖 {self.display_name}:")
        print("要件を明確化するために、いくつか確認させてください。\n")
        
        clarified_requirements = initial_requirements.copy()
        
        for point in unclear_points:
            response = self.ask_user_input(point, required=True)
            
            # 回答を適切なフィールドに格納
            if "target" in point.lower():
                clarified_requirements["target"] = response
            elif "objective" in point.lower():
                clarified_requirements["objective"] = response
            elif "scope" in point.lower():
                clarified_requirements["scope"] = response
            else:
                # その他の確認事項
                if "clarifications" not in clarified_requirements:
                    clarified_requirements["clarifications"] = {}
                clarified_requirements["clarifications"][point] = response
        
        return clarified_requirements

class OpenAIAgentBase(AgentBase):
    """OpenAI APIを使用するエージェント基底クラス"""
    
    def __init__(self, agent_name: str, display_name: str, 
                 config_path: Optional[str] = None):
        super().__init__(agent_name, display_name, config_path)
        
        # OpenAI設定
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY が設定されていません")

    def _execute_ai_task(self, task_name: str, user_input: str,
                        system_prompt: str, knowledge_context: str) -> str:
        """OpenAI APIを使用してタスクを実行"""
        if not self.api_key:
            return f"OpenAI API Keyが設定されていないため、{task_name}を実行できません。"
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # プロンプト構築
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            if knowledge_context:
                messages.append({
                    "role": "user", 
                    "content": f"{knowledge_context}\n\n---\n\n{user_input}"
                })
            else:
                messages.append({"role": "user", "content": user_input})
            
            # AI実行
            ai_params = self.config.get("ai_parameters", {})
            response = openai.ChatCompletion.create(
                model=ai_params.get("model", "gpt-4"),
                messages=messages,
                temperature=ai_params.get("temperature", 0.7),
                max_tokens=ai_params.get("max_tokens", 2000)
            )
            
            result = response.choices[0].message.content
            logger.info(f"AI タスク実行完了: {task_name}")
            
            return result
            
        except ImportError:
            logger.error("openaiライブラリがインストールされていません")
            return f"OpenAIライブラリが見つからないため、{task_name}を実行できません。"
        except Exception as e:
            logger.error(f"AI タスク実行エラー: {e}")
            return f"エラーが発生しました: {e}" 


class ClaudeAgentBase(AgentBase):
    """Claude APIを使用するエージェント基底クラス"""
    
    def __init__(self, agent_name: str, display_name: str, 
                 config_path: Optional[str] = None):
        super().__init__(agent_name, display_name, config_path)
        
        # Claude設定
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY が設定されていません")

    def _execute_ai_task(self, task_name: str, user_input: str,
                        system_prompt: str, knowledge_context: str) -> str:
        """Claude APIを使用してタスクを実行"""
        if not self.api_key:
            return f"Claude API Keyが設定されていないため、{task_name}を実行できません。"
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # プロンプト構築
            if knowledge_context:
                user_message = f"{knowledge_context}\n\n---\n\n{user_input}"
            else:
                user_message = user_input
            
            # AI実行
            ai_params = self.config.get("ai_parameters", {}).get("claude", {})
            response = client.messages.create(
                model=ai_params.get("model", "claude-3-sonnet-20240229"),
                max_tokens=ai_params.get("max_tokens", 2000),
                temperature=ai_params.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result = response.content[0].text
            logger.info(f"Claude AI タスク実行完了: {task_name}")
            
            return result
            
        except ImportError:
            logger.error("anthropicライブラリがインストールされていません")
            return f"Anthropicライブラリが見つからないため、{task_name}を実行できません。"
        except Exception as e:
            logger.error(f"Claude AI タスク実行エラー: {e}")
            return f"エラーが発生しました: {e}" 

    def _execute_code_task(self, task_name: str, code: str) -> str:
        """Claude Code実行機能を使用してコードを実行"""
        if not self.api_key:
            return f"Claude API Keyが設定されていないため、{task_name}を実行できません。"
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # コード実行用のプロンプト
            system_prompt = """
            あなたは優秀なデータサイエンティスト兼プログラマです。
            提供されたコードを実行し、結果を分析して報告してください。
            
            以下の形式で回答してください：
            1. 実行結果の要約
            2. 生成されたグラフやデータの説明
            3. 重要な発見やインサイト
            4. 推奨事項
            """
            
            user_message = f"""
            以下のコードを実行してください：
            
            ```python
            {code}
            ```
            
            実行結果とその分析を提供してください。
            """
            
            ai_params = self.config.get("ai_parameters", {}).get("claude", {})
            response = client.messages.create(
                model=ai_params.get("model", "claude-3-sonnet-20240229"),
                max_tokens=ai_params.get("max_tokens", 2000),
                temperature=ai_params.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result = response.content[0].text
            logger.info(f"Claude Code実行完了: {task_name}")
            
            return result
            
        except ImportError:
            logger.error("anthropicライブラリがインストールされていません")
            return f"Anthropicライブラリが見つからないため、{task_name}を実行できません。"
        except Exception as e:
            logger.error(f"Claude Code実行エラー: {e}")
            return f"エラーが発生しました: {e}" 


class MultiAIAgentBase(AgentBase):
    """複数のAIプロバイダーを統合するエージェント基底クラス"""
    
    def __init__(self, agent_name: str, display_name: str, 
                 config_path: Optional[str] = None):
        super().__init__(agent_name, display_name, config_path)
        
        # 設定からプロバイダーを取得
        self.provider = self.config.get("ai_parameters", {}).get("provider", "openai")
        
        # 各プロバイダーの設定
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        
        # 利用可能なプロバイダーをチェック
        self.available_providers = []
        if self.openai_key:
            self.available_providers.append("openai")
        if self.claude_key:
            self.available_providers.append("claude")
        
        if not self.available_providers:
            logger.warning("利用可能なAIプロバイダーがありません")
        elif self.provider not in self.available_providers:
            logger.warning(f"指定されたプロバイダー '{self.provider}' が利用できません。利用可能: {self.available_providers}")
            if self.available_providers:
                self.provider = self.available_providers[0]
                logger.info(f"プロバイダーを '{self.provider}' に変更しました")

    def _execute_ai_task(self, task_name: str, user_input: str,
                        system_prompt: str, knowledge_context: str) -> str:
        """設定に基づいて適切なAIプロバイダーでタスクを実行"""
        
        if self.provider == "claude" and self.claude_key:
            return self._execute_claude_task(task_name, user_input, system_prompt, knowledge_context)
        elif self.provider == "openai" and self.openai_key:
            return self._execute_openai_task(task_name, user_input, system_prompt, knowledge_context)
        elif self.provider == "both" and self.claude_key and self.openai_key:
            # 両方のプロバイダーを使用して結果を比較
            return self._execute_both_providers(task_name, user_input, system_prompt, knowledge_context)
        else:
            return f"利用可能なAIプロバイダーがありません。設定を確認してください。"

    def _execute_claude_task(self, task_name: str, user_input: str,
                            system_prompt: str, knowledge_context: str) -> str:
        """Claude APIでタスクを実行"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            # プロンプト構築
            if knowledge_context:
                user_message = f"{knowledge_context}\n\n---\n\n{user_input}"
            else:
                user_message = user_input
            
            # AI実行
            ai_params = self.config.get("ai_parameters", {}).get("claude", {})
            response = client.messages.create(
                model=ai_params.get("model", "claude-3-sonnet-20240229"),
                max_tokens=ai_params.get("max_tokens", 2000),
                temperature=ai_params.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result = response.content[0].text
            logger.info(f"Claude AI タスク実行完了: {task_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Claude AI タスク実行エラー: {e}")
            return f"Claude AIエラー: {e}"

    def _execute_openai_task(self, task_name: str, user_input: str,
                            system_prompt: str, knowledge_context: str) -> str:
        """OpenAI APIでタスクを実行"""
        try:
            import openai
            openai.api_key = self.openai_key
            
            # プロンプト構築
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            if knowledge_context:
                messages.append({
                    "role": "user", 
                    "content": f"{knowledge_context}\n\n---\n\n{user_input}"
                })
            else:
                messages.append({"role": "user", "content": user_input})
            
            # AI実行
            ai_params = self.config.get("ai_parameters", {}).get("openai", {})
            response = openai.ChatCompletion.create(
                model=ai_params.get("model", "gpt-4"),
                messages=messages,
                temperature=ai_params.get("temperature", 0.7),
                max_tokens=ai_params.get("max_tokens", 2000)
            )
            
            result = response.choices[0].message.content
            logger.info(f"OpenAI タスク実行完了: {task_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI タスク実行エラー: {e}")
            return f"OpenAI エラー: {e}"

    def _execute_both_providers(self, task_name: str, user_input: str,
                               system_prompt: str, knowledge_context: str) -> str:
        """両方のプロバイダーを使用して結果を比較"""
        claude_result = self._execute_claude_task(task_name, user_input, system_prompt, knowledge_context)
        openai_result = self._execute_openai_task(task_name, user_input, system_prompt, knowledge_context)
        
        # 結果を統合
        combined_result = f"""
# 🤖 AI分析結果 - 複数プロバイダー比較

## 🔹 Claude分析結果
{claude_result}

## 🔹 OpenAI分析結果
{openai_result}

## 📊 統合まとめ
両方のAIプロバイダーからの分析結果を統合し、より包括的な洞察を提供します。
"""
        
        return combined_result

    def execute_code_analysis(self, code: str, task_name: str = "コード分析") -> str:
        """コード分析専用メソッド（Claude Code機能を優先使用）"""
        if self.claude_key:
            return self._execute_claude_code_task(task_name, code)
        else:
            return self._execute_ai_task(
                task_name, 
                f"以下のコードを分析してください：\n\n```python\n{code}\n```",
                "あなたは優秀なコードレビュアーです。提供されたコードを分析し、実行結果を予測し、改善点を提案してください。",
                ""
            )

    def _execute_claude_code_task(self, task_name: str, code: str) -> str:
        """Claude Code実行機能を使用"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            system_prompt = """
            あなたは優秀なデータサイエンティスト兼プログラマです。
            提供されたコードを実行し、結果を分析して報告してください。
            
            以下の形式で回答してください：
            1. 実行結果の要約
            2. 生成されたグラフやデータの説明
            3. 重要な発見やインサイト
            4. 推奨事項
            """
            
            user_message = f"""
            以下のコードを実行してください：
            
            ```python
            {code}
            ```
            
            実行結果とその分析を提供してください。
            """
            
            ai_params = self.config.get("ai_parameters", {}).get("claude", {})
            response = client.messages.create(
                model=ai_params.get("model", "claude-3-sonnet-20240229"),
                max_tokens=ai_params.get("max_tokens", 2000),
                temperature=ai_params.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result = response.content[0].text
            logger.info(f"Claude Code実行完了: {task_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Claude Code実行エラー: {e}")
            return f"Claude Code実行エラー: {e}"