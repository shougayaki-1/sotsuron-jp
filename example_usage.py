#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境変数モジュールの使用例
"""

# 環境変数モジュールをインポート
from env_loader import (
    load_environment, 
    get_gemini_api_key, 
    get_debug_mode, 
    get_environment,
    get_project_paths
)

def main():
    """メイン処理"""
    try:
        # 環境変数を読み込み
        print("=== 環境変数の読み込み ===")
        env_file_path = load_environment()
        print(f"読み込まれた.envファイル: {env_file_path}")
        print()
        
        # 各種環境変数を取得
        print("=== 環境変数の取得 ===")
        api_key = get_gemini_api_key()
        debug_mode = get_debug_mode()
        environment = get_environment()
        project_paths = get_project_paths()
        
        print(f"APIキー: {api_key[:10]}...")
        print(f"デバッグモード: {debug_mode}")
        print(f"環境: {environment}")
        print()
        
        # プロジェクトパス情報
        print("=== プロジェクトパス情報 ===")
        for key, path in project_paths.items():
            print(f"{key}: {path}")
        print()
        
        # 実際の使用例
        print("=== 実際の使用例 ===")
        if debug_mode:
            print("デバッグモードが有効です")
        
        if environment == 'development':
            print("開発環境で実行中です")
        
        # ここでGemini APIの設定を行う例
        # import google.generativeai as genai
        # genai.configure(api_key=api_key)
        # print("Gemini APIが設定されました")
        
    except ValueError as e:
        print(f"エラー: {e}")
        print("解決方法:")
        print("1. プロジェクトルート（sotsuron-jp）に.envファイルが存在することを確認")
        print("2. GEMINI_API_KEYが正しく設定されていることを確認")
        print("3. python-dotenvがインストールされていることを確認")
    except Exception as e:
        print(f"予期しないエラー: {e}")

if __name__ == "__main__":
    main()
