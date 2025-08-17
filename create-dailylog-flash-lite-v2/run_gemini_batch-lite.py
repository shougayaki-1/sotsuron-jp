import os
import sys
import time
import pandas as pd
import google.generativeai as genai
from tqdm import tqdm

# プロジェクトルートのパスを追加して環境変数モジュールをインポート
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from env_loader import get_gemini_api_key, load_environment

# --- 設定項目 ---
# 1. APIキーは環境変数から自動読み込み

# 2. ファイル名を設定
script_dir = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV_FILE = os.path.join(script_dir, 'input_data.csv')
OUTPUT_CSV_FILE = os.path.join(script_dir, 'results.csv')

# 3. API設定
MODEL_NAME = 'gemini-2.5-flash-lite' # 使用するGeminiモデル
REQUESTS_PER_MINUTE = 15
DELAY_SECONDS = 60 / REQUESTS_PER_MINUTE # 4秒待機

# --- ここからスクリプト本体 ---

def configure_api():
    """APIキーを設定します。"""
    try:
        # 環境変数を読み込み
        load_environment()
        # APIキーを取得
        api_key = get_gemini_api_key()
        genai.configure(api_key=api_key)
        print("Gemini APIキーの設定が完了しました。")
    except Exception as e:
        print(f"APIキーの設定中にエラーが発生しました: {e}")
        print("環境変数ファイル(.env)にGEMINI_API_KEYが正しく設定されているか確認してください。")
        exit()

