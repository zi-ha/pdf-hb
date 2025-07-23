@echo off
echo 正在安装PDF合并工具所需的依赖...
echo.

pip install PyPDF2

echo.
echo 安装完成！
echo.
echo 使用方法：
echo 1. 将PDF文件放在同一个文件夹中
echo 2. 运行 python pdf_merger.py (完整版)
echo    或者 python simple_pdf_merger.py (简化版)
echo.
pause