#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用的な環境変数読み込みモジュール
sotsuron-jp直下の.envファイルを自動的に読み込みます
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment(env_file='.env'):
    """
    環境変数を読み込む
    
    Args:
        env_file: 環境変数ファイル名
    
    Returns:
        str: 読み込まれた.envファイルのパス
    """
    # 現在のディレクトリ（sotsuron-jp）の.envファイルを読み込み
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, env_file)
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"環境変数ファイルを読み込みました: {env_path}")
        return env_path
    else:
        # フォールバック: 現在の作業ディレクトリから.envを探す
        load_dotenv()
        print("現在の作業ディレクトリの.envファイルを読み込みました")
        return os.path.join(os.getcwd(), env_file)

def get_env_var(key, default=None, required=False):
    """
    環境変数を取得する
    
    Args:
        key: 環境変数名
        default: デフォルト値
        required: 必須かどうか
    
    Returns:
        str: 環境変数の値
    
    Raises:
        ValueError: 必須の環境変数が設定されていない場合
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"環境変数 {key} が設定されていません")
    
    return value

def get_gemini_api_key():
    """
    Gemini APIキーを取得する
    
    Returns:
        str: APIキー
    
    Raises:
        ValueError: APIキーが設定されていない場合
    """
    return get_env_var('GEMINI_API_KEY', required=True)

def get_debug_mode():
    """
    デバッグモードを取得する
    
    Returns:
        bool: デバッグモード
    """
    return get_env_var('DEBUG', 'False').lower() == 'true'

def get_environment():
    """
    環境設定を取得する
    
    Returns:
        str: 環境設定
    """
    return get_env_var('ENVIRONMENT', 'production')

def get_project_paths():
    """
    プロジェクトのパス情報を取得する
    
    Returns:
        dict: プロジェクトパスの辞書
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'root': current_dir,
        'conan_diary': os.path.join(current_dir, 'conan-diary-project'),
        'create_dailylog': os.path.join(current_dir, 'create-dailylog'),
        'create_dailylog_flash': os.path.join(current_dir, 'create-dailylog-flash'),
        'create_dailylog_local': os.path.join(current_dir, 'create-dailylog-local')
    }

# 使用例
if __name__ == "__main__":
    try:
        # 環境変数を読み込み
        env_file_path = load_environment()
        print(f"読み込まれた.envファイル: {env_file_path}")
        
        # 各種環境変数を取得
        api_key = get_gemini_api_key()
        debug_mode = get_debug_mode()
        environment = get_environment()
        project_paths = get_project_paths()
        
        print(f"APIキー: {api_key[:10]}...")
        print(f"デバッグモード: {debug_mode}")
        print(f"環境: {environment}")
        print(f"プロジェクトルート: {project_paths['root']}")
        
    except ValueError as e:
        print(f"エラー: {e}")
        print("解決方法:")
        print("1. プロジェクトルート（sotsuron-jp）に.envファイルが存在することを確認")
        print("2. GEMINI_API_KEYが正しく設定されていることを確認")
        print("3. python-dotenvがインストールされていることを確認")
    except Exception as e:
        print(f"予期しないエラー: {e}")
