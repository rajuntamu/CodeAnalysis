import os
import ollama
import datetime

# ==========================================
# 1. 設定・準備
# ==========================================

# 解析したいディレクトリ（現在の場所）
TARGET_DIR = "./"

# 結果を保存するファイル名
LOG_FILE = "analysis_report.txt"

# 解析プロンプト（XMLタグ方式に変更）
# {code_content} という波括弧は使わず、単純な文字列置換用のマークを使います
PROMPT_TEMPLATE = """
あなたは優秀なセキュリティエンジニア兼不動産システムの専門家です。
以下の <source_code> タグで囲まれたコードをレビューし、次の2点をチェックしてください。

1. 【セキュリティ】脆弱性（SQLインジェクション、XSS、OSコマンドインジェクションなど）
2. 【業務仕様】成約済み物件が誤って公開される、意図しないステータス変更などのロジック不備

**回答のルール:**
- 解説や指摘は**すべて日本語**で行ってください。
- 指摘する箇所の**ソースコードは原文のまま**引用してください。
- 問題がない場合は「問題なし」とだけ答えてください。

<source_code>
__CODE_HERE__
</source_code>
"""

# ログ出力用関数
def log_message(text):
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ==========================================
# 2. 実行処理
# ==========================================

# ログファイルの初期化
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== ソースコード解析レポート ===\n")
    f.write(f"実行日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("==================================\n\n")

print("解析を開始します。結果は 'analysis_report.txt' にも保存されます...\n")

for root, dirs, files in os.walk(TARGET_DIR):
    if ".venv" in dirs: dirs.remove(".venv")
    if ".git" in dirs: dirs.remove(".git")
    if "__pycache__" in dirs: dirs.remove("__pycache__")

    for file in files:
        if file.endswith(".py") and file != "analyze.py":
            file_path = os.path.join(root, file)
            
            log_message(f"--- 解析中: {file_path} ---")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 【修正点】 .format() ではなく .replace() を使用
                # これにより、ソースコード内の { } や ``` があっても崩れません
                final_prompt = PROMPT_TEMPLATE.replace("__CODE_HERE__", content)
                
                response = ollama.chat(model='llama3', messages=[
                  {'role': 'user', 'content': final_prompt},
                ])
                
                result_text = response['message']['content']
                log_message(result_text)
                log_message("\n" + "="*30 + "\n")
                
            except Exception as e:
                log_message(f"エラー: ファイルを読み込めませんでした ({e})")

log_message("すべての解析が終了しました。")
