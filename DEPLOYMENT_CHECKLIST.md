# ✅ DEPLOYMENT FIX CHECKLIST

Print this or keep it open while you deploy!

---

## ☐ STEP 1: VERCEL ENVIRONMENT VARIABLES (CRITICAL!)

Go to: https://vercel.com/dashboard

☐ Click your project
☐ Go to **Settings** → **Environment Variables**
☐ Add these 5 variables for **Production**:

```
☐ NEXT_PUBLIC_API_URL = [YOUR BACKEND URL]
☐ NEXT_PUBLIC_AUTH0_DOMAIN = hariharasudharsanj.us.auth0.com
☐ NEXT_PUBLIC_AUTH0_CLIENT_ID = 7q73PbVm1krlqaqnKtGZbPJHXdfaIkHT
☐ NEXT_PUBLIC_AUTH0_AUDIENCE = https://agentos.local/api
☐ VERCEL_FORCE_NO_BUILD_CACHE = 1
```

☐ **Find your backend URL** (Railway/Heroku dashboard)
☐ **Replace** [YOUR BACKEND URL] with actual URL
☐ **Save** all variables

---

## ☐ STEP 2: CLEAN LOCAL CACHE

```bash
cd c:\Users\Windows\agentos\frontend
rmdir /s /q .next
cd ..
```

☐ Executed successfully

---

## ☐ STEP 3: COMMIT CHANGES

**Option A: Use automated script**

```bash
deploy-frontend-fix.bat
```

☐ Script ran successfully

**Option B: Manual commit**

```bash
git add .
git commit -m "fix: Configure Vercel deployment and fix env variables"
git push origin main
```

☐ Committed and pushed

---

## ☐ STEP 4: MONITOR DEPLOYMENT

☐ Go to Vercel Dashboard → **Deployments**
☐ Watch the build progress (2-5 minutes)
☐ Check for any errors in build logs
☐ Wait for "Deployment Ready" message

---

## ☐ STEP 5: VERIFY DEPLOYMENT

☐ Visit: https://agent-bap3k3x86-first-intern.vercel.app
☐ Hard refresh: **Ctrl + Shift + R**
☐ Open DevTools (F12) → **Network** tab
☐ Try to login or use a feature
☐ Check API calls go to backend (not localhost)
☐ Check **Console** tab for errors (should be clean)

---

## ☐ STEP 6: FUNCTIONAL TESTING

☐ Login works correctly
☐ Dashboard loads with latest UI
☐ Navigation works
☐ Features work (send email, view data, etc.)
☐ No CORS errors
☐ No console errors
☐ Test on different browser/incognito

---

## ☐ TROUBLESHOOTING (IF NEEDED)

### If still showing old version:

☐ Clear browser cache completely
☐ Try incognito/private window
☐ Check Vercel deployment status (should be "Ready")
☐ Verify build completed successfully

### If API calls failing:

☐ Verify NEXT_PUBLIC_API_URL in Vercel dashboard
☐ Test backend URL directly in browser
☐ Check backend CORS includes Vercel URL
☐ Check backend is running and accessible

### If build failing:

☐ Read Vercel build logs for specific error
☐ Test build locally: `cd frontend && npm run build`
☐ Check for TypeScript/syntax errors

---

## 📝 NOTES SECTION

**My Backend URL:**

---

**Deployment Started At:**

---

**Deployment Completed At:**

---

**Any Errors Encountered:**

---

---

---

**Resolution:**

---

---

---

---

## 🎉 DEPLOYMENT COMPLETE!

☐ All checks passed
☐ Site showing latest changes
☐ All features working
☐ No errors in console
☐ Mobile/desktop tested

**Date Completed:** ******\_\_\_******

**Time Taken:** ******\_\_\_****** minutes

---

**Keep this checklist for future deployments! 📌**
