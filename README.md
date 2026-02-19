# Direct Line 会話サービス

Copilot Studio と Direct Line API を使用したPython会話システムの実装

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 🌟 特徴

- ✅ **Microsoft Copilot Studio** との統合
- 🤖 **Direct Line API** を使用したリアルタイム会話
- 💬 **連続会話モード** サポート
- 🔄 **自動トークン管理** と再試行機能
- 📝 **コマンドライン** および **プログラマティック** インターフェース
- 🛡️ **堅牢なエラーハンドリング**

## 🎯 概要

Direct Line APIを使用してCopilot Studioとの会話を自動化するPythonサービスです。
コマンドライン引数での直接実行、対話モード、プログラマティックAPI使用など、複数の利用方法をサポートします。

## 📁 ファイル構成

- `directline_conversation_service.py` - メインサービス
- `conversation.py` - コマンドライン対応の使用例
- `.env` - 設定ファイル（Direct Line認証情報）
- `requirements.txt` - 依存関係

## 🛠️ 環境セットアップ

### 1. **前提条件**

- Python 3.7以上
- Microsoft Copilot Studio へのアクセス
- Direct Line チャネルの設定権限

### 2. **Python環境の準備**

```bash
# リポジトリをクローンまたはダウンロード
cd C:\BotFramework

# 仮想環境を作成（推奨）
python -m venv .venv

# 仮想環境を有効化
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows cmd:
.\.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 3. **Copilot Studio設定**

#### Step 1: Direct Line チャネルの有効化
1. Copilot Studio（https://copilotstudio.microsoft.com/）にログイン
2. 対象のボットを選択
3. 左メニュー「チャネル」→「Direct Line」を選択
4. 「Direct Line を有効にする」をクリック
5. 「シークレット キーを表示」をクリックしてシークレットをコピー

#### Step 2: エンドポイント情報の取得
1. ボット設定画面で「詳細設定」を確認
2. エンドポイントURLをコピー（例: `https://xxxxx.powerplatform.com/...`）

### 4. **環境変数の設定**

`.env` ファイルを作成して以下を設定：

```env
# Copilot Studio エンドポイント（ボット設定から取得）
AGENT_ENDPOINT_URL=https://your-copilot-studio-endpoint.powerplatform.com/copilotstudio/dataverse-backed/authenticated/bots/your-bot/conversations?api-version=2022-03-01-preview

# 認証ヘッダー名（通常は変更不要）
CUSTOM_AUTH_HEADER_NAME=Authorization

# Direct Line シークレットキー（Bearerプレフィックス付き）
CUSTOM_AUTH_HEADER_VALUE=Bearer YOUR_DIRECT_LINE_SECRET_HERE
```

### 5. **動作確認**

```bash
# 基本テスト
python conversation.py "こんにちは"

# 詳細出力でテスト
python conversation.py "テスト" --wait 5 --retries 10
```

## 🚀 使用方法

### **コマンドライン実行**

```bash
# 基本的な使用（デフォルト: 5秒待機、10回リトライ）
python conversation.py "こんにちは"

# カスタムオプション
python conversation.py "質問です" --wait 5 --retries 10

# 簡潔な出力（結果のみ表示）
python conversation.py "テスト" --quiet

# メッセージ送信のみ（応答取得スキップ）
python conversation.py "通知メッセージ" --send-only

# 対話モード（連続会話）
python conversation.py --interactive

# ヘルプ表示
python conversation.py --help
```

### **プログラマティック使用**

```python
from directline_conversation_service import DirectLineConversationService

# サービスを初期化
service = DirectLineConversationService()

# 基本的な会話
result = service.send_and_get_response("こんにちは")
if result["success"]:
    for response in result.get("bot_responses", []):
        print(f"🤖: {response}")

# カスタム設定での会話
result = service.send_and_get_response(
    "詳細な質問です",
    wait_time=5.0,    # 5秒待機
    max_retries=10    # 最大10回試行
)

# 手動制御
send_result = service.send_message("メッセージ")
if send_result["success"]:
    time.sleep(3)
    activities_result = service.get_activities()
    bot_responses = activities_result.get("bot_responses", [])
```

## ✅ 主要機能

### **1. 自動認証管理**
- Direct Line トークンの自動生成・更新
- セッション管理とエラーハンドリング
- トークン有効期限の自動監視

### **2. メッセージ送信**
- シンプルなテキストメッセージ送信
- Bot Framework Activity形式での通信
- 日本語ロケール対応

### **3. 応答取得**
- ボットからの応答を自動取得
- Watermark機能による効率的な応答追跡
- リアルタイム応答監視

### **4. コマンドライン対応**
- 引数での直接メッセージ送信
- 対話モード
- カスタマイズ可能な待機時間とリトライ

