#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code分析エンジン
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
import pandas as pd
import numpy as np

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from common.utils.agent_base import MultiAIAgentBase

class ClaudeCodeAnalyzer(MultiAIAgentBase):
    """Claude Code機能を使用した分析エンジン"""
    
    def __init__(self, project_dir: str = None, verbose: bool = False):
        super().__init__(
            agent_name="persona", 
            display_name="Claude Code分析エンジン",
            config_path="agents/persona/config.yml"
        )
        
        self.project_dir = Path(project_dir) if project_dir else Path(".")
        self.verbose = verbose
        self.setup_logging()
        
    def setup_logging(self):
        """ログ設定"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
    def generate_sample_data(self) -> pd.DataFrame:
        """サンプルデータ生成"""
        np.random.seed(42)
        n_customers = 1000
        
        data = {
            'customer_id': range(1, n_customers + 1),
            'age': np.random.normal(35, 12, n_customers).astype(int),
            'income': np.random.lognormal(10.5, 0.5, n_customers).astype(int),
            'satisfaction_score': np.random.normal(7.5, 1.5, n_customers).clip(1, 10),
        }
        
        data['age'] = np.clip(data['age'], 18, 80)
        data['income'] = np.clip(data['income'], 200, 2000)
        
        return pd.DataFrame(data)
        
    def analyze_with_claude_code(self, df: pd.DataFrame) -> str:
        """Claude Code機能でデータ分析"""
        
        csv_data = df.to_csv(index=False)
        
        code = f"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# データ読み込み
csv_data = '''{csv_data}'''
df = pd.read_csv(io.StringIO(csv_data))

# 基本統計
print("データ基本統計:")
print(df.describe())

# 可視化
plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
plt.hist(df['age'], bins=20, alpha=0.7)
plt.title('年齢分布')

plt.subplot(1, 3, 2)
plt.hist(df['income'], bins=20, alpha=0.7)
plt.title('年収分布')

plt.subplot(1, 3, 3)
plt.scatter(df['age'], df['income'], alpha=0.5)
plt.xlabel('年齢')
plt.ylabel('年収')
plt.title('年齢 vs 年収')

plt.tight_layout()
plt.show()
"""
        
        return self.execute_code_analysis(code, "データ分析")
        
    def run_analysis(self, date: str = None) -> Dict:
        """分析実行"""
        
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        self.logger.info(f"分析開始: {date}")
        
        # データ生成
        df = self.generate_sample_data()
        
        # Claude Code分析
        analysis_result = self.analyze_with_claude_code(df)
        
        return {
            'date': date,
            'analysis_result': analysis_result,
            'data_count': len(df)
        }


def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description='Claude Code分析')
    parser.add_argument('--date', type=str, help='分析日付')
    parser.add_argument('--verbose', action='store_true', help='詳細ログ')
    
    args = parser.parse_args()
    
    try:
        analyzer = ClaudeCodeAnalyzer(verbose=args.verbose)
        result = analyzer.run_analysis(date=args.date)
        
        print(f"✅ 分析完了: {result['date']}")
        print(f"📊 データ件数: {result['data_count']}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 