"""
Google Fit API OAuth認証ヘルパー
"""
import os
import requests
import json
from typing import Optional


class GoogleFitAuth:
    """Google Fit API認証クラス"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        self.refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("必要な環境変数が設定されていません")
    
    def get_access_token(self) -> Optional[str]:
        """
        リフレッシュトークンを使用してアクセストークンを取得
        
        Returns:
            str: アクセストークン、取得に失敗した場合はNone
        """
        url = "https://oauth2.googleapis.com/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            print(f"アクセストークン取得エラー: {e}")
            return None
    
    def get_auth_headers(self) -> Optional[dict]:
        """
        認証ヘッダーを取得
        
        Returns:
            dict: 認証ヘッダー、取得に失敗した場合はNone
        """
        access_token = self.get_access_token()
        
        if not access_token:
            return None
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


def get_authenticated_session() -> Optional[tuple]:
    """
    認証済みセッションとヘッダーを取得
    
    Returns:
        tuple: (requests.Session, headers) または None
    """
    auth = GoogleFitAuth()
    headers = auth.get_auth_headers()
    
    if not headers:
        return None
    
    session = requests.Session()
    session.headers.update(headers)
    
    return session, headers 
