@echo off
chcp 65001 >nul
echo ==============================================
echo          PyInstaller打包EXE一键脚本
echo ==============================================
echo.
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
echo 开始打包...
pyinstaller -F -w -n DeepSeek文案生成Agent main_server.py
echo.
echo 打包完成！EXE文件在 dist 文件夹内
echo 注意：运行EXE时需要把 .env、sensitive_words.txt 一同放在同级目录
pause
