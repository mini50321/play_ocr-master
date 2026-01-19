# Joomla Playbill Show Profile Module - Complete User Guide

## Overview

The **Playbill Show Profile Module** (MOD_PLAYBILL_SHOW) is a Joomla module that automatically displays cast, crew, and creative team information for a specific production directly within Joomla articles. The module pulls data dynamically from the Playbill database and does not store any data in Joomla.

---

## Module Information

**Module Name:** `MOD_PLAYBILL_SHOW` (Playbill Show Profile Module)

**Module Type:** Site Module (Frontend)

**Module Location:** `joomla_profile_modules/mod_playbill_show/`

**Purpose:** Display full show profile with cast, crew, and creative team from the most recent production

---

## Where It's Used

The Playbill Show Profile Module is designed to be used **inside Joomla articles**. It displays cast and crew information for a specific show production.

### Typical Use Case

1. A Joomla article already exists about a musical/show (e.g., "A Christmas Carol The Musical")
2. The article contains editorial content (text, images, etc.)
3. The module is embedded in the article to automatically display the cast and crew data
4. The module appears within the article content, typically after the editorial content

---

## How to Configure the Module

### Step 1: Access the Module

1. Log in to Joomla Administrator
2. Navigate to **Extensions → Modules**
3. Find **"Playbill Show Profile Module"** in the list
4. Click on the module name to edit it

### Step 2: Configure Basic Settings

#### Module Tab
- **Title:** (Optional) You can set a title or leave it blank to hide the module title
- **Show Title:** Choose whether to display the module title on the frontend
- **Position:** See "Displaying the Module" section below for position options
- **Status:** Set to **Published**

#### Menu Assignment Tab
- **Module Assignment:** 
  - **"On all pages"** - Module appears on all pages (useful for {loadposition} method)
  - **"Only on the pages selected"** - Select specific articles/menu items

#### Options Tab (Module Parameters)

**1. Module Enabled**
- **Value:** Yes (enabled) or No (disabled)
- **Default:** Yes
- **Description:** Enable or disable this module. When disabled, the module will not display any content.

**2. Default Show ID** ⭐ **REQUIRED**
- **Value:** Enter a numeric Show ID (e.g., `7`, `9`, `12`)
- **Default:** `0`
- **Description:** Default Show ID to display. Can be overridden by URL parameter `?show_id=123`. Set to 0 to require URL parameter.
- **How to Find Show ID:**
  1. Go to the Playbill app: `https://www.broadwayandmain.com/playbill_app/public/show/[ID]`
  2. Look at the URL - the number at the end is the Show ID
  3. Or check the Flask admin dashboard for the Show ID
- **Important:** The module prioritizes the module parameter over URL parameters to avoid conflicts with article IDs

**3. API Base URL**
- **Value:** `https://www.broadwayandmain.com/playbill_app/api/joomla`
- **Default:** Pre-filled with the correct URL
- **Description:** Base URL for the Playbill API. Usually does not need to be changed.

**4. Public Base URL**
- **Value:** `https://www.broadwayandmain.com/playbill_app/public`
- **Default:** Pre-filled with the correct URL
- **Description:** Base URL for public profile pages. Usually does not need to be changed.

**5. Profile Base URL**
- **Value:** (Optional) Leave empty or enter a Joomla menu item URL
- **Example:** `index.php?Itemid=533` (where 533 is your Joomla menu item ID)
- **Description:** Base URL for profile pages displayed in Joomla. If left empty, uses the Public Base URL.

**6. Actor Profile URL**
- **Value:** (Optional) Leave empty or enter a Joomla menu item URL
- **Example:** `index.php/actor-profile`
- **Description:** URL for actor profile links. Use Joomla menu item to display actor profiles in Joomla, or leave empty to use Profile Base URL.

### Step 3: Save the Module

Click **"Save"** or **"Save & Close"** to save your configuration.

---

## How to Display the Module in Articles

There are two main methods to display the module in your article content:

### Method 1: Using {loadposition} Syntax (Recommended)

This method allows you to embed the module directly in your article content, exactly where you want it.

#### Step 1: Enable the "Content - Load Modules" Plugin

1. Go to **Extensions → Plugins**
2. Search for: **"Content - Load Modules"**
3. Click on it to edit
4. Set **Status** to **"Enabled"**
5. Save

#### Step 2: Create a Custom Module Position

1. In your **Playbill Show Profile Module** settings
2. In the **Position** field, type a new position name: `playbill-content` (or any name you prefer)
3. Save the module

#### Step 3: Add Module to Article Content

1. Go to **Content → Articles**
2. Edit your article (e.g., "A Christmas Carol")
3. In the article editor, go to the end of your article text (or wherever you want the module to appear)
4. Add this line:
   ```
   {loadposition playbill-content}
   ```
   **Note:** Replace `playbill-content` with the exact position name you used in Step 2
5. Save the article

**Result:** The module will appear exactly where you placed `{loadposition playbill-content}` in your article content.

### Method 2: Using Template Positions

If you prefer to display the module in a template position (above or below article content):

