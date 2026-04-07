@echo off
REM Force clean deployment script for Windows

echo 🧹 Cleaning up local cache...
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo 📦 Installing dependencies...
call npm ci

echo 🏗️  Building for production...
call npm run build

echo ✅ Local build complete! Ready to deploy.
echo.
echo Next steps:
echo 1. Commit changes: git add . ^&^& git commit -m "fix: Update frontend deployment config"
echo 2. Push to deploy: git push origin main
echo 3. Check Vercel dashboard for deployment status
echo.
pause
