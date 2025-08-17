import os
import time
import pandas as pd
import requests
from tqdm import tqdm

# --- 設定項目 ---
# 1. あなたのローカルモデルサーバーの設定
#    OllamaのネイティブAPIエンドポイントを指定します。
LOCAL_API_ENDPOINT = "http://localhost:11434/api/chat"  # ★★★ 修正点1 ★★★
LOCAL_MODEL_NAME = "gpt-oss:20b"

# 2. ファイル名を設定
# スクリプトと同じディレクトリにあるCSVファイルを指定
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
INPUT_CSV_FILE = os.path.join(script_dir, 'prompts.csv')
OUTPUT_CSV_FILE = os.path.join(script_dir, 'results.csv')

# 3. API設定
DELAY_SECONDS = 1

# --- ここからスクリプト本体 ---

def check_server_connection():
    """スクリプト開始前にサーバーが起動しているか簡単なチェックを試みます。"""
    try:
        # サーバーのルートにアクセスしてみる
        base_url = LOCAL_API_ENDPOINT.replace("/api/chat", "")
        response = requests.get(base_url, timeout=3)
        # Ollamaサーバーはルートにアクセスすると "Ollama is running" と返す
        if response.ok and "Ollama is running" in response.text:
            print(f"Ollamaサーバーへの接続を確認しました: {base_url}")
            return True
        else:
            print(f"警告: サーバーは応答しましたが、Ollamaではない可能性があります。 (ステータス: {response.status_code})")
            return True # 接続はできたので処理は続行
    except requests.exceptions.RequestException as e:
        print("-" * 50)
        print(f"エラー: ローカルモデルサーバーに接続できません。")
        print(f"エンドポイント: {LOCAL_API_ENDPOINT}")
        print("Ollamaアプリが起動していることを確認してください。")
        print("-" * 50)
        return False

def process_prompts():
    """CSVファイルを読み込み、プロンプトを処理して結果を保存します。"""
    
    try:
        df_output = pd.read_csv(OUTPUT_CSV_FILE)
        print(f"'{OUTPUT_CSV_FILE}' を読み込みました。続きから処理を再開します。")
    except FileNotFoundError:
        try:
            df_input = pd.read_csv(INPUT_CSV_FILE)
            df_input['生成結果'] = ''
            df_output = df_input
            print(f"入力ファイル '{INPUT_CSV_FILE}' を基に、'{OUTPUT_CSV_FILE}' を新規作成します。")
        except FileNotFoundError:
            print(f"エラー: 入力ファイル '{INPUT_CSV_FILE}' が見つかりません。")
            return

    rows_to_process = [
        index for index, row in df_output.iterrows()
        if pd.isna(row.get('生成結果', float('nan'))) or str(row.get('生成結果', '')).strip() == ''
    ]

    if not rows_to_process:
        print("すべてのプロンプトが処理済みです。")
        return

    print(f"未処理のプロンプトが {len(rows_to_process)} 件見つかりました。処理を開始します。")

    for index in tqdm(rows_to_process, desc="日記を生成中 (ローカル)"):
        prompt = df_output.loc[index, '生成プロンプト']

        if pd.isna(prompt):
            df_output.loc[index, '生成結果'] = "エラー: プロンプトが空です"
            continue

        headers = {
            "Content-Type": "application/json",
        }
        # OllamaネイティブAPIでは stream: false を追加するとストリーミングなしの応答になる
        payload = {
            "model": LOCAL_MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False, 
        }

        try:
            response = requests.post(LOCAL_API_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            
            json_response = response.json()
            result_text = json_response['message']['content'] # ★★★ 修正点2 ★★★
            
        except requests.exceptions.RequestException as e:
            result_text = f"APIリクエストエラー: {e}"
            print(f"\n行 {index + 2} でAPIリクエストエラーが発生しました: {e}")
        except (KeyError, IndexError) as e:
            result_text = f"レスポンス形式エラー: {e} - {response.text}"
            print(f"\n行 {index + 2} でレスポンスの解析に失敗しました。")
        except Exception as e:
            result_text = f"予期せぬエラー: {e}"
            print(f"\n行 {index + 2} で予期せぬエラーが発生しました: {e}")

        df_output.loc[index, '生成結果'] = result_text
        df_output.to_csv(OUTPUT_CSV_FILE, index=False)
        
        time.sleep(DELAY_SECONDS)

    print("\nすべての処理が完了しました。")

if __name__ == "__main__":
    if check_server_connection():
        process_prompts()