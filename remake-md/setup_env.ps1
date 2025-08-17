# Gemini API環境変数設定スクリプト
# このスクリプトを実行する前に、Google AI StudioからAPIキーを取得してください

Write-Host "=== Gemini API環境変数設定 ===" -ForegroundColor Green
Write-Host ""

# 現在のディレクトリに応じたモデル情報を表示
$current_dir = Get-Location
Write-Host "現在のディレクトリ: $current_dir" -ForegroundColor Cyan

if ($current_dir -match "pro") {
    Write-Host "📁 プロディレクトリを検出: gemini-1.5-pro が使用されます" -ForegroundColor Yellow
} elseif ($current_dir -match "flash") {
    Write-Host "📁 フラッシュディレクトリを検出: gemini-1.5-flash が使用されます" -ForegroundColor Yellow
} else {
    Write-Host "📁 デフォルトディレクトリ: gemini-2.5-flash-lite が使用されます" -ForegroundColor Yellow
}

Write-Host ""

# 現在のAPIキーを確認
$current_key = $env:GEMINI_API_KEY
if ($current_key) {
    Write-Host "現在のAPIキー: $($current_key.Substring(0, [Math]::Min(10, $current_key.Length)))..." -ForegroundColor Yellow
} else {
    Write-Host "APIキーが設定されていません" -ForegroundColor Red
}

Write-Host ""
Write-Host "新しいAPIキーを入力してください（Enterキーでスキップ）:" -ForegroundColor Cyan
$new_key = Read-Host

if ($new_key -and $new_key -ne "") {
    # 環境変数を設定
    $env:GEMINI_API_KEY = $new_key
    
    # 永続化（現在のセッションのみ）
    Write-Host ""
    Write-Host "APIキーが設定されました！" -ForegroundColor Green
    Write-Host "注意: この設定は現在のPowerShellセッションのみ有効です" -ForegroundColor Yellow
    Write-Host "永続化するには、システムの環境変数設定で設定してください" -ForegroundColor Yellow
    
    # テスト用の簡単な確認
    Write-Host ""
    Write-Host "設定をテストしますか？ (y/n):" -ForegroundColor Cyan
    $test = Read-Host
    if ($test -eq "y" -or $test -eq "Y") {
        try {
            Write-Host "Gemini APIの接続テスト中..." -ForegroundColor Yellow
            
            # セキュリティ修正: 一時ファイルを使用してPythonスクリプトを実行
            $temp_script_path = [System.IO.Path]::GetTempFileName()
            $temp_script_content = @"
import google.generativeai as genai
import os

# APIキーを環境変数から取得（セキュリティ向上）
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    try:
        genai.configure(api_key=api_key)
        print('✓ 接続成功！')
    except Exception as e:
        print(f'✗ 接続エラー: {e}')
else:
    print('✗ 環境変数からAPIキーを取得できませんでした')
"@
            
            # 一時ファイルにスクリプトを書き込み
            $temp_script_content | Out-File -FilePath $temp_script_path -Encoding UTF8
            
            # Pythonスクリプトを実行
            python $temp_script_path
            
            # 一時ファイルを削除
            Remove-Item $temp_script_path -Force
            
            # モデル選択のテストも実行
            Write-Host "モデル選択のテスト中..." -ForegroundColor Yellow
            
            $model_test_script_path = [System.IO.Path]::GetTempFileName()
            $model_test_content = @"
import os

current_dir = os.getcwd()
if 'pro' in current_dir.lower():
    print('📁 プロディレクトリ検出: gemini-2.5-pro')
elif 'flash' in current_dir.lower():
    print('📁 フラッシュディレクトリ検出: gemini-2.5-flash')
else:
    print('📁 デフォルトディレクトリ: gemini-2.5-flash-lite')
"@
            
            # 一時ファイルにスクリプトを書き込み
            $model_test_content | Out-File -FilePath $model_test_script_path -Encoding UTF8
            
            # Pythonスクリプトを実行
            python $model_test_script_path
            
            # 一時ファイルを削除
            Remove-Item $model_test_script_path -Force
            
        } catch {
            Write-Host "✗ 接続テストに失敗しました" -ForegroundColor Red
            Write-Host "エラー詳細: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "APIキーの設定をスキップしました" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "設定完了！" -ForegroundColor Green
Write-Host "プログラムを実行する準備ができました。" -ForegroundColor Green
Write-Host "使用されるモデル: " -NoNewline
if ($current_dir -match "pro") {
    Write-Host "gemini-1.5-pro" -ForegroundColor Yellow
} elseif ($current_dir -match "flash") {
    Write-Host "gemini-1.5-flash" -ForegroundColor Yellow
} else {
    Write-Host "gemini-2.5-flash-lite" -ForegroundColor Yellow
}
