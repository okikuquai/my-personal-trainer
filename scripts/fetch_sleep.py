#!/usr/bin/env python3
"""
Android Health Connectから睡眠データを取得して保存するのだ！

現在はモックアップ実装だが、将来的には実際のHealth Connect APIを使用するのだ。
"""
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from health_connect_client import create_health_connect_client, SleepRecord


# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_yesterday_date():
    """昨日の日付を取得するのだ"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def get_time_range():
    """昨日の開始・終了時刻を取得するのだ（睡眠は前日夜〜当日朝）"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    # 睡眠データは前日18時〜当日12時の範囲で取得
    start_time = yesterday.replace(hour=18, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999) + timedelta(hours=12)
    
    return start_time, end_time


def fetch_sleep_data_from_health_connect(client, start_time, end_time):
    """
    Health Connectから睡眠データを取得するのだ
    
    Args:
        client: Health Connectクライアント
        start_time: 開始日時
        end_time: 終了日時
        
    Returns:
        睡眠データの辞書
    """
    logger.info(f"Health Connectから睡眠データを取得中... ({start_time} - {end_time})")
    
    sleep_data = {
        "total_sleep_minutes": 0,
        "deep_sleep_minutes": None,
        "light_sleep_minutes": None,
        "rem_sleep_minutes": None,
        "sleep_efficiency": None,
        "bedtime": None,
        "wake_time": None,
        "sleep_quality_score": None
    }
    
    try:
        # 睡眠データを取得
        sleep_records = client.read_sleep_data(start_time, end_time)
        
        if sleep_records:
            # 最新のレコードを使用（通常は1日1回）
            latest_record = sleep_records[-1]
            
            sleep_data["total_sleep_minutes"] = latest_record.total_sleep_minutes
            sleep_data["deep_sleep_minutes"] = latest_record.deep_sleep_minutes
            sleep_data["light_sleep_minutes"] = latest_record.light_sleep_minutes
            sleep_data["rem_sleep_minutes"] = latest_record.rem_sleep_minutes
            sleep_data["sleep_efficiency"] = latest_record.sleep_efficiency
            sleep_data["bedtime"] = latest_record.bedtime
            sleep_data["wake_time"] = latest_record.wake_time
            
            # 睡眠の質スコアを計算（効率とREM睡眠の割合から）
            if sleep_data["sleep_efficiency"] and sleep_data["rem_sleep_minutes"]:
                rem_ratio = sleep_data["rem_sleep_minutes"] / sleep_data["total_sleep_minutes"]
                sleep_data["sleep_quality_score"] = round(
                    (sleep_data["sleep_efficiency"] * 0.7 + rem_ratio * 0.3) * 100, 1
                )
            
            logger.info(f"睡眠データ取得完了: {sleep_data['total_sleep_minutes']}分")
            logger.info(f"睡眠効率: {sleep_data['sleep_efficiency']}")
            if sleep_data["sleep_quality_score"]:
                logger.info(f"睡眠の質スコア: {sleep_data['sleep_quality_score']}")
        
        else:
            logger.warning("睡眠データが見つからなかったのだ")
            
    except Exception as e:
        logger.error(f"Health Connectからの睡眠データ取得中にエラーが発生したのだ: {e}")
        
    return sleep_data


def save_sleep_data(date_str, sleep_data):
    """
    睡眠データをJSONファイルに保存するのだ
    
    Args:
        date_str: 日付文字列
        sleep_data: 睡眠データ
        
    Returns:
        保存したファイルパス
    """
    # sleepディレクトリが存在しない場合は作成
    sleep_dir = Path('sleep')
    sleep_dir.mkdir(exist_ok=True)
    
    # ファイルパス
    file_path = sleep_dir / f"{date_str}.json"
    
    # 保存するデータ（Health Connect形式）
    data_to_save = {
        "date": date_str,
        "total_sleep_minutes": sleep_data['total_sleep_minutes'],
        "deep_sleep_minutes": sleep_data['deep_sleep_minutes'],
        "light_sleep_minutes": sleep_data['light_sleep_minutes'],
        "rem_sleep_minutes": sleep_data['rem_sleep_minutes'],
        "sleep_efficiency": sleep_data['sleep_efficiency'],
        "bedtime": sleep_data['bedtime'],
        "wake_time": sleep_data['wake_time'],
        "sleep_quality_score": sleep_data['sleep_quality_score'],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "health_connect"
    }
    
    # JSONファイルに保存
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"睡眠データを保存したのだ: {file_path}")
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
        "READ_SLEEP",
        "READ_SLEEP_STAGES"
    ]
    
    permissions = client.check_permissions(required_permissions)
    
    missing_permissions = [perm for perm, granted in permissions.items() if not granted]
    
    if missing_permissions:
        logger.warning(f"以下の権限が不足しているのだ: {missing_permissions}")
        return False
    
    logger.info("Health Connectの睡眠データ権限確認完了なのだ")
    return True


