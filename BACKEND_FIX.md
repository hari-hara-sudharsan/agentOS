# Backend API Configuration Fix

## Current Status ✅

**Frontend Deployed**: https://agent-dlm5mgybv-first-intern.vercel.app/
**Backend URL**: https://agentos-backend-tjx6.onrender.com

## Issues Found & Fixed

### 1. CORS Configuration ✅ FIXED

Updated `backend/main.py` to include both Vercel URLs:

- https://agent-dlm5mgybv-first-intern.vercel.app (NEW deployment)
- https://agent-bap3k3x86-first-intern.vercel.app (OLD deployment)

### 2. Vercel Environment Variable ⚠️ NEEDS UPDATE

**Current Issue**: Frontend is trying to call the wrong backend URL

**Fix Required in Vercel Dashboard**:

1. Go to: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. **UPDATE** the `NEXT_PUBLIC_API_URL` variable:

```
Variable: NEXT_PUBLIC_API_URL
Value: https://agentos-backend-tjx6.onrender.com
Environment: Production (and Preview if needed)
```

5. **Click "Save"**
6. **Redeploy** using your deploy hook to apply the change

### 3. Backend Deployment Status

Your backend should be deployed on **Render.com** at:

```
https://agentos-backend-tjx6.onrender.com
```

**Test if it's running**:

```bash
curl https://agentos-backend-tjx6.onrender.com/
```

Expected response:

```json
{ "message": "AgentOS backend running" }
```

**If backend is NOT running:**

- Check your Render.com dashboard
- Make sure the service is deployed and not spun down (free tier)
- Check logs for any errors
- Verify environment variables are set in Render

---

## Quick Fix Steps

### Step 1: Update CORS in Backend (DONE ✅)

The backend `main.py` now includes both Vercel URLs.

### Step 2: Commit and Deploy Backend

```bash
cd backend
git add main.py
git commit -m "fix: Add new Vercel URL to CORS origins"
git push origin fresh-changes
```

Then deploy to Render (if auto-deploy is disabled):

- Go to Render.com dashboard
- Manual deploy or merge to main branch

### Step 3: Update Vercel Environment Variable

1. Vercel Dashboard → Settings → Environment Variables
2. Edit `NEXT_PUBLIC_API_URL`
3. Set to: `https://agentos-backend-tjx6.onrender.com`
4. Save and redeploy

### Step 4: Test Everything

1. Visit: https://agent-dlm5mgybv-first-intern.vercel.app/
2. Open DevTools (F12) → Network tab
3. Try to use a feature
4. Check API calls go to: `https://agentos-backend-tjx6.onrender.com/api/...`
5. Verify no CORS errors in console

---

## Expected API Endpoints

Your backend should respond to:

- `GET /` - Root endpoint (health check)
- `GET /api/health` - Health check
- `GET /api/integrations` - List integrations
- `POST /api/agent/run-task-stream` - Run agent task
- `GET /api/approvals` - Get pending approvals
- `GET /api/activity` - Get activity log

---

## Troubleshooting

### Issue: "CORS error" in browser console

**Solution**: Make sure backend CORS includes your Vercel URL (already fixed in main.py)

### Issue: "Failed to fetch" or network error

**Solution**:

1. Check backend is running (visit backend URL in browser)
2. Check Vercel env var is set correctly
3. Redeploy frontend after changing env var

### Issue: Backend responds with 404

**Solution**: Check API endpoint paths - they should start with `/api/`

### Issue: Render backend is "sleeping" (free tier)

**Solution**:

- First request will be slow (50+ seconds)
- Consider upgrading Render plan or using another hosting service
- Or accept the delay for free tier

---

## Files Modified

1. `backend/main.py` - Added new Vercel URL to CORS origins
2. This documentation file

## Next Steps

1. ✅ Backend CORS updated (done)
2. ⏳ Deploy backend to Render
3. ⏳ Update Vercel environment variable
4. ⏳ Test frontend → backend connection
5. ⏳ Verify all features work

---

**Once you update the Vercel environment variable and redeploy, everything should work! 🎉**
