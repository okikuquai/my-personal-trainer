# Fitness Tracker with Google Fit API

Google Fit APIを活用した自動フィットネスデータ収集システムなのだ！  
GitHub Actionsで毎日のアクティビティデータと体重データを自動的に収集・保存するのだ。

## 🚨 重要な情報

**Google Fit REST API は2026年に非推奨になる予定なのだ！**
- 2024年5月1日以降、新規デベロッパーは登録できません
- 将来的には[Health Connect](https://developer.android.com/health-and-fitness/guides/health-connect)への移行を推奨

## 📊 機能

- **日別アクティビティデータ収集**: 歩数、距離、カロリー消費量など
- **体重データ追跡**: 日別の体重記録
- **自動化**: GitHub Actionsによる毎日の自動実行
- **データ保存**: JSON形式でのデータ蓄積
- **履歴管理**: Gitによるデータ変更履歴の追跡

## 📁 プロジェクト構造

```
fitness-trainer/
├── activity/           # アクティビティデータ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別アクティビティデータ
├── weight/             # 体重データ保存ディレクトリ
│   └── YYYY-MM-DD.json # 日別体重データ
├── .github/
│   └── workflows/      # GitHub Actions ワークフロー
├── scripts/            # データ収集スクリプト
└── README.md
```

## 🛠️ セットアップ

### 1. Google Cloud Consoleでの設定

1. [Google API Console](https://console.developers.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. Fitness APIを有効化
4. OAuth 2.0クライアントIDを作成
5. サービスアカウントキーを生成

### 2. GitHub Secretsの設定

以下のシークレットをGitHubリポジトリに設定してください：

```
GOOGLE_OAUTH_CLIENT_ID      # OAuth クライアントID
GOOGLE_OAUTH_CLIENT_SECRET  # OAuth クライアントシークレット
GOOGLE_REFRESH_TOKEN        # リフレッシュトークン
```

### 3. 初回認証

OAuth認証を行い、リフレッシュトークンを取得する必要があります。

## 📈 データ形式

### アクティビティデータ形式 (activity/YYYY-MM-DD.json)
```json
{
  "date": "2024-01-01",
  "steps": 10000,
  "distance": 8.5,
  "calories": 420,
  "active_minutes": 85,
  "created_at": "2024-01-01T23:59:59Z"
}
```

### 体重データ形式 (weight/YYYY-MM-DD.json)
```json
{
  "date": "2024-01-01",
  "weight": 70.5,
  "unit": "kg",
  "created_at": "2024-01-01T23:59:59Z"
}
```

## 🤖 GitHub Actions

毎日午前0時（JST）に自動実行され、前日のデータを収集・保存します。

## 🔧 スクリプト

- `scripts/fetch_activity.py`: アクティビティデータ取得
- `scripts/fetch_weight.py`: 体重データ取得
- `scripts/auth.py`: OAuth認証処理

## 📝 ライセンス

MIT License

## 🚀 今後の展望

Google Fit API非推奨に備え、以下への移行を検討中：
- [Health Connect for Android](https://developer.android.com/health-and-fitness/guides/health-connect)
- Apple HealthKit (iOS)
- その他のフィットネスAPI

---

**Note**: このプロジェクトは教育・個人利用目的で作成されています。商用利用の場合は、各APIの利用規約を確認してください。
