#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
各プロジェクトで環境変数が正しく読み込まれるかテストするスクリプト
"""

import os
import sys
import subprocess
from pathlib import Path

def test_env_loader():
    """メインの環境変数ローダーをテスト"""
    print("=== メイン環境変数ローダーのテスト ===")
    try:
        from env_loader import get_gemini_api_key, load_environment
        load_environment()
        api_key = get_gemini_api_key()
        print(f"✅ 環境変数ローダー: 正常 (APIキー: {api_key[:10]}...)")
        return True
    except Exception as e:
        print(f"❌ 環境変数ローダー: エラー - {e}")
        return False

def test_project_script(project_name, script_path):
    """個別のプロジェクトスクリプトをテスト"""
    print(f"\n=== {project_name} のテスト ===")
    
    if not os.path.exists(script_path):
        print(f"⚠️  {project_name}: スクリプトファイルが見つかりません")
        return False
    
    try:
        # スクリプトのインポート部分をテスト
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 環境変数モジュールのインポートが含まれているかチェック
        if 'from env_loader import' in content:
            print(f"✅  {project_name}: 環境変数モジュールのインポート確認済み")
            
            # APIキーの直接記述が削除されているかチェック
            if 'AIzaSy' not in content:
                print(f"✅  {project_name}: APIキーの直接記述が削除済み")
                return True
            else:
                print(f"❌  {project_name}: APIキーの直接記述が残っています")
                return False
        else:
            print(f"❌  {project_name}: 環境変数モジュールのインポートが見つかりません")
            return False
            
    except Exception as e:
        print(f"❌  {project_name}: エラー - {e}")
        return False

def main():
    """メイン処理"""
    print("環境変数統合テストを開始します...\n")
    
    # メイン環境変数ローダーのテスト
    main_test_passed = test_env_loader()
    
    if not main_test_passed:
        print("\n❌ メイン環境変数ローダーのテストが失敗しました。")
        print("環境変数ファイル(.env)の設定を確認してください。")
        return
    
    # 各プロジェクトのテスト
    projects = [
        ("create-dailylog", "create-dailylog/run_gemini_batch.py"),
        ("create-dailylog-flash", "create-dailylog-flash/run_gemini_batch-flash.py"),
        ("create-dailylog-flash-lite-v2", "create-dailylog-flash-lite-v2/run_gemini_batch-lite.py"),
    ]
    
    passed_count = 0
    total_count = len(projects)
    
    for project_name, script_path in projects:
        if test_project_script(project_name, script_path):
            passed_count += 1
    
    # 結果サマリー
    print(f"\n=== テスト結果サマリー ===")
    print(f"総プロジェクト数: {total_count}")
    print(f"成功: {passed_count}")
    print(f"失敗: {total_count - passed_count}")
    
    if passed_count == total_count:
        print("\n🎉 すべてのテストが成功しました！")
        print("環境変数の統合が完了しています。")
    else:
        print(f"\n⚠️  {total_count - passed_count}個のプロジェクトで問題が発生しています。")
        print("上記のエラー内容を確認して修正してください。")

if __name__ == "__main__":
    main()
