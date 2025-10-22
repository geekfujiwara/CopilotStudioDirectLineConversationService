#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Line API 会話サービス
応答取得機能を含むフル機能実装
"""

import os
import json
import logging
import time
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectLineConversationService:
    """
    Direct Line APIを使用した会話サービス
    メッセージ送信・応答取得の完全実装
    """
    
    def __init__(self):
        """サービスの初期化"""
        
        # 設定値の取得
        self.endpoint_url = os.getenv('AGENT_ENDPOINT_URL', '')
        self.auth_header_name = os.getenv('CUSTOM_AUTH_HEADER_NAME', 'Authorization')
        self.auth_header_value = os.getenv('CUSTOM_AUTH_HEADER_VALUE', '')
        
        # Direct Line API設定
        self.directline_endpoint = "https://directline.botframework.com/v3/directline"
        
        # トークン管理
        self.current_token = None
        self.token_expires_at = None
        self.conversation_id = None
        
        # 応答取得用
        self.watermark = None  # 応答取得の進行状況を追跡
        
        # セッション
        self.session = requests.Session()
        
        logger.info("Direct Line 会話サービス初期化完了")
        logger.info(f"エンドポイント: {self.endpoint_url}")
        logger.info(f"認証ヘッダー名: {self.auth_header_name}")
        
        # 設定検証
        self._validate_configuration()
    
    def _validate_configuration(self):
        """設定の検証"""
        if not self.endpoint_url:
            raise ValueError("AGENT_ENDPOINT_URL is required")
        if not self.auth_header_value:
            raise ValueError("CUSTOM_AUTH_HEADER_VALUE is required")
        
        logger.info("✅ 設定検証完了")
    
    def generate_direct_line_token(self) -> Dict[str, Any]:
        """Direct Line APIトークンを生成"""
        
        logger.info("Direct Line トークンを生成中...")
        
        # シークレットを抽出（Bearerプレフィックスを除去）
        secret = self.auth_header_value.replace('Bearer ', '')
        
        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        
        token_endpoint = f"{self.directline_endpoint}/tokens/generate"
        
        try:
            response = self.session.post(token_endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.current_token = token_data.get('token')
                # 注意: トークン生成時のconversationIdは使用しない（存在しない場合もある）
                
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
                
                logger.info("Direct Line トークン生成成功")
                logger.info(f"有効期限: {expires_in}秒")
                
                # 会話IDはリセット（新しい会話を開始する必要がある）
                self.conversation_id = None
                self.watermark = None
                
                return {
                    "success": True,
                    "token": self.current_token,
                    "expires_in": expires_in
                }
            else:
                error_msg = f"トークン生成失敗: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"トークン生成エラー: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def ensure_token_available(self) -> bool:
        """トークンが利用可能であることを確認"""
        
        # トークンが存在し、まだ有効か確認
        if (self.current_token and 
            self.token_expires_at and 
            datetime.now(timezone.utc).timestamp() < self.token_expires_at - 300):
            
            remaining = int(self.token_expires_at - datetime.now(timezone.utc).timestamp())
            logger.info(f"✅ 既存トークンを使用 (残り{remaining}秒)")
            return True
        
        # トークンを新規生成（会話IDもリセット）
        logger.info("🔄 新しいトークンを生成...")
        self.conversation_id = None
        self.watermark = None
        
        result = self.generate_direct_line_token()
        return result.get("success", False)
    
    def start_conversation(self) -> Dict[str, Any]:
        """新しい会話を開始"""
        
        if not self.ensure_token_available():
            return {"success": False, "error": "トークンの取得に失敗しました"}
        
        start_conversation_url = f"{self.directline_endpoint}/conversations"
        
        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info("🔄 新しい会話を開始中...")
            response = self.session.post(start_conversation_url, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                conversation_data = response.json()
                new_conversation_id = conversation_data.get('conversationId')
                if new_conversation_id:
                    self.conversation_id = new_conversation_id
                    self.watermark = None  # 新しい会話なのでwatermarkをリセット
                    logger.info(f"✅ 新しい会話開始: {new_conversation_id}")
                    return {
                        "success": True, 
                        "conversation_id": new_conversation_id,
                        "conversation_data": conversation_data
                    }
                else:
                    return {"success": False, "error": "会話IDが取得できませんでした"}
            else:
                error_msg = f"会話開始失敗: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"会話開始エラー: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Direct Line APIでメッセージを送信"""
        
        print("📤 Direct Line API メッセージ送信")
        print("=" * 60)
        print(f"メッセージ: {message}")
        
        # Step 1: トークンの確保
        if not self.ensure_token_available():
            return {
                "success": False,
                "error": "トークンの取得に失敗しました"
            }
        
        # Step 2: 会話の確保（必要に応じて新しい会話を開始）
        if not self.conversation_id:
            conversation_result = self.start_conversation()
            if not conversation_result["success"]:
                return {
                    "success": False,
                    "error": f"会話開始失敗: {conversation_result['error']}"
                }
        
        # Step 3: メッセージ送信
        send_url = f"{self.directline_endpoint}/conversations/{self.conversation_id}/activities"
        
        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json"
        }
        
        # Bot Framework Activity作成
        activity = {
            "type": "message",
            "from": {
                "id": "user123",
                "name": "Test User"
            },
            "text": message,
            "locale": "ja-JP",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channelId": "directline"
        }
        
        print(f"🎫 会話ID: {self.conversation_id}")
        print(f"🔗 送信URL: {send_url}")
        print(f"\n📋 送信アクティビティ:")
        print(json.dumps(activity, indent=2, ensure_ascii=False))
        
        try:
            print(f"\n🚀 メッセージ送信中...")
            
            response = self.session.post(send_url, headers=headers, json=activity, timeout=30)
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                response_data = response.json() if response.content else {}
                print(f"レスポンス: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                print("✅ メッセージ送信成功!")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response_data,
                    "conversation_id": self.conversation_id,
                    "activity": activity
                }
            else:
                error_msg = f"メッセージ送信失敗: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            error_msg = f"メッセージ送信エラー: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_activities(self, watermark: Optional[str] = None) -> Dict[str, Any]:
        """会話のアクティビティ（応答）を取得"""
        
        print("📥 Direct Line API 応答取得")
        print("=" * 60)
        
        if not self.ensure_token_available():
            return {
                "success": False,
                "error": "トークンの取得に失敗しました"
            }
        
        if not self.conversation_id:
            return {
                "success": False,
                "error": "会話IDが設定されていません"
            }
        
        # watermarkを使用してアクティビティを取得
        get_url = f"{self.directline_endpoint}/conversations/{self.conversation_id}/activities"
        
        if watermark or self.watermark:
            get_url += f"?watermark={watermark or self.watermark}"
        
        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Accept": "application/json"
        }
        
        print(f"🎫 会話ID: {self.conversation_id}")
        print(f"🔗 取得URL: {get_url}")
        print(f"📍 Watermark: {watermark or self.watermark or 'なし'}")
        
        try:
            print(f"\n🔍 応答取得中...")
            
            response = self.session.get(get_url, headers=headers, timeout=30)
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                activities_data = response.json()
                activities = activities_data.get('activities', [])
                new_watermark = activities_data.get('watermark')
                
                # watermarkを更新
                if new_watermark:
                    self.watermark = new_watermark
                
                print(f"📋 取得アクティビティ数: {len(activities)}")
                print(f"📍 新しいWatermark: {new_watermark}")
                
                # アクティビティの詳細を表示
                bot_responses = []
                for i, activity in enumerate(activities):
                    activity_type = activity.get('type', 'unknown')
                    from_id = activity.get('from', {}).get('id', 'unknown')
                    text = activity.get('text', '')
                    
                    print(f"\nアクティビティ {i+1}:")
                    print(f"  タイプ: {activity_type}")
                    print(f"  送信者: {from_id}")
                    
                    if text:
                        print(f"  テキスト: {text}")
                        # ボットからの応答を収集
                        if from_id != 'user123':  # ユーザー以外からの応答
                            bot_responses.append(text)
                    
                    # その他の情報
                    if activity.get('attachments'):
                        print(f"  添付ファイル: {len(activity['attachments'])}個")
                    
                    timestamp = activity.get('timestamp', '')
                    if timestamp:
                        print(f"  時刻: {timestamp}")
                
                print("✅ 応答取得成功!")
                
                return {
                    "success": True,
                    "activities": activities,
                    "watermark": new_watermark,
                    "bot_responses": bot_responses,
                    "total_activities": len(activities)
                }
            else:
                error_msg = f"応答取得失敗: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            error_msg = f"応答取得エラー: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def send_and_get_response(self, message: str, wait_time: float = 2.0, max_retries: int = 5) -> Dict[str, Any]:
        """メッセージを送信してボットからの応答を取得"""
        
        print("🔄 メッセージ送信 & 応答取得")
        print("=" * 70)
        
        # Step 1: メッセージ送信
        send_result = self.send_message(message)
        if not send_result["success"]:
            return send_result
        
        print(f"\n{'='*70}")
        print("⏳ ボット応答待機中...")
        
        # Step 2: 応答を待機して取得（watermarkを使わず全アクティビティを確認）
        for attempt in range(max_retries):
            time.sleep(wait_time)
            
            print(f"\n🔍 応答取得試行 {attempt + 1}/{max_retries}")
            
            # 全アクティビティを取得してボット応答を探す
            get_result = self.get_activities()
            
            if get_result["success"]:
                bot_responses = get_result.get("bot_responses", [])
                
                if bot_responses:
                    print(f"\n🎉 ボット応答受信!")
                    print("=" * 50)
                    for i, response in enumerate(bot_responses, 1):
                        print(f"応答 {i}: {response}")
                    
                    return {
                        "success": True,
                        "message_sent": message,
                        "bot_responses": bot_responses,
                        "send_result": send_result,
                        "get_result": get_result,
                        "attempts": attempt + 1
                    }
                else:
                    print(f"  まだ応答がありません...")
            else:
                print(f"  応答取得エラー: {get_result.get('error')}")
        
        print(f"\n⚠️ {max_retries}回試行しましたが、ボット応答を取得できませんでした")
        
        return {
            "success": False,
            "error": f"ボット応答を{max_retries}回の試行で取得できませんでした",
            "message_sent": message,
            "send_result": send_result,
            "attempts": max_retries
        }
    
    def show_conversation_status(self):
        """現在の会話状況を表示"""
        
        print("\n🎫 会話ステータス:")
        print(f"  ✅ トークン: {'あり' if self.current_token else 'なし'}")
        if self.current_token:
            remaining = int(self.token_expires_at - datetime.now(timezone.utc).timestamp()) if self.token_expires_at else 0
            print(f"    残り時間: {remaining}秒")
        
        print(f"  🆔 会話ID: {self.conversation_id or 'なし'}")
        print(f"  📍 Watermark: {self.watermark or 'なし'}")


