# Fitness Tracker with Android Health Connect

An advanced health and fitness data management system powered by Android Health Connect!  
This system provides secure, centralized health data collection and management through the Android Health Connect platform.

## 🎯 Prerequisites

Prerequisites to maximize the benefits of this system:

### 📱 Daily Recording with Fitness Apps
- Record your daily activities using **Health Connect compatible apps**
  - Steps, distance, calories burned
  - Weight and body fat percentage measurements  
  - Sleep duration and sleep quality
  - Meal and nutrition logging
- **Recommended Apps**: Google Fit, Samsung Health, Fitbit, MyFitnessPal, etc.

### 🤖 AI Personal Trainer (Cursor)
- **Cursor (AI) serves as your personal trainer** to support your health management
- Provides personalized advice based on collected data
- Assists with health goal setting and progress tracking
- Offers continuous motivational coaching

## 🌟 What is Android Health Connect?

[Android Health Connect](https://developer.android.com/health-and-fitness/guides/health-connect) is a platform for securely storing and sharing health and fitness data on Android devices.

### Key Features
- **Centralized Management**: Integrates health data from multiple apps
- **Privacy-Focused**: Complete user control over data
- **Standardization**: Consistent data formats and APIs
- **Google Fit Successor**: Next-generation platform replacing Google Fit API

## 📊 Features

- **Activity Data Management**: Steps, distance, calories, heart rate, etc.
- **Weight & Body Data Tracking**: Weight, body fat percentage, BMI, etc.
- **Sleep Data**: Sleep duration and quality analysis
- **Nutrition Data**: Calorie intake and nutrient tracking
- **Data Synchronization**: Multi-device data sync

## 📁 Project Structure

```
fitness-trainer/
├── activity/           # Activity data storage directory
│   └── YYYY-MM-DD.json # Daily activity data
├── weight/             # Weight data storage directory
│   └── YYYY-MM-DD.json # Daily weight data
├── sleep/              # Sleep data storage directory
│   └── YYYY-MM-DD.json # Daily sleep data
├── nutrition/          # Nutrition data storage directory
│   └── YYYY-MM-DD.json # Daily nutrition data
├── .github/
│   └── workflows/      # GitHub Actions workflows
├── scripts/            # Data collection scripts
│   ├── health_connect_client.py  # Health Connect client
│   ├── fetch_activity.py         # Activity data fetching
│   ├── fetch_weight.py           # Weight data fetching
│   ├── fetch_sleep.py            # Sleep data fetching
│   ├── fetch_nutrition.py        # Nutrition data fetching
│   └── auth.py                   # Authentication handling
└── README.md
```

## 🛠️ Setup

### 1. Android Health Connect SDK Configuration

```gradle
dependencies {
    implementation "androidx.health.connect:connect-client:1.1.0-alpha07"
}
```

### 2. Permissions Configuration

Add required permissions to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.health.READ_STEPS" />
<uses-permission android:name="android.permission.health.WRITE_STEPS" />
<uses-permission android:name="android.permission.health.READ_DISTANCE" />
<uses-permission android:name="android.permission.health.READ_TOTAL_CALORIES_BURNED" />
<uses-permission android:name="android.permission.health.READ_WEIGHT" />
<uses-permission android:name="android.permission.health.WRITE_WEIGHT" />
```

### 3. Health Connect Client Initialization

```kotlin
private val healthConnectClient by lazy { HealthConnectClient.getOrCreate(context) }
```

## 📈 Supported Data Types

### Basic Data Types
- **Steps**: Step count data
- **Distance**: Distance traveled
- **TotalCaloriesBurned**: Total calories burned
- **ActiveCaloriesBurned**: Active calories burned
- **Heart Rate**: Heart rate data
- **Weight**: Body weight
- **Height**: Body height
- **Sleep**: Sleep data

### Advanced Data Types
- **Exercise Session**: Workout sessions
- **Nutrition**: Nutritional data
- **Hydration**: Water intake
- **Body Fat**: Body fat percentage
- **Blood Pressure**: Blood pressure readings

## 📊 Data Format Examples

### Activity Data (activity/YYYY-MM-DD.json)
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

### Weight Data (weight/YYYY-MM-DD.json)
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

### Sleep Data (sleep/YYYY-MM-DD.json)
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

## 🔒 Privacy and Security

Health Connect is designed based on the following privacy principles:

- **User Control**: Users have complete control over all data access
- **Transparency**: Clear visibility of which apps access what data
- **Minimal Permissions**: Access only to necessary data
- **Encryption**: On-device data encryption

## 🚀 Implementation Guide

### 1. Data Reading Example

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

### 2. Data Writing Example

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

Automated workflows can be configured to collect data from Health Connect daily and save as JSON files.

## 📱 Supported Platforms

- **Android 14+**: Native support
- **Android 9-13**: Via Health Connect app
- **Wear OS**: Support planned

## 🔗 Related Links

- [Android Health Connect Official Documentation](https://developer.android.com/health-and-fitness/guides/health-connect)
- [Health Connect SDK](https://developer.android.com/jetpack/androidx/releases/health-connect)
- [Data Types Reference](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/package-summary)
- [Health Connect Sample Apps](https://github.com/android/health-samples)

## 💡 Getting Started (Beginner's Guide)

### 1. Set Up Fitness Apps
1. Install **Google Fit** or **Samsung Health** on your smartphone
2. Open the app and enter basic information (height, weight, age)
3. Start recording daily steps, exercise, and meals

### 2. Interact with AI Trainer (Cursor)
1. Ask "How are you feeling today?"
2. Consult about health-related questions or concerns
3. Receive personalized advice based on your data

### 3. Continuous Health Management
- **Daily**: App recording (some parts are automated)
- **Weekly**: Health check-in sessions with Cursor
- **Monthly**: Long-term trend analysis and goal adjustment

## 📝 License

MIT License

## 🚀 Future Roadmap

- **More Data Type Support**: Addition of new health metrics
- **AI Analysis Features**: Enhanced health data trend analysis and personalization
- **Wearable Integration**: Connection with more devices
- **Community Features**: Health data sharing capabilities
- **Voice Interface**: Voice-based health coaching

---

**Note**: This project is designed for personal health data management using Android Health Connect. It does not provide medical advice. Always consult healthcare professionals for important health decisions. 
