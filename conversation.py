#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Line 会話サービス使用例
コマンドライン引数でメッセージを指定可能
"""

import sys
import argparse
from directline_conversation_service import DirectLineConversationService

def send_message_from_args():
    """コマンドライン引数からメッセージを送信"""
    
    parser = argparse.ArgumentParser(
        description='Copilot Studioとの会話を実行',
        epilog='例: python conversation.py "こんにちは" --wait 5 --retries 10 --continue'
    )
    
    parser.add_argument(
        'message',
        help='ボットに送信するメッセージ'
    )
    
    parser.add_argument(
        '--wait', '-w',
        type=float,
        default=5.0,
        help='応答待機時間（秒）。デフォルト: 5.0'
    )
    
    parser.add_argument(
        '--retries', '-r',
        type=int,
        default=10,
        help='最大リトライ回数。デフォルト: 10'
    )
    
    parser.add_argument(
        '--send-only', '-s',
        action='store_true',
        help='メッセージ送信のみ（応答取得をスキップ）'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='詳細なログを非表示にして結果のみ表示'
    )
    
    parser.add_argument(
        '--continue', '-c',
        action='store_true',
        help='連続会話モード（同じセッションで複数メッセージを送信）'
    )
    
    args = parser.parse_args()
    
    # サービスを初期化
    service = DirectLineConversationService()
    
    if not args.quiet:
        print("🤖 Direct Line 会話サービス")
        print("=" * 50)
        print(f"📤 メッセージ: {args.message}")
        print(f"⏱️  待機時間: {args.wait}秒")
        print(f"🔄 最大リトライ: {args.retries}回")
        print("-" * 50)
    
    try:
        # 連続会話モードの場合
        if getattr(args, 'continue', False):
            return continuous_conversation_mode(service, args.message, args)
        
        if args.send_only:
            # メッセージ送信のみ
            result = service.send_message(args.message)
            if result["success"]:
                if args.quiet:
                    print("✅ 送信成功")
                else:
                    print("✅ メッセージ送信成功")
                    print(f"📋 レスポンス: {result.get('response', {})}")
                return True
            else:
                print(f"❌ 送信失敗: {result['error']}")
                return False
        else:
            # メッセージ送信 & 応答取得
            result = service.send_and_get_response(
                args.message,
                wait_time=args.wait,
                max_retries=args.retries
            )
            
            if result["success"]:
                bot_responses = result.get("bot_responses", [])
                
                if args.quiet:
                    # 簡潔な出力
                    for response in bot_responses:
                        print(f"🤖: {response}")
                else:
                    # 詳細な出力
                    print("✅ 会話成功!")
                    print(f"📤 送信: {result['message_sent']}")
                    print(f"🎯 試行回数: {result.get('attempts', 1)}")
                    print("-" * 30)
                    
                    if bot_responses:
                        for i, response in enumerate(bot_responses, 1):
                            print(f"🤖 応答 {i}: {response}")
                    else:
                        print("⚠️  ボットからの応答がありませんでした")
                
                return True
            else:
                print(f"❌ 会話失敗: {result['error']}")
                return False
                
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False


def continuous_conversation_mode(service, initial_message, args):
    """連続会話モード"""
    
    if not args.quiet:
        print("💬 連続会話モード開始")
        print("=" * 50)
        print("追加メッセージを入力してください（'quit'で終了）")
        print(f"初回メッセージ: {initial_message}")
        print("-" * 50)
    
    # 初回メッセージを送信
    if args.send_only:
        result = service.send_message(initial_message)
        if result["success"]:
            if args.quiet:
                print("✅ 送信成功")
            else:
                print("✅ 初回メッセージ送信成功")
        else:
            print(f"❌ 初回送信失敗: {result['error']}")
            return False
    else:
        result = service.send_and_get_response(
            initial_message,
            wait_time=args.wait,
            max_retries=args.retries
        )
        
        if result["success"]:
            bot_responses = result.get("bot_responses", [])
            
            if args.quiet:
                for response in bot_responses:
                    print(f"🤖: {response}")
            else:
                print("✅ 初回会話成功!")
                print(f"📤 送信: {initial_message}")
                for i, response in enumerate(bot_responses, 1):
                    print(f"🤖 応答 {i}: {response}")
        else:
            print(f"❌ 初回会話失敗: {result['error']}")
            return False
    
    # 連続会話ループ
    try:
        while True:
            if not args.quiet:
                print()  # 空行
            
            user_input = input("👤 追加メッセージ: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '終了', 'q']:
                if not args.quiet:
                    print("👋 連続会話を終了します")
                break
            
            if not user_input:
                print("⚠️  メッセージを入力してください")
                continue
            
            if not args.quiet:
                print("🔄 送信中...")
            
            if args.send_only:
                result = service.send_message(user_input)
                if result["success"]:
                    if args.quiet:
                        print("✅ 送信成功")
                    else:
                        print("✅ メッセージ送信成功")
                else:
                    print(f"❌ 送信失敗: {result['error']}")
            else:
                result = service.send_and_get_response(
                    user_input,
                    wait_time=args.wait,
                    max_retries=args.retries
                )
                
                if result["success"]:
                    bot_responses = result.get("bot_responses", [])
                    if bot_responses:
                        for response in bot_responses:
                            print(f"🤖: {response}")
                    else:
                        print("⚠️  ボットからの応答がありませんでした")
                else:
                    print(f"❌ エラー: {result['error']}")
                    
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n👋 中断されました")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    return True


def example_usage():
    """デモンストレーション用の使用例"""
    
    print("🎯 デモンストレーション モード")
    print("=" * 50)
    
    # サービスを初期化
    service = DirectLineConversationService()
    
    # Example 1: 基本的なメッセージ送信
    print("=== Example 1: メッセージ送信のみ ===")
    send_result = service.send_message("こんにちは、元気ですか？")
    if send_result["success"]:
        print("✅ メッセージ送信成功")
    else:
        print(f"❌ 送信失敗: {send_result['error']}")
    
    # Example 2: 応答を手動取得
    print("\n=== Example 2: 応答手動取得 ===")
    activities_result = service.get_activities()
    if activities_result["success"]:
        bot_responses = activities_result.get("bot_responses", [])
        print(f"✅ ボット応答数: {len(bot_responses)}")
        for response in bot_responses:
            print(f"🤖 ボット: {response}")
    
    # Example 3: 統合機能（推奨）
    print("\n=== Example 3: 統合機能（送信&応答取得） ===")
    conversation_result = service.send_and_get_response(
        "今日のおすすめを教えてください",
        wait_time=3.0,  # 3秒待機
        max_retries=3   # 最大3回試行
    )
    
    if conversation_result["success"]:
        print("✅ 完全な会話成功")
        print(f"📤 送信メッセージ: {conversation_result['message_sent']}")
        
        bot_responses = conversation_result.get("bot_responses", [])
        for i, response in enumerate(bot_responses, 1):
            print(f"🤖 ボット応答 {i}: {response}")
    else:
        print(f"❌ 会話失敗: {conversation_result['error']}")


def interactive_mode():
    """対話モード"""
    
    print("💬 対話モード")
    print("=" * 50)
    print("メッセージを入力してください（'quit'で終了）")
    
    service = DirectLineConversationService()
    
    while True:
        try:
            user_input = input("\n👤 あなた: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '終了', 'q']:
                print("👋 お疲れ様でした！")
                break
            
            if not user_input:
                print("⚠️  メッセージを入力してください")
                continue
            
            print("🔄 送信中...")
            result = service.send_and_get_response(user_input, wait_time=5.0)
            
            if result["success"]:
                bot_responses = result.get("bot_responses", [])
                if bot_responses:
                    for response in bot_responses:
                        print(f"🤖 ボット: {response}")
                else:
                    print("⚠️  ボットからの応答がありませんでした")
            else:
                print(f"❌ エラー: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 中断されました")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # コマンドライン引数がある場合
        if sys.argv[1] == "--demo":
            example_usage()
        elif sys.argv[1] == "--interactive":
            interactive_mode()
        else:
            # 通常の引数処理
            success = send_message_from_args()
            sys.exit(0 if success else 1)
    else:
        # 引数がない場合はヘルプを表示
        print("🤖 Direct Line 会話サービス")
        print("=" * 50)
        print("使用方法:")
        print("  python conversation.py \"メッセージ\" [オプション]")
        print("  python conversation.py --demo")
        print("  python conversation.py --interactive")
        print("\nオプション:")
        print("  --wait, -w      応答待機時間（秒）デフォルト: 5.0")
        print("  --retries, -r   最大リトライ回数 デフォルト: 10")
        print("  --send-only, -s メッセージ送信のみ")
        print("  --quiet, -q     簡潔な出力")
        print("  --continue, -c  連続会話モード")
        print("\n例:")
        print("  python conversation.py \"こんにちは\"")
        print("  python conversation.py \"今日の天気は？\" --wait 5 --retries 10")
        print("  python conversation.py \"テスト\" --send-only --quiet")
        print("  python conversation.py \"こんにちは\" --continue")
        print("  python conversation.py --interactive")
        sys.exit(1)