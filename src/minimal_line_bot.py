"""
最小限のLINE Bot (改善システム統合版)
Pydantic互換性問題を回避しつつ、改善システムを統合
"""

import os
import sys
import traceback
from datetime import datetime
from flask import Flask, request

# 環境変数読み込み
from dotenv import load_dotenv
env_path = os.path.join('..', '.env')
load_dotenv(env_path)

# パス設定
current_dir = os.path.dirname(__file__)
tests_dir = os.path.join(current_dir, '..', 'tests')
sys.path.insert(0, tests_dir)

app = Flask(__name__)

# 改善システムの初期化
improved_generator = None

def initialize_improved_system():
    """改善システムを初期化"""
    global improved_generator

    try:
        from improved_response_system import ImprovedResponseGenerator
        db_path = os.path.join(current_dir, '..', 'db', 'conversation_history.db')
        improved_generator = ImprovedResponseGenerator(db_path)
        print("[INIT] ✅ Improved response system initialized")
        return True
    except Exception as e:
        print(f"[INIT] ❌ Failed to initialize improved system: {e}")
        return False

def generate_response(user_id: str, message: str) -> dict:
    """応答生成（改善システム使用）"""

    if improved_generator:
        try:
            result = improved_generator.generate_improved_response(user_id, message)
            if result.get('quality_score', 0) >= 2.5:  # 基準値を下げて動作確認
                print(f"[RESPONSE] ✅ Enhanced response (score: {result['quality_score']:.1f})")
                return {
                    'text': result['response'],
                    'source': 'enhanced_system',
                    'quality_score': result['quality_score']
                }
            else:
                print(f"[RESPONSE] ⚠️ Low quality, using fallback (score: {result['quality_score']:.1f})")
        except Exception as e:
            print(f"[RESPONSE] ❌ Enhanced system error: {e}")

    # フォールバック応答
    fallback_responses = {
        'こんにちは': 'こんにちは！お元気ですか？',
        'ありがとう': 'どういたしまして！お役に立てて嬉しいです。',
        'おはよう': 'おはようございます！今日も一日頑張りましょう！',
        'お疲れ様': 'お疲れ様でした！ゆっくり休んでくださいね。'
    }

    # キーワードマッチング
    for keyword, response in fallback_responses.items():
        if keyword in message:
            return {
                'text': response,
                'source': 'fallback_template',
                'quality_score': 2.0
            }

    # デフォルト応答
    return {
        'text': f'「{message}」について考えさせてください。何か他にお手伝いできることはありますか？',
        'source': 'default',
        'quality_score': 1.5
    }

@app.route('/')
def health_check():
    """ヘルスチェック"""
    status = {
        'status': 'running',
        'improved_system': 'enabled' if improved_generator else 'disabled',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return status

@app.route('/callback', methods=['POST'])
def callback():
    """LINEからのWebhook受信"""
    try:
        print(f"[WEBHOOK] Received at {datetime.now().strftime('%H:%M:%S')}")

        # リクエストデータの取得
        body = request.get_data(as_text=True)

        # 簡単なJSONパース（LINE Bot SDK使用せず）
        import json
        data = json.loads(body)

        # イベント処理
        events = data.get('events', [])
        for event in events:
            if event.get('type') == 'message' and event.get('message', {}).get('type') == 'text':
                # メッセージ情報取得
                user_id = event.get('source', {}).get('userId', 'unknown')
                message_text = event.get('message', {}).get('text', '')
                reply_token = event.get('replyToken', '')

                print(f"[MESSAGE] From {user_id[:10]}...: '{message_text}'")

                # 応答生成
                response_data = generate_response(user_id, message_text)

                print(f"[RESPONSE] {response_data['source']} (score: {response_data['quality_score']:.1f})")
                print(f"[RESPONSE] Text: '{response_data['text'][:50]}...'")

                # 実際のLINE送信（簡略化）
                if reply_token and os.getenv('LINE_CHANNEL_ACCESS_TOKEN'):
                    try:
                        import requests

                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {os.getenv("LINE_CHANNEL_ACCESS_TOKEN")}'
                        }

                        payload = {
                            'replyToken': reply_token,
                            'messages': [{
                                'type': 'text',
                                'text': response_data['text']
                            }]
                        }

                        response = requests.post(
                            'https://api.line.me/v2/bot/message/reply',
                            headers=headers,
                            json=payload,
                            timeout=10
                        )

                        if response.status_code == 200:
                            print("[SEND] ✅ Message sent successfully")
                        else:
                            print(f"[SEND] ❌ Failed to send message: {response.status_code}")

                    except Exception as send_error:
                        print(f"[SEND] ❌ Send error: {send_error}")
                else:
                    print("[SEND] ⚠️ No reply token or access token")

        return 'OK', 200

    except Exception as e:
        print(f"[ERROR] Webhook error: {e}")
        traceback.print_exc()
        return 'Error', 500

@app.route('/test')
def test_endpoint():
    """テスト用エンドポイント"""
    test_responses = []

    test_messages = [
        "こんにちは",
        "ありがとうございました",
        "おはようございます",
        "お疲れ様でした"
    ]

    for message in test_messages:
        response = generate_response("TEST_USER", message)
        test_responses.append({
            'input': message,
            'output': response['text'],
            'source': response['source'],
            'quality_score': response['quality_score']
        })

    return {
        'test_results': test_responses,
        'improved_system_status': 'enabled' if improved_generator else 'disabled'
    }

if __name__ == "__main__":
    print("🤖 最小限LINE Bot (改善システム統合版)")
    print("=" * 60)

    # 改善システム初期化
    improved_system_ok = initialize_improved_system()

    print(f"📊 システム状況:")
    print(f"   改善システム: {'✅ 有効' if improved_system_ok else '❌ 無効'}")
    print(f"   ACCESS_TOKEN: {'✅ 設定済み' if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else '❌ 未設定'}")
    print(f"   CHANNEL_SECRET: {'✅ 設定済み' if os.getenv('LINE_CHANNEL_SECRET') else '❌ 未設定'}")

    print(f"\n🌐 エンドポイント:")
    print(f"   ヘルスチェック: http://localhost:5000/")
    print(f"   Webhook: http://localhost:5000/callback")
    print(f"   テスト: http://localhost:5000/test")

    print(f"\n🚀 サーバー起動中...")

    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 サーバーを停止しました")
    except Exception as e:
        print(f"\n❌ サーバーエラー: {e}")
        traceback.print_exc()
