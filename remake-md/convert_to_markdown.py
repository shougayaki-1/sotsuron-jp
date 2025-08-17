import pandas as pd
import re
import google.generativeai as genai
import os
from datetime import datetime

def get_gemini_model():
    """
    現在のディレクトリに応じて適切なGeminiモデルを選択
    """
    current_dir = os.getcwd()
    
    # ディレクトリ名に基づいてモデルを選択
    if "pro" in current_dir.lower():
        model_name = "gemini-1.5-pro"
        print(f"📁 プロディレクトリを検出: {model_name} を使用します")
    elif "flash" in current_dir.lower():
        model_name = "gemini-1.5-flash"
        print(f"📁 フラッシュディレクトリを検出: {model_name} を使用します")
    else:
        # デフォルトは gemini-2.5-flash-lite
        model_name = "gemini-2.5-flash-lite"
        print(f"📁 デフォルトディレクトリ: {model_name} を使用します")
    
    return model_name

def setup_gemini_api():
    """
    Gemini APIの設定
    """
    try:
        # 環境変数からAPIキーを取得
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("警告: GEMINI_API_KEY環境変数が設定されていません。")
            print("環境変数を設定するか、.envファイルを作成してください。")
            return None
        
        # Gemini APIの設定
        genai.configure(api_key=api_key)
        
        # 適切なモデルを選択
        model_name = get_gemini_model()
        model = genai.GenerativeModel(model_name)
        
        print(f"✅ Gemini API設定完了: {model_name}")
        return model
    except Exception as e:
        print(f"Gemini APIの設定でエラーが発生しました: {e}")
        return None

def convert_to_markdown_with_gemini(text, model):
    """
    Gemini APIを使用してmarkdown形式を変換する
    """
    if pd.isna(text) or text == '':
        return ""
    
    # プロンプトの作成
    prompt = f"""あなたは、与えられたMarkdownテキストを、指定された厳格なルールに従って再フォーマットするタスクを実行します。創造的な文章の生成や内容の変更は一切行わず、形式の変換のみに集中してください。

目的
以下の入力テキストに含まれる表記のゆれ（例: ## と ### の混在、不要な番号付け 1. など）を修正し、厳格に定義された出力テンプレートに完全に一致するように整形する。

入力テキスト (Input Text)
```markdown
{text}
```

出力テンプレート (Output Template) - 【最重要】
以下のテンプレートとルールを絶対に遵守して、入力テキストを再構成してください。このテンプレート以外の形式は認められません。

```markdown
## {{事件の発生日}}

### {{エピソードタイトル}}

### **導入 - その日の始まり**
（ここに「導入」セクションの本文を記述）

### **遭遇 - 事件の発生**
（ここに「遭遇」セクションの本文を記述）

### **捜査と観察 - 新一の視点**
（ここに「捜査と観察」セクションの本文を記述）

### **閃き - 真相への鍵**
（ここに「閃き」セクションの本文を記述）

### **真相解明 - 解決の舞台裏**
（ここに「真相解明」セクションの本文を記述）

### **結びと内省 - 事件の後で**
（ここに「結びと内省」セクションの本文を記述）
```

厳格なルール (Strict Rules)
見出しの正規化:
入力テキストの日付部分（例: ## 2023年1月3日）は、必ず ##（H2見出し）形式にしてください。
入力テキストのエピソードタイトル部分（例: ### 二十年目の殺意...）は、必ず ###（H3見出し）形式にしてください。

セクション見出しの統一:
入力テキストの 1. 導入 - その日の始まり や ## 導入 - その日の始まり のようなセクション見出しは、すべて ### **（セクション名）** の形式（H3見出し + 太字）に変換してください。
先頭の番号（1. や 2. など）は完全に削除してください。

空白行のルール:
各見出しとその下の本文の間、および本文の段落と段落の間には、必ず空行を1行だけ挿入してください。複数行の空行は許可されません。

内容の不変性:
各セクションの本文の内容（文章、句読点など）は一切変更しないでください。 あなたのタスクはフォーマットの修正のみです。

実行指示
上記のルールに従い、入力テキストを整形した結果のみを出力してください。説明や前置きは不要です。"""

    try:
        # Gemini APIにリクエストを送信
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # エラーが発生した場合は、エラーを表示して処理を停止
        error_msg = f"Gemini APIでの変換でエラーが発生しました: {e}"
        print(f"❌ {error_msg}")
        print(f"対象テキスト: {text[:100]}...")  # 最初の100文字を表示
        raise Exception(error_msg)  # エラーを再発生させて処理を停止

def process_csv(input_file, output_file):
    """
    CSVファイルを読み込み、生成結果列をmarkdown形式に変換して新しいCSVファイルを作成
    """
    try:
        # Gemini APIの設定
        print("Gemini APIの設定中...")
        model = setup_gemini_api()
        if model is None:
            print("Gemini APIの設定に失敗しました。プログラムを終了します。")
            return
        
        # CSVファイルを読み込み
        print(f"CSVファイルを読み込み中: {input_file}")
        df = pd.read_csv(input_file, encoding='utf-8')
        
        print(f"読み込んだデータの列名: {list(df.columns)}")
        print(f"データの行数: {len(df)}")
        
        # 生成結果列を探す（複数の可能性をチェック）
        target_column = None
        possible_columns = ['生成結果', '事件の概要', '概要', '内容']
        
        for col in possible_columns:
            if col in df.columns:
                target_column = col
                break
        
        if target_column is None:
            print("生成結果列が見つかりません。利用可能な列:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col}")
            return
        
        print(f"対象列: {target_column}")
        
        # エラー処理の選択肢を提供
        print("\nエラー処理の選択:")
        print("1. エラーが発生した行をスキップして処理を続行")
        print("2. エラーが発生したら処理を停止")
        choice = input("選択してください (1 または 2): ").strip()
        
        continue_on_error = choice == "1"
        
        # 生成結果列の各行をGemini APIを使用してmarkdown形式に変換
        print("Gemini APIを使用したmarkdown形式への変換を開始...")
        
        # 処理の進捗を表示するためのカウンター
        total_rows = len(df)
        error_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            if index % 10 == 0:  # 10行ごとに進捗を表示
                print(f"処理中... {index + 1}/{total_rows} 行目")
            
            # 生成結果列の内容を変換
            original_text = row[target_column]
            try:
                converted_text = convert_to_markdown_with_gemini(original_text, model)
                df.at[index, target_column] = converted_text
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"❌ 行 {index + 1} でエラーが発生しました: {e}")
                print(f"対象テキスト: {original_text[:100]}...")
                
                if not continue_on_error:
                    print("エラーが発生したため、処理を停止します。")
                    return
                else:
                    # エラーが発生した場合は空文字列にする
                    df.at[index, target_column] = ""
                    print(f"行 {index + 1} をスキップして処理を続行します。")
        
        # 処理結果の表示
        print(f"\n=== 処理完了 ===")
        print(f"成功: {success_count} 行")
        print(f"エラー: {error_count} 行")
        print(f"合計: {total_rows} 行")
        
        # 新しいCSVファイルとして保存
        print(f"変換結果を保存中: {output_file}")
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"出力ファイル: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    メイン処理
    """
    print("=== CSV to Markdown Converter (Gemini API版) ===")
    
    # 入力ファイルと出力ファイルのパス
    input_file = "input_data.csv"
    output_file = "output.csv"
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    # CSVファイルの処理
    process_csv(input_file, output_file)

if __name__ == "__main__":
    main()