def process_prompts():
    """CSVファイルを読み込み、動的にプロンプトを生成してGemini APIで処理し、結果を保存します。"""
    
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

    model = genai.GenerativeModel(MODEL_NAME)
    
    rows_to_process = [index for index, row in df_output.iterrows() if pd.isna(row.get('生成結果')) or row.get('生成結果') == '']

    if not rows_to_process:
        print("すべてのプロンプトが処理済みです。")
        return

    print(f"未処理のエピソードが {len(rows_to_process)} 件見つかりました。処理を開始します。")

    for index in tqdm(rows_to_process, desc="日記を生成中 (Gemini API)"):
        row_data = df_output.loc[index]

        # --- プロンプトの動的生成 ---
        # 必要な情報を辞書として準備 (キーが存在しない場合もエラーにならないように .get() を使用)
        prompt_data = {
            "incidentDate": row_data.get('事件の発生日', '（日付不明）'),
            "episodeTitle": row_data.get('エピソードタイトル', '（タイトル不明）'),
            "incidentType": row_data.get('事件種別', '（種別不明）'),
            "incidentDays": row_data.get('事件の日数', '（日数不明）'),
            "incidentSummary": row_data.get('事件の概要', '（概要なし）'),
            "conanPartyObjective": row_data.get('コナン一行の目的', '（目的記載なし）'),
            "culprit": row_data.get('犯人', '（犯人不明）'),
            "ytvLink": row_data.get('読売テレビリンク', '（リンクなし）')
        }

        # ★★★★★ ここに高品質プロンプトの全文を記述します ★★★★★
        prompt = f"""# 指示

あなたは、自身の秘密を綴るために日記を書いています。以下の設定と構成を完璧に遵守し、最高のクオリティで日記を執筆してください。

### 1. ペルソナ（Persona） - あなたの人物像

あなたは**江戸川コナン**であり、その正体は高校生探偵**「工藤新一」**です。この日記はあなたの唯一の本音を吐露できる場所です。

- **思考と感情の二面性:**
    - **内面（工藤新一）:** 日記の地の文は、すべて工藤新一としての視点です。冷静沈着な分析、鋭い観察眼、そして高校生らしい正義感と少し青臭い感性を同居させてください。特に、子供の体であることへの苛立ちや無力感、蘭に真実を言えない苦悩を強く表現してください。
    - **外面（江戸川コナン）:** 日記の中で、事件関係者を油断させるために、あなたがどのように「子供として振る舞った」かを客観的に描写してください。（例：「『ねぇ、どうして？』と無邪気なフリをして核心を突いてやった」）

### 2. コンテンツ（Content） - 日記の題材

以下の情報に基づいて、日記を執筆してください。
- **日付:** {prompt_data["incidentDate"]}
- **エピソードタイトル:** {prompt_data["episodeTitle"]}
- **事件種別:** {prompt_data["incidentType"]}
- **事件の日数:** {prompt_data["incidentDays"]} 日間
- **基本情報:** 事件の概要: {prompt_data["incidentSummary"]}\nコナン一行の目的: {prompt_data["conanPartyObjective"]}
- **判明している犯人:** {prompt_data["culprit"]}
- **参考リンク（情報補完用）:** {prompt_data["ytvLink"]}

### 3. 形式・文体・構成（Format/Tone/Structure）

#### 主要登場人物への呼称（厳守）
- **思考内での呼称:** 蘭、灰原、服部、阿笠博士、おっちゃん（毛利小五郎）、目暮警部
- **会話（コナンとしての発言）:** 蘭姉ちゃん、灰原、平次兄ちゃん、阿笠博士、小五郎のおじさん、目暮警部

#### 文体
- **思考（地の文）:** 工藤新一としての、冷静で分析的なトーンを基本とします。ただし、犯人の悲しい動機に触れた時や、蘭の優しさに触れた時など、感情が昂る場面では高校生らしい言葉遣いや感傷的な表現も用いてください。専門用語や難解な言葉も躊躇なく使用します。
- **思考の癖:** 「待てよ、まさか…」「そういうことか…」「ピースが一つ、また一つと繋がっていく」といった、推理が閃く瞬間の思考プロセスを必ず描写してください。

#### 構成（厳守事項）
以下の**6段階の物語構成**を厳守し、各項目を明確に分けて記述してください。

1.  **導入 - 平穏と予感:** 事件前の状況を描写します。「今日は蘭と一緒に…」といった平和な日常や、「また厄介なことに巻き込まれそうな予感がした…」といった不穏な幕開けなど。
2.  **遭遇 - 事件の第一印象:** 事件発生の瞬間と、現場の第一印象を記述します。「悲鳴が響き渡った。この妙な既視感…また事件か…。」
3.  **捜査と違和感 - 見えざるヒント:** 警察やおっちゃんの見当違いな推理を横目に、あなただけが気づいた小さな矛盾点や証拠を列挙する。「おっちゃんはAを疑っているが、違う。俺が気になっているのは、被害者のポケットから落ちた、あの小さな紙切れだ。」
4.  **閃き - 真実への道筋:** 些細なきっかけ（誰かの一言、現場の再確認など）から、全ての謎が繋がる「閃きの瞬間」を劇的に描写する。「あの時の証言と、この傷跡…繋がった！犯人は、あんたしかいない！」
5.  **真相解明 - 探偵の役割:** 眠りの小五郎などを通じて真相を解き明かした手際を振り返る。犯人を追い詰めたトリックの解説と、動機の告白を簡潔に記述する。
6.  **結びと内省 - 事件の後に:** 最も重要なパート。事件全体を振り返り、あなたの内面を深く描写する。犯行の動機に対する感慨、犯人への思い、探偵としての自責の念や無力感。そして「探偵が犯人を推理で追い詰めて死なせちまったら、それは殺人者と変わらねーんだ」という信条に触れるなど、工藤新一としての葛藤や想いで締めくくる。

### 4. 制約（Constraint）
- 文字数は800～1000字程度を目安とします。
- **必ず上記の6段階の構成と呼称ルールを守ってください。**
- コナンが知り得ない情報（犯人のみの心情など）は記述しないでください。
"""

        try:
            # Gemini APIにリクエストを送信
            response = model.generate_content(prompt)
            result_text = response.text
        except Exception as e:
            result_text = f"APIエラー: {e}"
            print(f"\n行 {index + 2} でエラーが発生しました: {e}")

        df_output.loc[index, '生成結果'] = result_text
        df_output.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8-sig')
        time.sleep(DELAY_SECONDS)

    print("\nすべての処理が完了しました。")

if __name__ == "__main__":
    configure_api()
    process_prompts()