def main():
    """デモンストレーション実行"""
    
    print("🤖 Direct Line API 会話サービス")
    print("メッセージ送信 & 応答取得デモ")
    print("=" * 70)
    
    try:
        # サービス初期化
        service = DirectLineConversationService()
        
        # 会話状況表示
        service.show_conversation_status()
        
        # Demo 1: 基本的なメッセージ送信
        print(f"\n{'='*70}")
        print("📤 Demo 1: 基本メッセージ送信")
        print("-" * 40)
        result = service.send_message("こんにちは")
        
        # Demo 2: 応答取得
        print(f"\n{'='*70}")
        print("📥 Demo 2: 応答取得")
        print("-" * 40)
        activities_result = service.get_activities()
        
        # Demo 3: メッセージ送信 & 応答取得（統合）
        print(f"\n{'='*70}")
        print("🔄 Demo 3: 統合機能（送信 & 応答取得）")
        print("-" * 40)
        conversation_result = service.send_and_get_response("今日の天気はどうですか？")
        
        # 最終ステータス
        print(f"\n{'='*70}")
        print("📊 最終ステータス")
        print("-" * 40)
        service.show_conversation_status()
        
        print(f"\n🎉 デモ完了!")
        
        return {
            "basic_send": result,
            "get_activities": activities_result,
            "full_conversation": conversation_result
        }
        
    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    main()