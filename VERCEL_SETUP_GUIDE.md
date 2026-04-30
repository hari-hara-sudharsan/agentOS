# ⚡ QUICK FIX - Vercel Dashboard Settings

## 🎯 MOST IMPORTANT - Environment Variables

Go to your Vercel project and add these EXACT environment variables:

### Vercel Dashboard → Settings → Environment Variables

Add these **for Production**:

| Variable Name                 | Value                              | Environment |
| ----------------------------- | ---------------------------------- | ----------- |
| `NEXT_PUBLIC_API_URL`         | **YOUR_BACKEND_URL** (see below)   | Production  |
| `NEXT_PUBLIC_AUTH0_DOMAIN`    | `hariharasudharsanj.us.auth0.com`  | Production  |
| `NEXT_PUBLIC_AUTH0_CLIENT_ID` | `7q73PbVm1krlqaqnKtGZbPJHXdfaIkHT` | Production  |
| `NEXT_PUBLIC_AUTH0_AUDIENCE`  | `https://agentos.local/api`        | Production  |
| `VERCEL_FORCE_NO_BUILD_CACHE` | `1`                                | Production  |

### 🚨 FIND YOUR BACKEND URL

Your backend URL should be one of:

- Railway: `https://[your-app-name].up.railway.app`
- Heroku: `https://[your-app-name].herokuapp.com`
- Custom domain: `https://api.yourdomain.com`
- Other: Check your backend deployment platform

**How to find it:**

1. Go to your Railway/backend hosting dashboard
2. Look for "Deployment URL" or "Public URL"
3. Copy that URL
4. Use it for `NEXT_PUBLIC_API_URL`

Example: `NEXT_PUBLIC_API_URL=https://agentos-backend-production.up.railway.app`

---

## 📋 Step-by-Step Checklist

### ✅ Step 1: Update Environment Variables (CRITICAL)

- [ ] Go to Vercel Dashboard
- [ ] Click your project
- [ ] Go to Settings → Environment Variables
- [ ] Add all 5 variables above
- [ ] **IMPORTANT**: Set "Environment" to "Production" only
- [ ] Click Save

### ✅ Step 2: Clear Build Cache

- [ ] In Vercel Dashboard → Settings
- [ ] Scroll to "Build & Development Settings"
- [ ] Find deployment cache section
- [ ] Click "Clear Cache" if available
- [ ] (Or just set `VERCEL_FORCE_NO_BUILD_CACHE=1` which we did above)

### ✅ Step 3: Trigger New Deployment

Two options:

**Option A: Push code (Recommended)**

```bash
git add .
git commit -m "fix: Configure Vercel deployment with proper env vars"
git push origin main
```

**Option B: Manual redeploy**

- [ ] Vercel Dashboard → Deployments
- [ ] Click latest deployment
- [ ] Click "..." menu → "Redeploy"
- [ ] **UNCHECK** "Use existing Build Cache"
- [ ] Click "Redeploy"

### ✅ Step 4: Verify Deployment

- [ ] Wait for build to complete (2-5 minutes)
- [ ] Visit your Vercel URL: https://agent-bap3k3x86-first-intern.vercel.app
- [ ] Open DevTools (F12) → Network tab
- [ ] Try to login or use a feature
- [ ] Check that API calls go to your backend URL (not localhost!)
- [ ] Hard refresh: `Ctrl + Shift + R`

### ✅ Step 5: Test Everything

- [ ] Login works
- [ ] Dashboard loads
- [ ] Features work (send email, etc.)
- [ ] No console errors
- [ ] No CORS errors

---

## 🐛 Still Not Working?

### Check 1: Is Backend Running?

```bash
# Test your backend URL
curl https://YOUR-BACKEND-URL.railway.app/
```

Should return: `{"message":"AgentOS Backend","status":"operational"}`

### Check 2: CORS Configuration

Make sure your backend `main.py` has the Vercel URL:

```python
origins = [
    "http://localhost:3000",
    "https://agent-bap3k3x86-first-intern.vercel.app"  # ← Your Vercel URL
]
```

### Check 3: Browser Console Errors

1. Open DevTools (F12)
2. Go to Console tab
3. Look for red errors
4. Share them if you need help

### Check 4: Vercel Build Logs

1. Vercel Dashboard → Deployments
2. Click the latest deployment
3. Click "Building" or "Build Logs"
4. Check for errors

---

## 📱 Mobile/Browser Cache Issues?

After deploying, users might still see the old version due to browser cache:

**Solution:**

1. Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Clear browser cache: Settings → Privacy → Clear browsing data
3. Incognito/Private window to test

---

## 🎉 Success Indicators

You'll know it's fixed when:

- ✅ Login redirects work correctly
- ✅ Dashboard shows your latest UI changes
- ✅ Network tab shows API calls to your backend (not localhost)
- ✅ No CORS errors in console
- ✅ All features work as expected

---

## 💡 Pro Tips for Future Deployments

1. **Never hardcode URLs** - Always use environment variables
2. **Test locally first** - Run `npm run build` locally before pushing
3. **Use Preview Deployments** - Vercel creates preview URLs for branches
4. **Set Preview env vars too** - Add env vars for "Preview" environment
5. **Monitor deployments** - Enable Vercel notifications on Discord/Slack

---

**Need the backend URL?** Check:

- Railway Dashboard → Your project → Settings → Domain
- Or wherever you deployed your FastAPI backend

**Backend not deployed yet?** Deploy it first, then come back and update `NEXT_PUBLIC_API_URL`!
