import os
import time
import pandas as pd
import google.generativeai as genai
from tqdm import tqdm

# --- スクリプト自身の場所を基準にファイルのパスを自動設定 ---
# このスクリプトファイルが存在するディレクトリの絶対パスを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- 設定項目 ---
# 1. あなたのAPIキーを設定してください
API_KEY = "AIzaSyCjRWV08l2uaxMQrQ9YTWIFy6PQxoPh2J0" # 環境変数から読み込むことを推奨

# 2. ファイル名を設定 (スクリプトと同じフォルダにあることを前提とする)
INPUT_CSV_FILE = os.path.join(script_dir, 'prompts.csv')
OUTPUT_CSV_FILE = os.path.join(script_dir, 'results.csv')

# 3. API設定
MODEL_NAME = 'gemini-2.5-flash-lite'
REQUESTS_PER_MINUTE = 15
DELAY_SECONDS = 60 / REQUESTS_PER_MINUTE

# --- ここからスクリプト本体 ---

def configure_api():
    """APIキーを設定します。"""
    if API_KEY == 'YOUR_API_KEY':
        print("エラー: APIキーが設定されていません。スクリプトを編集するか、環境変数を設定してください。")
        exit()
    try:
        genai.configure(api_key=API_KEY)
        print("Gemini APIキーの設定が完了しました。")
    except Exception as e:
        print(f"APIキーの設定中にエラーが発生しました: {e}")
        exit()

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
            print(f"スクリプトが探しているパス: {INPUT_CSV_FILE}")
            return

    model = genai.GenerativeModel(MODEL_NAME)
    
    rows_to_process = [index for index, row in df_output.iterrows() if pd.isna(row.get('生成結果', float('nan'))) or row.get('生成結果', '') == '']

    if not rows_to_process:
        print("すべてのプロンプトが処理済みです。")
        return

    print(f"未処理のプロンプトが {len(rows_to_process)} 件見つかりました。処理を開始します。")

    for index in tqdm(rows_to_process, desc="日記を生成中"):
        prompt = df_output.loc[index, '生成プロンプト']

        if pd.isna(prompt):
            df_output.loc[index, '生成結果'] = "エラー: プロンプトが空です"
            continue

        try:
            response = model.generate_content(prompt)
            result_text = response.text
        except Exception as e:
            result_text = f"APIエラー: {e}"
            print(f"\n行 {index + 2} でエラーが発生しました: {e}")

        df_output.loc[index, '生成結果'] = result_text
        df_output.to_csv(OUTPUT_CSV_FILE, index=False)
        time.sleep(DELAY_SECONDS)

    print("\nすべての処理が完了しました。")

if __name__ == "__main__":
    configure_api()
    process_prompts()