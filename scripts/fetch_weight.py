#!/usr/bin/env python3
"""
Android Health Connectから体重データを取得して保存するのだ！

現在はモックアップ実装だが、将来的には実際のHealth Connect APIを使用するのだ。
"""
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from health_connect_client import create_health_connect_client, WeightRecord


# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_yesterday_date():
    """昨日の日付を取得するのだ"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def get_time_range():
    """昨日の開始・終了時刻を取得するのだ"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_time, end_time


def fetch_weight_data_from_health_connect(client, start_time, end_time):
    """
    Health Connectから体重データを取得するのだ
    
    Args:
        client: Health Connectクライアント
        start_time: 開始日時
        end_time: 終了日時
        
    Returns:
        体重データの辞書
    """
    logger.info(f"Health Connectから体重データを取得中... ({start_time} - {end_time})")
    
    weight_data = {
        "weight_kg": 0.0,
        "body_fat_percentage": None,
        "muscle_mass_kg": None,
        "bmi": None
    }
    
    try:
        # 体重データを取得
        weight_records = client.read_weight_data(start_time, end_time)
        
        if weight_records:
            # 最新のレコードを使用（複数回測定された場合）
            latest_record = weight_records[-1]
            
            weight_data["weight_kg"] = latest_record.weight_kg
            weight_data["body_fat_percentage"] = latest_record.body_fat_percentage
            weight_data["muscle_mass_kg"] = latest_record.muscle_mass_kg
            
            # BMIを計算（身長は仮定値: 170cm）
            if weight_data["weight_kg"] > 0:
                height_m = 1.70  # 実際のアプリでは設定値を使用
                weight_data["bmi"] = round(weight_data["weight_kg"] / (height_m ** 2), 1)
            
            logger.info(f"体重データ取得完了: {weight_data['weight_kg']}kg")
            if weight_data["body_fat_percentage"]:
                logger.info(f"体脂肪率: {weight_data['body_fat_percentage']}%")
            if weight_data["bmi"]:
                logger.info(f"BMI: {weight_data['bmi']}")
        
        else:
            logger.warning("体重データが見つからなかったのだ")
            
    except Exception as e:
        logger.error(f"Health Connectからの体重データ取得中にエラーが発生したのだ: {e}")
        
    return weight_data


def save_weight_data(date_str, weight_data):
    """
    体重データをJSONファイルに保存するのだ
    
    Args:
        date_str: 日付文字列
        weight_data: 体重データ
        
    Returns:
        保存したファイルパス
    """
    # weightディレクトリが存在しない場合は作成
    weight_dir = Path('weight')
    weight_dir.mkdir(exist_ok=True)
    
    # ファイルパス
    file_path = weight_dir / f"{date_str}.json"
    
    # 保存するデータ（Health Connect形式）
    data_to_save = {
        "date": date_str,
        "weight_kg": weight_data['weight_kg'],
        "body_fat_percentage": weight_data['body_fat_percentage'],
        "muscle_mass_kg": weight_data['muscle_mass_kg'],
        "bmi": weight_data['bmi'],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "health_connect"
    }
    
    # JSONファイルに保存
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"体重データを保存したのだ: {file_path}")
        logger.info(f"データ内容: {data_to_save}")
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"ファイル保存中にエラーが発生したのだ: {e}")
        return None


def validate_health_connect_permissions(client):
    """
    Health Connectの権限を確認するのだ
    
    Args:
        client: Health Connectクライアント
        
    Returns:
        権限が正常かどうか
    """
    required_permissions = [
        "READ_WEIGHT",
        "READ_BODY_FAT",
        "READ_HEIGHT"
    ]
    
    permissions = client.check_permissions(required_permissions)
    
    missing_permissions = [perm for perm, granted in permissions.items() if not granted]
    
    if missing_permissions:
        logger.warning(f"以下の権限が不足しているのだ: {missing_permissions}")
        return False
    
    logger.info("Health Connectの体重データ権限確認完了なのだ")
    return True


def insert_sample_weight_data(client, weight_kg, body_fat_percentage=None):
    """
    サンプルの体重データをHealth Connectに挿入するのだ（テスト用）
    
    Args:
        client: Health Connectクライアント
        weight_kg: 体重（kg）
        body_fat_percentage: 体脂肪率（%、オプション）
        
    Returns:
        成功したかどうか
    """
    try:
        success = client.insert_weight_record(weight_kg, body_fat_percentage)
        if success:
            logger.info(f"サンプル体重データを挿入したのだ: {weight_kg}kg")
        return success
    except Exception as e:
        logger.error(f"サンプルデータ挿入中にエラーが発生したのだ: {e}")
        return False


def main():
    """メイン処理なのだ"""
    logger.info("=== Health Connect 体重データ取得開始 ===")
    
    try:
        # Health Connectクライアントを作成（現在はモックモード）
        client = create_health_connect_client(mock_mode=True)
        
        # 権限を確認
        if not validate_health_connect_permissions(client):
            logger.error("Health Connectの権限が不足しているのだ")
            return False
        
        # 昨日の日付と時間範囲を取得
        date_str = get_yesterday_date()
        start_time, end_time = get_time_range()
        
        logger.info(f"取得対象日: {date_str}")
        logger.info(f"時間範囲: {start_time} - {end_time}")
        
        # Health Connectから体重データを取得
        weight_data = fetch_weight_data_from_health_connect(client, start_time, end_time)
        
        if not weight_data or weight_data['weight_kg'] == 0.0:
            logger.warning("有効な体重データが取得できなかったのだ")
            # モックモードの場合、ダミーデータを生成
            if client.mock_mode:
                import random
                weight_data = {
                    "weight_kg": round(random.uniform(60.0, 80.0), 1),
                    "body_fat_percentage": round(random.uniform(10.0, 25.0), 1),
                    "muscle_mass_kg": round(random.uniform(45.0, 60.0), 1),
                    "bmi": None
                }
                # BMIを計算
                height_m = 1.70
                weight_data["bmi"] = round(weight_data["weight_kg"] / (height_m ** 2), 1)
                logger.info("モックデータを生成したのだ")
        
        # ファイルに保存
        saved_file = save_weight_data(date_str, weight_data)
        
        if saved_file:
            logger.info("=== 体重データ取得完了 ===")
            return True
        else:
            logger.error("データ保存に失敗したのだ")
            return False
            
    except Exception as e:
        logger.error(f"処理中に予期しないエラーが発生したのだ: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
