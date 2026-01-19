# Troubleshooting: Playbill Show Profile Module Not Displaying

## Quick Checklist

Based on your configuration (Show ID: 9, Position: top3, Status: Published), check these items:

---

## 1. ✅ Module Position Issue (MOST COMMON)

**Problem:** The module position `top3` might not be rendered in your article template.

**Solution:**
1. Go to **Extensions → Templates → Styles**
2. Find your active template (likely "Shaper Helix3 - Default")
3. Click on it to edit
4. Check if the position `top3` exists in your template
5. **Alternative:** Change the module position to a position that's definitely visible in articles:
   - `content-top` (usually appears above article content)
   - `content-bottom` (usually appears below article content)
   - `main-top` (if available)
   - Or check your template's available positions

**How to find available positions:**
- In Joomla admin, go to **Extensions → Modules**
- Click **"New"** or edit any module
- Look at the **Position** dropdown - these are all available positions
- Choose one that's commonly used for article content

---

## 2. ✅ Menu Assignment Issue

**Problem:** The module might not be assigned to the article you're viewing.

**Solution:**
1. In the module configuration, go to the **"Menu Assignment"** tab
2. Check the **"Module Assignment"** setting:
   - If set to **"Only on the pages selected"**, make sure your article/menu item is selected
   - If set to **"On all pages"**, it should appear everywhere (but might still have position issues)
3. **For articles specifically:**
   - You need to create a **Menu Item** for the article first
   - Then assign the module to that menu item
   - Or use **"On all pages"** if you want it on all articles

**Steps to assign to a specific article:**
1. Create a menu item for your article (if not already created):
   - Go to **Menus → [Your Menu] → Add New Menu Item**
   - Menu Item Type: **Single Article**
   - Select your article
   - Save
2. In the module, go to **Menu Assignment** tab
3. Select **"Only on the pages selected"**
4. Select the menu item you just created
5. Save the module

---

## 3. ✅ Show ID Validation

**Problem:** Show ID 9 might not exist or have no data.

**Solution:**
1. Verify Show ID 9 exists:
   - Go to: `https://www.broadwayandmain.com/playbill_app/public/show/9`
   - If you get a 404 or "Show not found", the ID doesn't exist
   - Try a different Show ID that you know exists
2. Check if the show has productions:
   - Even if the show exists, it needs to have at least one production with credits
   - The module will display "No productions found" if there's no data

---

## 4. ✅ API Connection Issue

**Problem:** The module can't connect to the Playbill API.

**Solution:**
1. Verify API URL is correct:
   - Should be: `https://www.broadwayandmain.com/playbill_app/api/joomla`
   - Test the API directly:
     - Go to: `https://www.broadwayandmain.com/playbill_app/api/joomla/show/9`
     - You should see JSON data, not an error
2. Check Joomla error logs:
   - Go to **System → System Information → Log Files**
   - Look for errors related to "Playbill" or "mod_playbill_show"
   - Check for cURL errors or HTTP errors

---

## 5. ✅ Module Enabled Check

**Problem:** Module might be disabled even though it shows "Yes".

**Solution:**
1. Double-check the **"Module Enabled"** setting is set to **"Yes"** (green)
2. Make sure the module **Status** is **"Published"** (not Unpublished or Archived)
3. Check **"Start Publishing"** date - make sure it's not in the future
4. Check **"Finish Publishing"** date - make sure it's not in the past

---

## 6. ✅ Template Position Not Rendered

**Problem:** Your template might not render the `top3` position in article view.

**Solution:**
1. **Change the position** to one that's commonly rendered in articles:
   - Try: `content-top`, `content-bottom`, `main-top`, `main-bottom`
   - Or check your template documentation for article-specific positions
2. **For Helix3 template specifically:**
   - Helix3 has custom positions
   - Try positions like: `content-top`, `content-bottom`, `main-top`
   - Or use the Helix3 Layout Builder to add a custom position

---

## 7. ✅ Debug Mode

**Enable debug mode to see error messages:**

