@echo off
chcp 65001 >nul
title 智面幻境 - 一键启动

echo ======================================
echo   智面幻境 (OfferPilot) 一键启动
echo   AI模拟面试训练系统
echo ======================================
echo.

set "PROJECT_ROOT=%~dp0"

:: ============================================
:: 1. 环境配置
:: ============================================
echo [1/4] 检查环境配置...

:: JDK 21（Lombok 兼容，避免 JDK 26 编译错误）
set "JAVA_HOME=C:\Program Files\Zulu\zulu-21"
if not exist "%JAVA_HOME%\bin\java.exe" (
    echo [警告] 未找到 JDK 21，尝试使用系统默认 Java...
    set "JAVA_HOME="
) else (
    echo         JDK 21: %JAVA_HOME%
)

:: 数据库密码（MySQL root 密码，覆盖可能存在的错误环境变量）
set "DB_PASSWORD=123456"
echo         数据库密码: %DB_PASSWORD%

:: ============================================
:: 2. 启动后端 (Spring Boot :8080)
:: ============================================
echo.
echo [2/4] 启动后端服务...

cd /d "%PROJECT_ROOT%\后端"
start "智面幻境-后端" cmd /c "mvnw.cmd spring-boot:run -q 2>&1"

:: 等待后端启动
echo         等待后端启动（约 10-30 秒）...
set /a waited=0
:wait_backend
timeout /t 2 /nobreak >nul
set /a waited+=2
curl -s http://localhost:8080/api/auth/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}" >nul 2>&1
if %errorlevel% equ 0 goto backend_ready
if %waited% geq 60 goto backend_timeout
goto wait_backend

:backend_timeout
echo         [警告] 后端启动超时，请手动检查
goto frontend_start

:backend_ready
echo         后端已就绪 (端口 8080)

:: ============================================
:: 3. 启动前端 (Vite :5173)
:: ============================================
:frontend_start
echo.
echo [3/4] 启动前端开发服务器...

cd /d "%PROJECT_ROOT%\前端"
start "智面幻境-前端" cmd /c "npm run dev 2>&1"

:: 等待前端启动
echo         等待前端启动（约 3-10 秒）...
timeout /t 4 /nobreak >nul

:: ============================================
:: 4. 打开浏览器
:: ============================================
echo.
echo [4/4] 打开浏览器...
start http://localhost:5173

echo.
echo ======================================
echo   启动完成！
echo   前端: http://localhost:5173
echo   后端: http://localhost:8080
echo.
echo   测试账号（密码均为 123456）:
echo     admin   - 系统管理员
echo     teacher - 就业指导老师
echo     student - 测试学生
echo ======================================
echo.
echo 按任意键退出...
pause >nul
