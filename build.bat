@echo off
REM 设置代码页为 UTF-8 以支持中文字符
chcp 65001

REM 将当前目录更改为脚本所在的目录
cd /d %~dp0

REM 检查是否提供了正确数量的参数
if "%~4"=="" (
    echo "用法：build.bat <json 文件> <输出目录> <是否结尾暂停[yes/no]> <程序名称>"
    exit /b 1
)

REM 获取参数
set "json_path=%~1"
set "output_dir=%~2"
set "pause_flag=%~3"
set "name=%~4"

REM 显示提供的路径
echo "JSON路径: %json_path%"
echo "输出目录: %output_dir%"

REM 确保输出目录存在
if not exist "%output_dir%" (
    echo 输出目录不存在,正在创建...
    mkdir "%output_dir%"
)

REM 确保资产目录存在
if not exist "assets" mkdir assets
if not exist "assets\images" mkdir assets\images

REM 将 JSON 文件复制到资产文件夹
copy "%json_path%" "assets\presets.json"

REM 检查 main.py 是否存在
if not exist "main.py" (
    echo "当前目录中未找到 main.py"
    exit /b 1
)

REM 使用必要的参数运行 pyinstaller
poetry run pyinstaller main.py --onefile --clean --noconsole --name "%name%" --icon "assets\images\icon.ico" --add-data "assets\images\logo.png;assets/images" --add-data "assets\images\icon.ico;assets/images" --add-data "assets\presets.json;assets" --distpath "%output_dir%"

REM 检查 pyinstaller 是否成功
if errorlevel 1 (
    echo "PyInstaller 运行失败，请查看日志"
    del assets\presets.json
    rmdir /s /q build
    rmdir /s /q __pycache__
    exit /b 1
)

REM 清理临时文件
del %name%.spec
del assets\presets.json
rmdir /s /q build

REM 根据第三个参数决定是否暂停脚本
if /i "%pause_flag%"=="yes" (
    pause
)