def analyze_sleep_patterns(sleep_data):
    """
    睡眠パターンを分析するのだ
    
    Args:
        sleep_data: 睡眠データ
        
    Returns:
        分析結果の辞書
    """
    analysis = {
        "sleep_duration_category": "unknown",
        "sleep_quality_category": "unknown",
        "recommendations": []
    }
    
    total_hours = sleep_data['total_sleep_minutes'] / 60 if sleep_data['total_sleep_minutes'] else 0
    
    # 睡眠時間の分類
    if total_hours >= 7 and total_hours <= 9:
        analysis["sleep_duration_category"] = "optimal"
    elif total_hours >= 6 and total_hours < 7:
        analysis["sleep_duration_category"] = "short"
        analysis["recommendations"].append("もう少し長く眠ることをお勧めするのだ")
    elif total_hours > 9:
        analysis["sleep_duration_category"] = "long"
        analysis["recommendations"].append("睡眠時間が長すぎるかもしれないのだ")
    else:
        analysis["sleep_duration_category"] = "insufficient"
        analysis["recommendations"].append("睡眠時間が不足しているのだ")
    
    # 睡眠効率の分析
    if sleep_data['sleep_efficiency']:
        if sleep_data['sleep_efficiency'] >= 0.85:
            analysis["sleep_quality_category"] = "excellent"
        elif sleep_data['sleep_efficiency'] >= 0.75:
            analysis["sleep_quality_category"] = "good"
        else:
            analysis["sleep_quality_category"] = "needs_improvement"
            analysis["recommendations"].append("睡眠の質を改善することをお勧めするのだ")
    
    # REM睡眠の分析
    if sleep_data['rem_sleep_minutes'] and sleep_data['total_sleep_minutes']:
        rem_ratio = sleep_data['rem_sleep_minutes'] / sleep_data['total_sleep_minutes']
        if rem_ratio < 0.15:
            analysis["recommendations"].append("REM睡眠が少ないかもしれないのだ")
    
    return analysis


def main():
    """メイン処理なのだ"""
    logger.info("=== Health Connect 睡眠データ取得開始 ===")
    
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
        
        # Health Connectから睡眠データを取得
        sleep_data = fetch_sleep_data_from_health_connect(client, start_time, end_time)
        
        if not sleep_data or sleep_data['total_sleep_minutes'] == 0:
            logger.warning("有効な睡眠データが取得できなかったのだ")
            # モックモードの場合、ダミーデータを生成
            if client.mock_mode:
                import random
                total_sleep = random.randint(360, 540)  # 6-9時間
                sleep_data = {
                    "total_sleep_minutes": total_sleep,
                    "deep_sleep_minutes": int(total_sleep * 0.2),
                    "light_sleep_minutes": int(total_sleep * 0.6),
                    "rem_sleep_minutes": int(total_sleep * 0.2),
                    "sleep_efficiency": round(random.uniform(0.75, 0.95), 2),
                    "bedtime": "23:30:00",
                    "wake_time": "07:30:00",
                    "sleep_quality_score": None
                }
                # 睡眠の質スコアを計算
                rem_ratio = sleep_data["rem_sleep_minutes"] / sleep_data["total_sleep_minutes"]
                sleep_data["sleep_quality_score"] = round(
                    (sleep_data["sleep_efficiency"] * 0.7 + rem_ratio * 0.3) * 100, 1
                )
                logger.info("モック睡眠データを生成したのだ")
        
        # 睡眠パターンを分析
        analysis = analyze_sleep_patterns(sleep_data)
        logger.info(f"睡眠分析結果: {analysis}")
        
        # ファイルに保存
        saved_file = save_sleep_data(date_str, sleep_data)
        
        if saved_file:
            logger.info("=== 睡眠データ取得完了 ===")
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
