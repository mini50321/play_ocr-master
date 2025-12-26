# Fix TEST_MODE Not Working on Render

## 🔴 The Problem

**TEST_MODE is set to `true` but not working because:**
- The app needs to be **restarted** after changing environment variables
- The app was already running with the old value

---

## ✅ Solution: Restart the App

### Step 1: Verify Environment Variable

**In Render dashboard:**
1. Go to **"Environment"** (you're already there)
2. Check that `TEST_MODE` = `true` (you have it set correctly)

### Step 2: Restart the App

**You need to restart the app to pick up the new environment variable:**

**Option A: Manual Deploy (Easiest)**
1. In Render dashboard, go to your service
2. Click **"Manual Deploy"** button (top right)
3. Click **"Deploy latest commit"**
4. Wait for deployment to complete

**Option B: Via Settings**
1. Go to **"Settings"** in left sidebar
2. Scroll down to **"Deploy"** section
3. Click **"Clear build cache & deploy"**
4. Wait for deployment

**Option C: Just Wait**
- Render auto-deploys on code changes
- If you push new code, it will restart automatically

---

## 🧪 Step 3: Verify It's Working

**After restart, test it:**

1. **Visit your app:** `https://playbill-app-test.onrender.com`
2. **Try uploading a PDF:**
   - Go to upload page
   - Upload a test PDF
   - Should use mock data (no API call)
3. **Check logs:**
   - Go to **"Logs"** in Render
   - Look for: `"TEST MODE: Using mock data for..."`

**If you see that message, TEST_MODE is working!**

---

## 🔍 Why This Happens

**Environment variables are loaded when the app starts:**
- App starts → Reads environment variables → Stores in memory
- Changing variables in dashboard → Doesn't affect running app
- **Solution:** Restart app → Reads new variables

---

## ✅ Quick Fix

**Right now, do this:**

1. **In Render dashboard, click:** "Manual Deploy" (top right)
2. **Click:** "Deploy latest commit"
3. **Wait:** 2-3 minutes for deployment
4. **Test:** Upload a PDF - should use mock data now

**That's it!**

---

## 📝 Alternative: Check Current Value

**To verify the app sees the variable:**

1. **Go to:** "Shell" in Render dashboard
2. **Run:**
   ```python
   python -c "from config import Config; print('TEST_MODE:', Config.TEST_MODE)"
   ```
3. **Should print:** `TEST_MODE: True`

**If it prints `False`, the app hasn't restarted yet.**

---

## 🎯 Summary

**Problem:** App needs restart after changing environment variables
**Solution:** Click "Manual Deploy" to restart the app
**Result:** TEST_MODE will work after restart

**Do this now:**
1. Click "Manual Deploy"
2. Wait for deployment
3. Test upload - should use mock data