### **5. エラーハンドリング**
- 詳細なエラーレポート
- 自動リトライ機能
- ログ出力とデバッグ支援

## 📋 API リファレンス

### `DirectLineConversationService`

#### `__init__()`
```python
service = DirectLineConversationService()
```
- 環境変数から設定を自動読み込み
- トークン管理とセッションを初期化

#### `send_message(message: str) -> Dict[str, Any]`
- **目的**: メッセージをボットに送信
- **パラメータ**: `message` - 送信するテキストメッセージ
- **戻り値**: 送信結果とメタデータを含む辞書

#### `get_activities(watermark: Optional[str] = None) -> Dict[str, Any]`
- **目的**: 会話のアクティビティ（応答）を取得
- **パラメータ**: `watermark` - 取得開始位置（省略時は最初から）
- **戻り値**: アクティビティリストとボット応答

#### `send_and_get_response(message: str, wait_time: float = 5.0, max_retries: int = 10) -> Dict[str, Any]`
- **目的**: メッセージ送信から応答取得までを一括実行
- **パラメータ**:
  - `message`: 送信メッセージ
  - `wait_time`: 各試行間の待機時間（秒）
  - `max_retries`: 最大リトライ回数
- **戻り値**: 完全な会話結果

## 📊 レスポンス形式

### **成功時**
```python
{
    "success": True,
    "message_sent": "送信したメッセージ",
    "bot_responses": [
        "ボットからの応答1",
        "ボットからの応答2"
    ],
    "attempts": 3
}
```

### **失敗時**
```python
{
    "success": False,
    "error": "エラーメッセージ",
    "status_code": 404
}
```

## 🛠️ トラブルシューティング

### **よくある問題と解決方法**

#### **1. 401 Authorization Error**
```
❌ トークン生成失敗: 401 - Unauthorized
```
**解決方法**: 
- `.env` ファイルの `CUSTOM_AUTH_HEADER_VALUE` が正しいか確認
- Copilot Studio設定でDirect Line チャネルが有効化されているか確認
- シークレットキーが正しく `Bearer ` プレフィックス付きで設定されているか確認

#### **2. 404 Resource Not Found**
```
❌ メッセージ送信失敗: 404 - Conversation not found
```
**解決方法**:
- 会話が正常に作成されているか確認
- サービスを再起動して新しいトークンを生成
- エンドポイントURLが正しいか確認

#### **3. 応答が取得できない**
```
⚠️ 10回試行しましたが、ボット応答を取得できませんでした
```
**解決方法**:
- `--wait` オプションで待機時間を増やす（例: `--wait 10`）
- `--retries` オプションでリトライ回数を増やす（例: `--retries 15`）
- Copilot Studioのボット設定とトリガーを確認

### **デバッグモード**

詳細なログを有効にするには：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 実用例

### **バッチ処理**
```python
service = DirectLineConversationService()

questions = [
    "こんにちは",
    "今日の天気は？",
    "サポートが必要です"
]

for question in questions:
    result = service.send_and_get_response(question, wait_time=5.0)
    if result["success"]:
        print(f"Q: {question}")
        for response in result.get("bot_responses", []):
            print(f"A: {response}")
    print("-" * 50)
```

### **CSVファイルからの一括処理**
```bash
# questions.txtファイルから質問を読み込んで実行
while IFS= read -r line; do
    python conversation.py "$line" --quiet
done < questions.txt
```

### **スクリプトでの自動化**
```bash
#!/bin/bash
# 定期実行スクリプト例
python conversation.py "システム状況を確認してください" --quiet > status.log
python conversation.py "今日のタスクリストを表示して" --quiet > tasks.log
```

## 🔄 アップデート履歴

- **v1.0**: 基本的なDirect Line API実装
- **v1.1**: Watermark機能による効率的な応答取得
- **v1.2**: 統合機能追加（send_and_get_response）
- **v1.3**: エラーハンドリングとロギング改善
- **v1.4**: コマンドライン引数対応
- **v1.5**: 対話モード追加、待機時間・リトライ回数のカスタマイズ

## 📞 サポート

### **設定確認チェックリスト**
- [ ] Python 3.7以上がインストールされている
- [ ] 必要な依存関係がインストールされている（`pip install -r requirements.txt`）
- [ ] `.env` ファイルが正しく設定されている
- [ ] Copilot StudioでDirect Line チャネルが有効化されている
- [ ] Direct Line シークレットキーが有効である

### **ログファイルの確認**
問題が発生した場合は、詳細ログを有効にして原因を特定してください：

```bash
# デバッグモードで実行
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from conversation import *
# テスト実行
"
```

---

**🎯 このガイドに従って設定すれば、Copilot Studioとの自動会話システムが動作します！**