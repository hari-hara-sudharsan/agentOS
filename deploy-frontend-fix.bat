@echo off
REM Quick commit and deploy script

echo ========================================
echo   AgentOS Frontend Deployment Fix
echo ========================================
echo.

echo Step 1: Cleaning local cache...
cd frontend
if exist .next (
    rmdir /s /q .next
    echo ✓ Cleaned .next folder
) else (
    echo ✓ .next folder already clean
)
cd ..

echo.
echo Step 2: Staging files...
git add frontend/vercel.json
git add frontend/.env.production
git add frontend/next.config.ts
git add frontend/deploy-check.bat
git add frontend/deploy-check.sh
git add DEPLOYMENT_FIX.md
git add VERCEL_SETUP_GUIDE.md
git add FRONTEND_FIX_SUMMARY.md
git add deploy-frontend-fix.bat

echo ✓ Files staged

echo.
echo Step 3: Creating commit...
git commit -m "fix: Configure Vercel deployment and fix environment variables" -m "- Add vercel.json with proper cache control headers" -m "- Add .env.production template for production builds" -m "- Update next.config.ts with Next.js optimizations" -m "- Add deployment verification scripts" -m "- Force cache invalidation to ensure fresh builds" -m "- Add comprehensive deployment guides" -m "" -m "Fixes: Frontend not showing latest changes on Vercel" -m "Fixes: Environment variables pointing to localhost in production"

echo ✓ Commit created

echo.
echo Step 4: Checking git status...
git status

echo.
echo ========================================
echo   Ready to Deploy!
echo ========================================
echo.
echo BEFORE pushing, please:
echo 1. Go to Vercel Dashboard
echo 2. Set environment variables (see VERCEL_SETUP_GUIDE.md)
echo 3. Make sure you have your backend URL ready
echo.
echo Press any key to PUSH to origin/main and trigger deployment...
echo (Or press Ctrl+C to cancel)
pause > nul

echo.
echo Pushing to origin/main...
git push origin main

echo.
echo ========================================
echo   Deployment Triggered!
echo ========================================
echo.
echo Next steps:
echo 1. Watch Vercel Dashboard for build progress
echo 2. Wait 2-5 minutes for build to complete
echo 3. Visit: https://agent-bap3k3x86-first-intern.vercel.app
echo 4. Hard refresh: Ctrl + Shift + R
echo.
echo If you haven't set Vercel env vars yet:
echo - See VERCEL_SETUP_GUIDE.md for instructions
echo - This is REQUIRED for the fix to work!
echo.
pause
