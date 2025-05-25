# Fitness Tracker with Android Health Connect

Android Health Connectを活用した健康・フィットネスデータ管理システムなのだ！  
Android Health Connectプラットフォームを使って、安全で一元管理されたヘルスデータの収集・管理を行うのだ。

## 🎯 このリポジトリについて 

このシステムを最大限活用するための前提条件なのだ：

### 📱 フィットネスアプリでの日々の記録
- **Health Connect対応アプリ**で日々のアクティビティを記録してください
  - 歩数、距離、カロリー消費量
  - 体重、体脂肪率の測定
  - 睡眠時間と睡眠の質
  - 食事・栄養の記録
- **推奨アプリ**: Google Fit、Samsung Health、Fitbit、MyFitnessPal など

### 🤖 AI パーソナルトレーナー（Cursor）
- **Cursor（AI）がパーソナルトレーナー**となり、あなたの健康管理をサポートします
- 収集されたデータを基に、個別のアドバイスを提供
- 健康目標の設定と進捗管理をお手伝い
- 継続的なモチベーション向上のためのコーチング

## 🌟 Android Health Connectとは

[Android Health Connect](https://developer.android.com/health-and-fitness/guides/health-connect?hl=ja)は、Androidデバイス上でヘルスとフィットネスのデータを安全に保存・共有するためのプラットフォームなのだ。

### 主な特徴
- **一元管理**: 複数のアプリからのヘルスデータを統合
- **プライバシー重視**: ユーザーが完全にコントロール
- **標準化**: 一貫したデータ形式とAPI
- **Google Fit後継**: Google Fit APIの次世代プラットフォーム

## 📊 機能

- **アクティビティデータ管理**: 歩数、距離、カロリー、心拍数など
- **体重・身体データ追跡**: 体重、体脂肪率、BMIなど
- **睡眠データ**: 睡眠時間、睡眠の質の分析
- **栄養データ**: カロリー摂取量、栄養素の記録
- **データ同期**: 複数デバイス間でのデータ同期

## 📁 プロジェクト構造

```
fitness-trainer/
├── activity/           # アクティビティデータ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別アクティビティデータ
├── weight/             # 体重データ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別体重データ
├── sleep/              # 睡眠データ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別睡眠データ
├── nutrition/          # 栄養データ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別栄養データ
├── .github/
│   └── workflows/      # GitHub Actions ワークフロー
├── scripts/            # データ収集スクリプト
│   ├── health_connect_client.py  # Health Connect クライアント
│   ├── fetch_activity.py         # アクティビティデータ取得
│   ├── fetch_weight.py           # 体重データ取得
│   └── auth.py                   # 認証処理
└── README.md
```

## 🛠️ セットアップ

### 1. Android Health Connect SDK の設定

```gradle
dependencies {
    implementation "androidx.health.connect:connect-client:1.1.0-alpha07"
}
```

### 2. Permissions の設定

`AndroidManifest.xml` に必要な権限を追加：

```xml
<uses-permission android:name="android.permission.health.READ_STEPS" />
<uses-permission android:name="android.permission.health.WRITE_STEPS" />
<uses-permission android:name="android.permission.health.READ_DISTANCE" />
<uses-permission android:name="android.permission.health.READ_TOTAL_CALORIES_BURNED" />
<uses-permission android:name="android.permission.health.READ_WEIGHT" />
<uses-permission android:name="android.permission.health.WRITE_WEIGHT" />
```

### 3. Health Connect クライアントの初期化

```kotlin
private val healthConnectClient by lazy { HealthConnectClient.getOrCreate(context) }
```

## 📈 サポートされるデータ型

### 基本データ型
- **Steps**: 歩数データ
- **Distance**: 移動距離
- **TotalCaloriesBurned**: 消費カロリー
- **ActiveCaloriesBurned**: アクティブカロリー
- **Heart Rate**: 心拍数
- **Weight**: 体重
- **Height**: 身長
- **Sleep**: 睡眠データ

### 高度なデータ型
- **Exercise Session**: ワークアウトセッション
- **Nutrition**: 栄養データ
- **Hydration**: 水分摂取量
- **Body Fat**: 体脂肪率
- **Blood Pressure**: 血圧

## 📊 データ形式例

### アクティビティデータ (activity/YYYY-MM-DD.json)
```json
{
  "date": "2024-01-01",
  "steps": 10000,
  "distance_meters": 8500,
  "active_calories": 420,
  "total_calories": 2100,
  "heart_rate": {
    "average": 75,
    "max": 150,
    "min": 60
  },
  "created_at": "2024-01-01T23:59:59Z",
  "data_source": "health_connect"
}
```

### 体重データ (weight/YYYY-MM-DD.json)
```json
{
  "date": "2024-01-01",
  "weight_kg": 70.5,
  "body_fat_percentage": 15.2,
  "muscle_mass_kg": 55.8,
  "created_at": "2024-01-01T23:59:59Z",
  "data_source": "health_connect"
}
```

### 睡眠データ (sleep/YYYY-MM-DD.json)
```json
{
  "date": "2024-01-01",
  "total_sleep_minutes": 480,
  "deep_sleep_minutes": 120,
  "light_sleep_minutes": 300,
  "rem_sleep_minutes": 90,
  "sleep_efficiency": 0.85,
  "bedtime": "23:30:00",
  "wake_time": "07:30:00",
  "created_at": "2024-01-01T23:59:59Z"
}
```

## 🔒 プライバシーとセキュリティ

Health Connectは以下のプライバシー原則に基づいて設計されているのだ：

- **ユーザーコントロール**: すべてのデータアクセスをユーザーが制御
- **透明性**: どのアプリがどのデータにアクセスするかを明確化
- **最小権限**: 必要最小限のデータのみアクセス
- **暗号化**: デバイス上でのデータ暗号化

## 🚀 実装ガイド

### 1. データ読み取り例

```kotlin
suspend fun readStepsData(): List<StepsRecord> {
    val request = ReadRecordsRequest(
        recordType = StepsRecord::class,
        timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
    )
    val response = healthConnectClient.readRecords(request)
    return response.records
}
```

### 2. データ書き込み例

```kotlin
suspend fun insertWeight(weightKg: Double) {
    val weightRecord = WeightRecord(
        weight = Mass.kilograms(weightKg),
        time = Instant.now(),
        zoneOffset = ZoneOffset.systemDefault().rules.getOffset(Instant.now())
    )
    healthConnectClient.insertRecords(listOf(weightRecord))
}
```

## 🤖 GitHub Actions

毎日自動でHealth Connectからデータを収集し、JSONファイルとして保存するワークフローを設定できるのだ。

## 📱 対応プラットフォーム

- **Android 14以降**: ネイティブサポート
- **Android 9-13**: Health Connect アプリ経由
- **Wear OS**: 対応予定

## 🔗 関連リンク

- [Android Health Connect 公式ドキュメント](https://developer.android.com/health-and-fitness/guides/health-connect?hl=ja)
- [Health Connect SDK](https://developer.android.com/jetpack/androidx/releases/health-connect)
- [データ型リファレンス](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/package-summary)
- [Health Connect サンプルアプリ](https://github.com/android/health-samples)

## 📝 ライセンス

MIT License

## 💡 使い方（初心者向け）

### 1. フィットネスアプリをセットアップ
1. **Google Fit**または**Samsung Health**をスマートフォンにインストール
2. アプリを開いて基本情報（身長、体重、年齢）を入力
3. 日々の歩数、運動、食事を記録開始

### 2. AIトレーナー（Cursor）と対話
1. 「今日の調子はどうですか？」と聞いてみてください
2. 健康に関する質問や悩みを相談
3. データを基にしたパーソナライズされたアドバイスを受け取り

### 3. 継続的な健康管理
- **毎日**: アプリでの記録（自動化されている部分もあります）
- **週1回**: Cursorとの健康チェックインセッション
- **月1回**: 長期的な傾向分析とゴール調整

## 🚀 今後の展望

- **より多くのデータ型サポート**: 新しいヘルスメトリクスの追加
- **AI分析機能**: ヘルスデータの傾向分析とパーソナライズ強化
- **ウェアラブル統合**: より多くのデバイスとの連携
- **コミュニティ機能**: ヘルスデータの共有機能
- **音声インターフェース**: 音声でのヘルスコーチング

---

**Note**: このプロジェクトはAndroid Health Connectを活用した個人のヘルスデータ管理を目的としています。医療アドバイスの提供は行いません。健康に関する重要な判断は、必ず医療専門家にご相談ください。