1. Set the module **Position** to one of these:
   - `content-top` (appears above article content)
   - `content-bottom` (appears below article content)
   - `main-top` or `main-bottom` (if available in your template)
   - Or check your template's available positions

2. In **Menu Assignment**, assign the module to your specific article/menu item

3. Save the module

**Result:** The module will appear in the template position you selected, relative to the article content.

---

## Exact Configuration Example

### Example: Displaying "A Christmas Carol" (Show ID: 9)

**Scenario:** You want to display cast and crew for "A Christmas Carol The Musical" (Show ID: 9) in an article.

**Steps:**

1. **Enable Plugin:**
   - Extensions → Plugins → "Content - Load Modules" → Enable

2. **Configure Module:**
   - Extensions → Modules → "Playbill Show Profile Module"
   - **Position:** `playbill-content`
   - **Default Show ID:** `9`
   - **Module Enabled:** Yes
   - **Status:** Published
   - **Menu Assignment:** "On all pages" (or assign to specific article)
   - Save

3. **Add to Article:**
   - Content → Articles → Edit "A Christmas Carol"
   - At the end of article text, add: `{loadposition playbill-content}`
   - Save article

4. **Clear Cache:**
   - System → Clear Cache → Clear all

5. **View Article:**
   - Visit the article page
   - Cast and crew information should appear where you placed `{loadposition}`

---

## Reusing the Module Across Multiple Articles

### ✅ Confirmation: One Module Can Be Reused

**Yes, you can reuse the same module across unlimited articles, but with one important consideration:**

### Option 1: Single Module Instance (Same Show ID for All Articles)

If you want to display the **same show** (same Show ID) on multiple articles:

1. Create one module instance
2. Set the **Default Show ID** (e.g., `9`)
3. Set **Position** to a custom position (e.g., `playbill-content`)
4. In **Menu Assignment**, set to **"On all pages"**
5. In each article, add: `{loadposition playbill-content}`
6. Save

**Result:** The same show data will appear on all articles that include `{loadposition playbill-content}`.

### Option 2: Multiple Module Instances (Different Show IDs)

If you want to display **different shows** on different articles:

1. Create multiple instances of the Playbill Show Profile Module
   - **Module Instance 1:** Default Show ID = `7` (Sister Act), Position = `playbill-sister-act`
   - **Module Instance 2:** Default Show ID = `9` (A Christmas Carol), Position = `playbill-christmas-carol`
   - **Module Instance 3:** Default Show ID = `12` (Another Show), Position = `playbill-show-12`
   - And so on...

2. In each article, use the corresponding position:
   - Article 1: `{loadposition playbill-sister-act}`
   - Article 2: `{loadposition playbill-christmas-carol}`
   - Article 3: `{loadposition playbill-show-12}`

**Result:** Each article displays the cast/crew for its specific show.

### ⭐ Key Point: Only Swap the Show ID

**For each article, you only need to:**
1. Create or edit a module instance
2. **Change the Default Show ID** to match the show for that article
3. Set a unique **Position** name (if using multiple instances)
4. Add `{loadposition position-name}` to the article
5. Save

**That's it!** The module handles everything else automatically (fetching data, displaying cast/crew, formatting, etc.).

---

## What the Module Displays

When configured correctly, the module automatically displays:

1. **Show Title** (from Playbill database)
2. **Theater Name** (from Playbill database)
3. **Year** (production year)
4. **Cast** (grouped by category)
   - Actor names (linked to actor profiles)
   - Roles
   - Equity indicators (*)
5. **Crew** (grouped by category)
   - Crew member names (linked to profiles)
   - Roles/positions
6. **Creative Team** (grouped by category)
   - Creative team member names (linked to profiles)
   - Roles/positions

### View Options

The module provides two viewing options:
- **By Category:** Credits grouped by category (Cast, Crew, Creative, etc.)
- **Alphabetical:** All credits sorted alphabetically by person name

---

## Important: Show ID Configuration

### ⚠️ Critical Issue: Article ID vs Show ID

**Problem:** The module was previously reading `id` from the URL, which could conflict with article IDs.

**Solution:** The module now prioritizes the **module parameter** (Default Show ID) over URL parameters.

**How it works:**
1. **First Priority:** Module parameter "Default Show ID" (e.g., `9`)
2. **Second Priority:** URL parameter `?show_id=123` (if module parameter is 0)
3. **Never uses:** URL parameter `?id=XXX` (to avoid conflicts with article IDs)

**Best Practice:** Always set the **Default Show ID** in module settings. Don't rely on URL parameters.

---

## Troubleshooting

### Module Not Displaying

**Check these items in order:**

1. **Plugin Enabled:**
   - Extensions → Plugins → "Content - Load Modules" → Must be **Enabled**

2. **Module Status:**
   - Module must be **Published**
   - **Module Enabled** must be **Yes**

3. **Show ID Set:**
   - **Default Show ID** must be set to a valid number (not 0)
   - Verify Show ID exists: `https://www.broadwayandmain.com/playbill_app/public/show/[ID]`

