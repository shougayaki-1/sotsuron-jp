# 環境変数設定ガイド

このプロジェクトでは、環境変数を`sotsuron-jp`直下の`.env`ファイルで一元管理しています。

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install python-dotenv
```

### 2. .envファイルの作成

`sotsuron-jp`直下に`.env`ファイルを作成し、以下の内容を記述してください：

```env
# Gemini API設定
GEMINI_API_KEY=your-actual-api-key-here

# その他の設定
DEBUG=True
ENVIRONMENT=development

# プロジェクト固有の設定
PROJECT_ROOT=sotsuron-jp
```

**重要**: `your-actual-api-key-here`の部分を、実際のGemini APIキーに置き換えてください。

## 使用方法

### 基本的な使用

```python
from env_loader import get_gemini_api_key, load_environment

# 環境変数を読み込み
load_environment()

# APIキーを取得
api_key = get_gemini_api_key()
```

### 他のプロジェクトでの使用

```python
import sys
import os

# プロジェクトルートのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from env_loader import get_gemini_api_key

# 自動的に親ディレクトリの.envファイルを読み込み
api_key = get_gemini_api_key()
```

### 利用可能な関数

- `load_environment()`: 環境変数ファイルを読み込み
- `get_gemini_api_key()`: Gemini APIキーを取得
- `get_debug_mode()`: デバッグモードを取得
- `get_environment()`: 環境設定を取得
- `get_project_paths()`: プロジェクトパス情報を取得

## ファイル構成

```
sotsuron-jp/
├── .env                    ← 環境変数ファイル
├── .gitignore             ← Git除外設定
├── env_loader.py          ← 環境変数読み込みモジュール
├── example_usage.py       ← 使用例
├── README.md              ← このファイル
├── conan-diary-project/   ← コナン日記プロジェクト
├── create-dailylog/       ← 日記作成プロジェクト
├── create-dailylog-flash/ ← フラッシュ版日記作成
└── create-dailylog-local/ ← ローカル版日記作成
```

## セキュリティ

- ✅ `.env`ファイルは`.gitignore`に含まれており、Gitにコミットされません
- ✅ APIキーなどの機密情報は環境変数で管理
- ✅ 各プロジェクトで共通の環境変数を使用

## トラブルシューティング

### エラー: "GEMINI_API_KEY環境変数が設定されていません"

**解決方法:**
1. `.env`ファイルが`sotsuron-jp`直下に存在することを確認
2. `GEMINI_API_KEY`が正しく設定されていることを確認
3. `python-dotenv`パッケージがインストールされていることを確認

### 動作確認

```bash
cd sotsuron-jp
python env_loader.py
python example_usage.py
```

正常に動作すれば、環境変数の設定は完了です。
