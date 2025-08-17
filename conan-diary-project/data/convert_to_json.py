import pandas as pd
import os

# --- 設定 ---
CSV_FILE_PATH = 'results.csv'
OUTPUT_DIR = 'json_data'
# --- 設定ここまで ---

def convert_csv_to_json():
    """
    results.csv（カンマ区切り）を読み込み、
    パラレルワールドごとにJSONファイルに変換して出力する関数
    """
    print(f"'{CSV_FILE_PATH}' の読み込みを開始します...")

    # CSVファイルの存在チェック
    if not os.path.exists(CSV_FILE_PATH):
        print(f"エラー: '{CSV_FILE_PATH}' が見つかりません。")
        print("スクリプトと同じ階層にCSVファイルを配置してください。")
        return

    try:
        # ★ 変更点: 区切り文字をタブからカンマに変更しました。
        # CSVファイルの1行目をヘッダーとして自動的に読み込みます。
        df = pd.read_csv(CSV_FILE_PATH, sep=',')

        print("CSVの読み込みが完了しました。")

        # --- データの整形 ---
        # '主要登場人物'列が存在するか確認
        if '主要登場人物' in df.columns:
            # 文字列をカンマで分割し、前後の空白を削除してリストに変換
            df['主要登場人物'] = df['主要登場人物'].apply(
                lambda x: [person.strip() for person in str(x).split(',')] if pd.notna(x) else []
            )
        else:
            print("警告: '主要登場人物' 列が見つかりません。処理をスキップします。")

        # 'パラレルワールド名'列が存在しない場合はエラー
        if 'パラレルワールド名' not in df.columns:
            print("エラー: CSVファイルに 'パラレルワールド名' の列が見つかりません。")
            print("この列はJSONへの分割に必須です。CSVのヘッダーを確認してください。")
            return

        # 出力ディレクトリの作成
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"出力ディレクトリ '{OUTPUT_DIR}' を作成しました。")

        # 'パラレルワールド名' でデータをグループ化
        grouped = df.groupby('パラレルワールド名')

        print(f"{len(grouped)}個のパラレルワールドが見つかりました。JSONへの変換を開始します...")

        # 各グループを個別のJSONファイルとして保存
        for world_name, group_df in grouped:
            # ファイル名をサニタイズ（安全なファイル名に変換）
            safe_world_name = "".join(c for c in world_name if c.isalnum() or c in ('_', '-')).rstrip()
            output_filename = os.path.join(OUTPUT_DIR, f'{safe_world_name}.json')

            # Webサイトで扱いやすいように、レコード形式（オブジェクトの配列）で出力
            group_df.to_json(
                output_filename,
                orient='records',   # レコード形式
                force_ascii=False,  # 日本語をそのまま出力
                indent=4            # 見やすいようにインデントを適用
            )
            print(f" -> '{output_filename}' を作成しました。")

        print("\nすべての処理が正常に完了しました。")
        print(f"'{OUTPUT_DIR}' ディレクトリ内にJSONファイルが生成されています。")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        print("CSVの形式（特に区切り文字や列の構成）が正しいか確認してください。")

# スクリプトを実行
if __name__ == '__main__':
    convert_csv_to_json()