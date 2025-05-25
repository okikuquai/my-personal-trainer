#!/usr/bin/env python3
"""
Google Fit API OAuth設定ヘルパー
初回認証でリフレッシュトークンを取得するためのスクリプト
"""
import requests
import json
from urllib.parse import urlencode


def print_setup_instructions():
    """セットアップ手順を表示"""
    print("=== Google Fit API OAuth設定ガイド ===")
    print()
    print("1. Google Cloud Consoleでの設定:")
    print("   - https://console.developers.google.com/ にアクセス")
    print("   - プロジェクトを作成または選択")
    print("   - Fitness API を有効化")
    print("   - OAuth 2.0 クライアントIDを作成（Webアプリケーション）")
    print("   - 承認済みリダイレクトURIに以下を追加:")
    print("     https://developers.google.com/oauthplayground")
    print()
    print("2. OAuth Playgroundでの認証:")
    print("   - https://developers.google.com/oauthplayground にアクセス")
    print("   - 右上の歯車アイコンから 'Use your own OAuth credentials' にチェック")
    print("   - OAuth Client ID と OAuth Client Secret を入力")
    print("   - 左側で 'Fitness v1' を選択し、必要なスコープにチェック:")
    print("     ✓ https://www.googleapis.com/auth/fitness.activity.read")
    print("     ✓ https://www.googleapis.com/auth/fitness.body.read")
    print("   - 'Authorize APIs' をクリック")
    print("   - Googleアカウントでログインし、権限を許可")
    print("   - 'Exchange authorization code for tokens' をクリック")
    print("   - 'Refresh token' をコピー")
    print()
    print("3. GitHub Secretsの設定:")
    print("   リポジトリの Settings > Secrets and variables > Actions で以下を設定:")
    print("   - GOOGLE_OAUTH_CLIENT_ID: OAuth クライアントID")
    print("   - GOOGLE_OAUTH_CLIENT_SECRET: OAuth クライアントシークレット")
    print("   - GOOGLE_REFRESH_TOKEN: リフレッシュトークン")
    print()


def generate_auth_url():
    """認証URLを生成（参考用）"""
    print("=== 認証URL生成（参考） ===")
    print("注意: 実際の認証にはOAuth Playgroundを使用することを推奨します")
    print()
    
    client_id = input("OAuth Client ID を入力してください: ").strip()
    
    if not client_id:
        print("Client IDが入力されませんでした")
        return
    
    # 認証URL生成
    params = {
        'client_id': client_id,
        'redirect_uri': 'https://developers.google.com/oauthplayground',
        'scope': 'https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.body.read',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    print(f"認証URL: {auth_url}")
    print()
    print("この URL にアクセスして認証を完了してください")


def test_credentials():
    """認証情報をテスト"""
    print("=== 認証情報テスト ===")
    print("GitHub Secretsに設定した値をテストします")
    print()
    
    client_id = input("OAuth Client ID: ").strip()
    client_secret = input("OAuth Client Secret: ").strip()
    refresh_token = input("Refresh Token: ").strip()
    
    if not all([client_id, client_secret, refresh_token]):
        print("すべての値を入力してください")
        return
    
    # アクセストークンを取得してテスト
    url = "https://oauth2.googleapis.com/token"
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            print("✅ アクセストークンの取得に成功しました！")
            
            # Google Fit APIをテスト
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            test_url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"
            test_response = requests.get(test_url, headers=headers)
            
            if test_response.status_code == 200:
                print("✅ Google Fit APIへのアクセスに成功しました！")
                print("設定が正しく完了しています。")
            else:
                print(f"❌ Google Fit APIのテストに失敗: {test_response.status_code}")
                print(f"エラー内容: {test_response.text}")
        else:
            print("❌ アクセストークンが取得できませんでした")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 認証エラー: {e}")


def main():
    """メイン処理"""
    print("Google Fit API OAuth設定ヘルパー")
    print("=" * 40)
    
    while True:
        print("\n選択してください:")
        print("1. セットアップ手順を表示")
        print("2. 認証URL生成（参考）")
        print("3. 認証情報をテスト")
        print("4. 終了")
        
        choice = input("\n番号を入力: ").strip()
        
        if choice == "1":
            print_setup_instructions()
        elif choice == "2":
            generate_auth_url()
        elif choice == "3":
            test_credentials()
        elif choice == "4":
            print("終了します")
            break
        else:
            print("無効な選択です")


if __name__ == "__main__":
    main() 
