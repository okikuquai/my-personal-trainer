#!/usr/bin/env python3
"""
Android Health Connectから栄養データを取得して保存するのだ！

現在はモックアップ実装だが、将来的には実際のHealth Connect APIを使用するのだ。
"""
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from health_connect_client import create_health_connect_client, NutritionRecord


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


def fetch_nutrition_data_from_health_connect(client, start_time, end_time):
    """
    Health Connectから栄養データを取得するのだ
    
    Args:
        client: Health Connectクライアント
        start_time: 開始日時
        end_time: 終了日時
        
    Returns:
        栄養データの辞書
    """
    logger.info(f"Health Connectから栄養データを取得中... ({start_time} - {end_time})")
    
    nutrition_data = {
        "calories_consumed": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "sugar_g": 0.0,
        "sodium_mg": 0.0,
        "water_ml": 0.0,
        "meal_breakdown": {
            "breakfast": {"calories": 0, "time": None},
            "lunch": {"calories": 0, "time": None},
            "dinner": {"calories": 0, "time": None},
            "snacks": {"calories": 0, "time": None}
        }
    }
    
    try:
        # 現在はモックモードなので、Health Connectクライアントから直接は取得できない
        # 将来的にはNutritionRecordを取得する実装に変更
        
        if client.mock_mode:
            # モック栄養データを生成
            import random
            
            # 基本的な栄養素データ
            total_calories = random.randint(1800, 2500)
            nutrition_data["calories_consumed"] = float(total_calories)
            
            # タンパク質（カロリーの15-25%）
            protein_calories = total_calories * random.uniform(0.15, 0.25)
            nutrition_data["protein_g"] = round(protein_calories / 4, 1)  # 1g = 4kcal
            
            # 炭水化物（カロリーの45-65%）
            carbs_calories = total_calories * random.uniform(0.45, 0.65)
            nutrition_data["carbs_g"] = round(carbs_calories / 4, 1)  # 1g = 4kcal
            
            # 脂質（カロリーの20-35%）
            fat_calories = total_calories * random.uniform(0.20, 0.35)
            nutrition_data["fat_g"] = round(fat_calories / 9, 1)  # 1g = 9kcal
            
            # その他の栄養素
            nutrition_data["fiber_g"] = round(random.uniform(20, 35), 1)
            nutrition_data["sugar_g"] = round(random.uniform(30, 80), 1)
            nutrition_data["sodium_mg"] = round(random.uniform(1500, 3000), 1)
            nutrition_data["water_ml"] = round(random.uniform(1500, 3000), 1)
            
            # 食事の内訳
            breakfast_ratio = random.uniform(0.20, 0.30)
            lunch_ratio = random.uniform(0.30, 0.40)
            dinner_ratio = random.uniform(0.30, 0.40)
            snacks_ratio = 1.0 - breakfast_ratio - lunch_ratio - dinner_ratio
            
            nutrition_data["meal_breakdown"]["breakfast"]["calories"] = int(total_calories * breakfast_ratio)
            nutrition_data["meal_breakdown"]["lunch"]["calories"] = int(total_calories * lunch_ratio)
            nutrition_data["meal_breakdown"]["dinner"]["calories"] = int(total_calories * dinner_ratio)
            nutrition_data["meal_breakdown"]["snacks"]["calories"] = int(total_calories * snacks_ratio)
            
            # 食事時間を設定
            nutrition_data["meal_breakdown"]["breakfast"]["time"] = "07:30:00"
            nutrition_data["meal_breakdown"]["lunch"]["time"] = "12:00:00"
            nutrition_data["meal_breakdown"]["dinner"]["time"] = "19:00:00"
            nutrition_data["meal_breakdown"]["snacks"]["time"] = "15:00:00"
            
            logger.info(f"栄養データ取得完了: {nutrition_data['calories_consumed']}kcal")
            logger.info(f"タンパク質: {nutrition_data['protein_g']}g, 炭水化物: {nutrition_data['carbs_g']}g, 脂質: {nutrition_data['fat_g']}g")
        
        else:
            # 実際のHealth Connect APIを使用
            # TODO: 実際の栄養データ取得を実装
            logger.warning("実際のHealth Connect APIはまだ実装されていないのだ")
            
    except Exception as e:
        logger.error(f"Health Connectからの栄養データ取得中にエラーが発生したのだ: {e}")
        
    return nutrition_data