1. Go to **System → Global Configuration**
2. Go to **System** tab
3. Set **"Error Reporting"** to **"Maximum"**
4. Set **"Debug System"** to **"Yes"**
5. Save
6. Refresh your article page
7. Look for any error messages or debug output
8. Check the page source (View → Page Source) for any PHP errors

---

## Step-by-Step Fix (Recommended Order)

### Step 1: Change Module Position
1. Edit the module
2. Change **Position** from `top3` to `content-top` or `content-bottom`
3. Save
4. View your article - does it appear now?

### Step 2: Check Menu Assignment
1. If still not showing, go to **Menu Assignment** tab
2. Change to **"On all pages"** temporarily
3. Save
4. View any page - does it appear now?
5. If yes, then it's a menu assignment issue - assign it to your specific article

### Step 3: Verify Show ID
1. Test the Show ID directly:
   - Visit: `https://www.broadwayandmain.com/playbill_app/public/show/9`
2. If that works, test the API:
   - Visit: `https://www.broadwayandmain.com/playbill_app/api/joomla/show/9`
3. If both work, the issue is likely position or assignment

### Step 4: Check Template
1. If using Helix3, check the template positions
2. Try a different position that you know works
3. Or contact template support for available article positions

---

## Common Solutions Summary

| Issue | Solution |
|-------|----------|
| Module not visible | Change position to `content-top` or `content-bottom` |
| Module on wrong pages | Check Menu Assignment tab |
| Show not found | Verify Show ID exists in Playbill app |
| No data displayed | Check if show has productions with credits |
| API error | Verify API URL and check error logs |

---

## 8. ✅ Check if Module is Being Called

**Problem:** Module might not be executing at all.

**Solution:**
1. View the page source (Right-click → View Page Source)
2. Search for: `Playbill Show Profile Module START`
3. If you see this comment, the module is being called
4. If you don't see it, the module is not being executed (position or assignment issue)

**What to look for in page source:**
- `<!-- Playbill Show Profile Module START: Show ID = 9 -->` - Module is running
- Error messages starting with `<div class="playbill-error">` - Module found an issue
- Nothing at all - Module not being called (check position/assignment)

---

## 9. ✅ Check for JavaScript Errors

**Problem:** JavaScript errors might prevent the module from displaying properly.

**Solution:**
1. Open browser Developer Console (F12)
2. Check the **Console** tab for errors
3. Look for:
   - Red error messages
   - Yellow warnings
   - Any errors mentioning "Playbill" or the module
4. **Note:** SVG errors from other files (like `zrt_lookup_fy2021.html`) are usually unrelated to the Playbill module
5. If you see JavaScript errors related to the module, note them down

---

## Still Not Working?

If none of the above solutions work:

1. **Check Joomla Error Logs:**
   - System → System Information → Log Files
   - Look for errors with "mod_playbill_show" or "Playbill"
   - Check for cURL errors or HTTP errors

2. **Test with a Different Show ID:**
   - Try Show ID `7` (Sister Act) if you know it exists
   - This will help determine if it's a Show ID issue or a module issue

3. **Check Module File Permissions:**
   - Ensure module files are readable
   - Check that helper files exist

4. **Clear Joomla Cache:**
   - System → Clear Cache
   - Clear all cache types

5. **Check PHP Error Logs:**
   - Check your server's PHP error log
   - Look for PHP warnings or errors

6. **View Page Source:**
   - Right-click on the page → View Page Source
   - Search for "Playbill" to see if any module output exists
   - Look for error messages or debug comments

---

## Quick Test

To quickly test if the module works at all:

1. Create a new module instance
2. Set Show ID to `7` (or any known working Show ID)
3. Set Position to `content-top`
4. Set Menu Assignment to **"On all pages"**
5. Save
6. Visit any page on your site
7. If it appears, the module works - the issue is with position/assignment
8. If it doesn't appear, there's a deeper issue (API, Show ID, or module code)

---

**Need More Help?**
- Check Joomla error logs
- Verify Show ID in Playbill app
- Test API endpoint directly
- Try different module positions

