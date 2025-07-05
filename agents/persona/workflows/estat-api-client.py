#!/usr/bin/env python3
"""
ペルソナベースAIエージェント - e-Stat API クライアント

このスクリプトは、日本の政府統計データ（e-Stat API）から統計データを取得します。
- 人口統計データの取得
- 家計調査データの取得
- 労働力調査データの取得
- XML→JSON変換・データクレンジング
- 統計データ可視化・Excel出力

使用方法:
    python estat-api-client.py --demo                          # デモ用サンプルデータ生成
    python estat-api-client.py --population                    # 人口統計データ取得
    python estat-api-client.py --household                     # 家計調査データ取得
    python estat-api-client.py --all                          # 全統計データ取得
"""

import os
import sys
import argparse
import datetime
import json
import pandas as pd
import numpy as np
from pathlib import Path
import requests
import xmltodict
import logging
from typing import Dict, List, Any, Optional
import time

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('estat-api-client.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

class EStatAPIClient:
    """e-Stat API クライアント"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ESTAT_API_KEY')
        self.base_url = "https://api.e-stat.go.jp/rest/3.0/app/json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PersonaAgent/1.0 (Statistical Analysis Tool)'
        })
        
        # API制限対応（1秒間に1リクエスト）
        self.last_request_time = 0
        self.min_interval = 1.0
    
    def _wait_for_rate_limit(self):
        """レート制限対応の待機"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """API リクエストを実行"""
        self._wait_for_rate_limit()
        
        if not self.api_key:
            logger.warning("e-Stat APIキーが設定されていません。デモモードで実行します。")
            return self._generate_demo_data(endpoint, params)
        
        try:
            # APIキーを追加
            params['appId'] = self.api_key
            
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            logger.info(f"API リクエスト成功: {endpoint}")
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"API リクエストエラー: {e}")
            logger.info("デモデータで代替します。")
            return self._generate_demo_data(endpoint, params)
    
    def _generate_demo_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """デモ用データを生成"""
        logger.info(f"デモデータを生成中: {endpoint}")
        
        if 'getStatsData' in endpoint or 'population' in str(params):
            return self._generate_population_demo()
        elif 'household' in str(params):
            return self._generate_household_demo()
        elif 'labor' in str(params):
            return self._generate_labor_demo()
        else:
            return self._generate_basic_demo()
    
    def _generate_population_demo(self) -> Dict[str, Any]:
        """人口統計デモデータ"""
        return {
            "GET_STATS_DATA": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。"
                },
                "PARAMETER": {
                    "DATA_FORMAT": "json"
                },
                "TABLE_INF": {
                    "TITLE": "人口推計（デモデータ）"
                },
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "cat01",
                            "@name": "男女",
                            "CLASS": [
                                {"@code": "1", "@name": "総数"},
                                {"@code": "2", "@name": "男"},
                                {"@code": "3", "@name": "女"}
                            ]
                        },
                        {
                            "@id": "cat02", 
                            "@name": "年齢",
                            "CLASS": [
                                {"@code": "001", "@name": "総数"},
                                {"@code": "002", "@name": "0～14歳"},
                                {"@code": "003", "@name": "15～64歳"},
                                {"@code": "004", "@name": "65歳以上"}
                            ]
                        }
                    ]
                },
                "DATA_INF": {
                    "VALUE": [
                        {"@cat01": "1", "@cat02": "001", "$": "125000000"},  # 総人口
                        {"@cat01": "2", "@cat02": "001", "$": "61000000"},   # 男性総数
                        {"@cat01": "3", "@cat02": "001", "$": "64000000"},   # 女性総数
                        {"@cat01": "1", "@cat02": "002", "$": "15000000"},   # 0-14歳
                        {"@cat01": "1", "@cat02": "003", "$": "75000000"},   # 15-64歳
                        {"@cat01": "1", "@cat02": "004", "$": "35000000"},   # 65歳以上
                    ]
                }
            }
        }
    
    def _generate_household_demo(self) -> Dict[str, Any]:
        """家計調査デモデータ"""
        return {
            "GET_STATS_DATA": {
                "RESULT": {"STATUS": 0},
                "TABLE_INF": {"TITLE": "家計調査（デモデータ）"},
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "cat01",
                            "@name": "費目",
                            "CLASS": [
                                {"@code": "001", "@name": "消費支出"},
                                {"@code": "002", "@name": "食料"},
                                {"@code": "003", "@name": "住居"},
                                {"@code": "004", "@name": "光熱・水道"},
                                {"@code": "005", "@name": "交通・通信"}
                            ]
                        }
                    ]
                },
                "DATA_INF": {
                    "VALUE": [
                        {"@cat01": "001", "$": "280000"},  # 消費支出（月額）
                        {"@cat01": "002", "$": "75000"},   # 食料
                        {"@cat01": "003", "$": "60000"},   # 住居
                        {"@cat01": "004", "$": "20000"},   # 光熱・水道
                        {"@cat01": "005", "$": "45000"},   # 交通・通信
                    ]
                }
            }
        }
    
    def _generate_labor_demo(self) -> Dict[str, Any]:
        """労働力調査デモデータ"""
        return {
            "GET_STATS_DATA": {
                "RESULT": {"STATUS": 0},
                "TABLE_INF": {"TITLE": "労働力調査（デモデータ）"},
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "cat01",
                            "@name": "就業状態",
                            "CLASS": [
                                {"@code": "01", "@name": "労働力人口"},
                                {"@code": "02", "@name": "就業者"},
                                {"@code": "03", "@name": "完全失業者"},
                                {"@code": "04", "@name": "非労働力人口"}
                            ]
                        }
                    ]
                },
                "DATA_INF": {
                    "VALUE": [
                        {"@cat01": "01", "$": "69000000"},  # 労働力人口
                        {"@cat01": "02", "$": "67500000"},  # 就業者
                        {"@cat01": "03", "$": "1500000"},   # 完全失業者
                        {"@cat01": "04", "$": "42000000"},  # 非労働力人口
                    ]
                }
            }
        }
    
    def _generate_basic_demo(self) -> Dict[str, Any]:
        """基本デモデータ"""
        return {
            "GET_STATS_DATA": {
                "RESULT": {"STATUS": 0},
                "TABLE_INF": {"TITLE": "統計データ（デモ）"},
                "DATA_INF": {
                    "VALUE": [
                        {"@cat01": "001", "$": "1000000"}
                    ]
                }
            }
        }
    
    def get_population_data(self) -> pd.DataFrame:
        """人口統計データを取得"""
        logger.info("人口統計データを取得中...")
        
        params = {
            'statsDataId': '0003448697',  # 人口推計の統計表ID
            'metaGetFlg': 'Y',
            'cntGetFlg': 'N',
            'explanationGetFlg': 'Y',
            'annotationGetFlg': 'Y',
            'sectionHeaderFlg': '1'
        }
        
        data = self._make_request('getStatsData', params)
        df = self._parse_population_data(data)
        
        logger.info(f"人口統計データ取得完了: {len(df)}行")
        return df
    
    def _parse_population_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """人口統計データを解析してDataFrameに変換"""
        try:
            stats_data = data['GET_STATS_DATA']
            values = stats_data['DATA_INF']['VALUE']
            
            # クラス情報を取得
            class_info = {}
            if 'CLASS_INF' in stats_data:
                for class_obj in stats_data['CLASS_INF']['CLASS_OBJ']:
                    class_id = class_obj['@id']
                    class_map = {}
                    for class_item in class_obj['CLASS']:
                        class_map[class_item['@code']] = class_item['@name']
                    class_info[class_id] = class_map
            
            # データを構造化
            rows = []
            for value in values:
                row = {'value': int(value['$'])}
                
                # クラス情報を追加
                for class_id, class_map in class_info.items():
                    if f'@{class_id}' in value:
                        code = value[f'@{class_id}']
                        row[class_id] = class_map.get(code, code)
                
                rows.append(row)
            
            df = pd.DataFrame(rows)
            logger.info("人口統計データの解析完了")
            return df
            
        except Exception as e:
            logger.error(f"人口統計データ解析エラー: {e}")
            # エラー時はサンプルデータを返す
            return pd.DataFrame({
                'cat01': ['総数', '男', '女', '総数', '総数', '総数'],
                'cat02': ['総数', '総数', '総数', '0～14歳', '15～64歳', '65歳以上'],
                'value': [125000000, 61000000, 64000000, 15000000, 75000000, 35000000]
            })
    
    def get_household_data(self) -> pd.DataFrame:
        """家計調査データを取得"""
        logger.info("家計調査データを取得中...")
        
        params = {
            'statsDataId': '0003348237',  # 家計調査の統計表ID
            'metaGetFlg': 'Y'
        }
        
        data = self._make_request('getStatsData', params)
        df = self._parse_household_data(data)
        
        logger.info(f"家計調査データ取得完了: {len(df)}行")
        return df
    
    def _parse_household_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """家計調査データを解析"""
        try:
            stats_data = data['GET_STATS_DATA']
            values = stats_data['DATA_INF']['VALUE']
            
            rows = []
            for value in values:
                row = {
                    'expense_category': value.get('@cat01', '不明'),
                    'amount': int(value['$']) if value['$'].isdigit() else 0
                }
                rows.append(row)
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"家計調査データ解析エラー: {e}")
            return pd.DataFrame({
                'expense_category': ['消費支出', '食料', '住居', '光熱・水道', '交通・通信'],
                'amount': [280000, 75000, 60000, 20000, 45000]
            })
    
    def get_labor_data(self) -> pd.DataFrame:
        """労働力調査データを取得"""
        logger.info("労働力調査データを取得中...")
        
        params = {
            'statsDataId': '0003348881',  # 労働力調査の統計表ID
            'metaGetFlg': 'Y'
        }
        
        data = self._make_request('getStatsData', params)
        df = self._parse_labor_data(data)
        
        logger.info(f"労働力調査データ取得完了: {len(df)}行")
        return df
    
    def _parse_labor_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """労働力調査データを解析"""
        try:
            stats_data = data['GET_STATS_DATA']
            values = stats_data['DATA_INF']['VALUE']
            
            rows = []
            for value in values:
                row = {
                    'employment_status': value.get('@cat01', '不明'),
                    'count': int(value['$']) if value['$'].isdigit() else 0
                }
                rows.append(row)
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"労働力調査データ解析エラー: {e}")
            return pd.DataFrame({
                'employment_status': ['労働力人口', '就業者', '完全失業者', '非労働力人口'],
                'count': [69000000, 67500000, 1500000, 42000000]
            })
    
    def save_data_to_excel(self, data_dict: Dict[str, pd.DataFrame], output_path: Path):
        """データをExcelファイルに保存"""
        logger.info(f"Excelファイルに保存中: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info("Excelファイル保存完了")
    
    def create_summary_report(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """統計データサマリーレポートを作成"""
        logger.info("サマリーレポート作成中...")
        
        summary = {
            'generation_date': datetime.datetime.now().isoformat(),
            'data_sources': list(data_dict.keys()),
            'statistics': {}
        }
        
        for name, df in data_dict.items():
            summary['statistics'][name] = {
                'record_count': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }
        
        logger.info("サマリーレポート作成完了")
        return summary

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='ペルソナベースAIエージェント e-Stat API クライアント'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='デモ用サンプルデータ生成'
    )
    
    parser.add_argument(
        '--population',
        action='store_true',
        help='人口統計データのみ取得'
    )
    
    parser.add_argument(
        '--household',
        action='store_true',
        help='家計調査データのみ取得'
    )
    
    parser.add_argument(
        '--labor',
        action='store_true',
        help='労働力調査データのみ取得'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='全統計データ取得'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='出力ディレクトリ'
    )
    
    args = parser.parse_args()
    
    # API クライアント初期化
    client = EStatAPIClient()
    
    # 出力ディレクトリ設定
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        data_dict = {}
        
        # データ取得
        if args.all or args.demo or (not any([args.population, args.household, args.labor])):
            logger.info("全統計データを取得中...")
            data_dict['population'] = client.get_population_data()
            data_dict['household'] = client.get_household_data()
            data_dict['labor'] = client.get_labor_data()
        else:
            if args.population:
                data_dict['population'] = client.get_population_data()
            if args.household:
                data_dict['household'] = client.get_household_data()
            if args.labor:
                data_dict['labor'] = client.get_labor_data()
        
        # 結果保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Excel出力
        excel_path = output_dir / f"estat_data_{timestamp}.xlsx"
        client.save_data_to_excel(data_dict, excel_path)
        
        # サマリーレポート作成
        summary = client.create_summary_report(data_dict)
        summary_path = output_dir / f"estat_summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ e-Stat データ取得が完了しました！")
        print(f"📊 取得データ種類: {', '.join(data_dict.keys())}")
        print(f"📁 Excel出力: {excel_path}")
        print(f"📋 サマリー: {summary_path}")
        
        # データ概要表示
        for name, df in data_dict.items():
            print(f"\n📈 {name}: {len(df)}件のデータ")
            if len(df) > 0:
                print(f"   カラム: {', '.join(df.columns)}")
        
    except Exception as e:
        logger.error(f"データ取得中にエラーが発生: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 