def save_nutrition_data(date_str, nutrition_data):
    """
    栄養データをJSONファイルに保存するのだ
    
    Args:
        date_str: 日付文字列
        nutrition_data: 栄養データ
        
    Returns:
        保存したファイルパス
    """
    # nutritionディレクトリが存在しない場合は作成
    nutrition_dir = Path('nutrition')
    nutrition_dir.mkdir(exist_ok=True)
    
    # ファイルパス
    file_path = nutrition_dir / f"{date_str}.json"
    
    # 保存するデータ（Health Connect形式）
    data_to_save = {
        "date": date_str,
        "calories_consumed": nutrition_data['calories_consumed'],
        "protein_g": nutrition_data['protein_g'],
        "carbs_g": nutrition_data['carbs_g'],
        "fat_g": nutrition_data['fat_g'],
        "fiber_g": nutrition_data['fiber_g'],
        "sugar_g": nutrition_data['sugar_g'],
        "sodium_mg": nutrition_data['sodium_mg'],
        "water_ml": nutrition_data['water_ml'],
        "meal_breakdown": nutrition_data['meal_breakdown'],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "health_connect"
    }
    
    # JSONファイルに保存
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"栄養データを保存したのだ: {file_path}")
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
        "READ_NUTRITION",
        "READ_HYDRATION"
    ]
    
    permissions = client.check_permissions(required_permissions)
    
    missing_permissions = [perm for perm, granted in permissions.items() if not granted]
    
    if missing_permissions:
        logger.warning(f"以下の権限が不足しているのだ: {missing_permissions}")
        return False
    
    logger.info("Health Connectの栄養データ権限確認完了なのだ")
    return True


def analyze_nutrition_balance(nutrition_data):
    """
    栄養バランスを分析するのだ
    
    Args:
        nutrition_data: 栄養データ
        
    Returns:
        分析結果の辞書
    """
    analysis = {
        "calorie_balance": "unknown",
        "macronutrient_balance": "unknown",
        "recommendations": [],
        "pfc_ratio": {
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }
    }
    
    total_calories = nutrition_data['calories_consumed']
    
    # カロリーバランスの分析
    if total_calories >= 1800 and total_calories <= 2500:
        analysis["calorie_balance"] = "appropriate"
    elif total_calories < 1800:
        analysis["calorie_balance"] = "low"
        analysis["recommendations"].append("カロリー摂取量が少ないかもしれないのだ")
    else:
        analysis["calorie_balance"] = "high"
        analysis["recommendations"].append("カロリー摂取量が多いかもしれないのだ")
    
    # PFCバランスの計算
    if total_calories > 0:
        protein_ratio = (nutrition_data['protein_g'] * 4) / total_calories
        fat_ratio = (nutrition_data['fat_g'] * 9) / total_calories
        carbs_ratio = (nutrition_data['carbs_g'] * 4) / total_calories
        
        analysis["pfc_ratio"]["protein"] = round(protein_ratio * 100, 1)
        analysis["pfc_ratio"]["fat"] = round(fat_ratio * 100, 1)
        analysis["pfc_ratio"]["carbs"] = round(carbs_ratio * 100, 1)
        
        # 理想的なPFCバランス: P 15-20%, F 20-30%, C 50-65%
        if 15 <= analysis["pfc_ratio"]["protein"] <= 20 and \
           20 <= analysis["pfc_ratio"]["fat"] <= 30 and \
           50 <= analysis["pfc_ratio"]["carbs"] <= 65:
            analysis["macronutrient_balance"] = "excellent"
        else:
            analysis["macronutrient_balance"] = "needs_adjustment"
            
            if analysis["pfc_ratio"]["protein"] < 15:
                analysis["recommendations"].append("タンパク質をもう少し摂ることをお勧めするのだ")
            elif analysis["pfc_ratio"]["protein"] > 20:
                analysis["recommendations"].append("タンパク質の摂取量が多いかもしれないのだ")
                
            if analysis["pfc_ratio"]["fat"] > 30:
                analysis["recommendations"].append("脂質の摂取量を控えめにすることをお勧めするのだ")
            elif analysis["pfc_ratio"]["fat"] < 20:
                analysis["recommendations"].append("良質な脂質をもう少し摂ることをお勧めするのだ")
    
    # 食物繊維の分析
    if nutrition_data['fiber_g'] < 20:
        analysis["recommendations"].append("食物繊維をもっと摂ることをお勧めするのだ")
    
    # 水分摂取の分析
    if nutrition_data['water_ml'] < 1500:
        analysis["recommendations"].append("水分をもっと摂ることをお勧めするのだ")
    
    return analysis


def main():
    """メイン処理なのだ"""
    logger.info("=== Health Connect 栄養データ取得開始 ===")
    
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
        
        # Health Connectから栄養データを取得
        nutrition_data = fetch_nutrition_data_from_health_connect(client, start_time, end_time)
        
        if not nutrition_data or nutrition_data['calories_consumed'] == 0.0:
            logger.warning("有効な栄養データが取得できなかったのだ")
            return False
        
        # 栄養バランスを分析
        analysis = analyze_nutrition_balance(nutrition_data)
        logger.info(f"栄養分析結果: {analysis}")
        
        # ファイルに保存
        saved_file = save_nutrition_data(date_str, nutrition_data)
        
        if saved_file:
            logger.info("=== 栄養データ取得完了 ===")
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