4. **Position Name Matches:**
   - Position in module settings must match exactly in `{loadposition}` tag
   - Case-sensitive: `playbill-content` ≠ `Playbill-Content`

5. **Clear Cache:**
   - System → Clear Cache → Clear all cache types

### Show ID Not Found Error

**If you see:** "Show not found or error loading data for Show ID: X"

**Check:**
1. Verify the Show ID exists in the Playbill database
2. Test the API directly: `https://www.broadwayandmain.com/playbill_app/api/joomla/show/[ID]`
3. You should see JSON data, not an error
4. Check Joomla error logs: **System → System Information → Log Files**

### Module Appears But Shows Error

**If module appears but shows an error message:**

1. **Check Show ID:**
   - Make sure Default Show ID is correct
   - Test the Show ID in Playbill app URL

2. **Check API Connection:**
   - Verify API Base URL is correct
   - Test API endpoint directly in browser

3. **Check Error Logs:**
   - System → System Information → Log Files
   - Look for errors with "mod_playbill_show" or "Playbill"

### {loadposition} Not Working

**If `{loadposition}` tag doesn't display the module:**

1. **Verify Plugin:**
   - Extensions → Plugins → "Content - Load Modules" → Must be **Enabled**
   - Check plugin settings - make sure it's enabled for your user group

2. **Check Position Name:**
   - Position name in module must match exactly in `{loadposition}` tag
   - No spaces, case-sensitive

3. **Check Module Assignment:**
   - If using "Only on the pages selected", make sure the article is selected
   - Or use "On all pages" for testing

4. **View Page Source:**
   - Right-click → View Page Source
   - Search for: `Playbill Show Profile Module START`
   - If you see it, module is loading but might have an error
   - If you don't see it, module isn't being called

### No Cast/Crew Displayed

**Possible reasons:**
1. The show exists but has no credits/crew assigned in the Playbill database
2. The API is not accessible (check API Base URL)
3. Check Joomla error logs for API connection errors

---

## Quick Reference

### Minimum Required Steps:

1. **Enable Plugin:**
   - Extensions → Plugins → "Content - Load Modules" → Enable

2. **Configure Module:**
   - Set **Default Show ID** (e.g., `9`)
   - Set **Position** (e.g., `playbill-content`)
   - Set **Module Enabled** = Yes
   - Set **Status** = Published
   - Save

3. **Add to Article:**
   - Edit article
   - Add `{loadposition playbill-content}` where you want module to appear
   - Save article

4. **Clear Cache:**
   - System → Clear Cache

5. **View Article:**
   - Module should appear where you placed `{loadposition}` tag

### Configuration Checklist:

- [ ] "Content - Load Modules" plugin is enabled
- [ ] Module is published
- [ ] Module Enabled = Yes
- [ ] Default Show ID is set (not 0)
- [ ] Position is set (e.g., `playbill-content`)
- [ ] `{loadposition}` tag is added to article
- [ ] Position name matches exactly
- [ ] Cache is cleared
- [ ] Show ID exists in Playbill database

---

## Technical Details

### Module Files
- **Main File:** `mod_playbill_show.php`
- **Template:** `tmpl/default.php`
- **Helper:** `helper/mod_playbill_show.php`
- **Configuration:** `mod_playbill_show.xml`

### API Endpoint
The module calls: `{API_BASE_URL}/show/{SHOW_ID}`

Example: `https://www.broadwayandmain.com/playbill_app/api/joomla/show/9`

### Data Source
- All data is fetched **dynamically** from the Playbill Flask application
- **No data is stored** in Joomla database
- Data is retrieved in real-time when the page loads

### Show ID Priority
1. **Module Parameter:** "Default Show ID" (highest priority)
2. **URL Parameter:** `?show_id=123` (only if module parameter is 0)
3. **Never uses:** `?id=XXX` (to avoid conflicts with article IDs)

---

## Summary

✅ **Module Name:** MOD_PLAYBILL_SHOW (Playbill Show Profile Module)

✅ **Where It's Used:** Inside Joomla articles using `{loadposition}` syntax

✅ **Configuration:** 
- Set **Default Show ID** (numeric ID from Playbill app)
- Set **Position** (custom position name)
- Enable "Content - Load Modules" plugin
- Add `{loadposition position-name}` to article

✅ **Reusability:** 
- One module instance can be assigned to multiple articles (same Show ID)
- Multiple module instances can be created (different Show IDs for different articles)
- **You only need to swap the Default Show ID** for each article

✅ **What It Does:** Automatically displays cast, crew, and creative team for the specified show

---

## Support

For issues or questions:
1. Check Joomla error logs: **System → System Information → Log Files**
2. Verify Show ID exists in Playbill app
3. Check API connectivity: Test `https://www.broadwayandmain.com/playbill_app/api/joomla/show/[ID]`
4. Ensure "Content - Load Modules" plugin is enabled
5. Verify position name matches exactly in `{loadposition}` tag
6. Clear Joomla cache after making changes

---

**Document Version:** 2.0  
**Last Updated:** January 2025  
**Module Version:** 1.0.0

