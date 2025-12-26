# Fix Map on Render - Database Issue

## 🔴 The Problem

**Map works locally but not on Render because:**
- Your local database has theater coordinates
- Render database is empty or doesn't have coordinates
- Need to populate Render database with data

---

## ✅ Solution 1: Add Sample Data to Render (Quick Test)

**Via Render Shell:**

1. **Go to Render dashboard** → Your service → **"Shell"**
2. **Run this to add sample data:**

```python
from app import app, db
from models import Theater, Show, Person, Production, Credit

with app.app_context():
    # Add theater with coordinates
    theater = Theater.query.filter_by(name="John W. Engeman Theater").first()
    if not theater:
        theater = Theater(
            name="John W. Engeman Theater",
            latitude="40.9012",
            longitude="-73.3434",
            city="Northport",
            state="NY"
        )
        db.session.add(theater)
    else:
        theater.latitude = "40.9012"
        theater.longitude = "-73.3434"
        theater.city = "Northport"
        theater.state = "NY"
    
    db.session.commit()
    print("Theater coordinates added!")
```

---

## ✅ Solution 2: Run add_sample_data.py on Render

**If you have `add_sample_data.py` script:**

1. **Upload it to Render** (if not already there)
2. **In Render Shell, run:**

```bash
python add_sample_data.py
```

**This will populate the database with sample data including coordinates.**

---

## ✅ Solution 3: Sync from Joomla (Best for Production)

**If Joomla database has theater coordinates:**

1. **In Render Shell, run:**

```python
from joomla_sync import sync_theaters_from_joomla
sync_theaters_from_joomla()
```

**This will:**
- Connect to Joomla database
- Copy all theaters with coordinates
- Update your Render database

**But first, make sure environment variables are set:**
- `JOOMLA_DB_HOST`
- `JOOMLA_DB_USER`
- `JOOMLA_DB_PASSWORD`
- `JOOMLA_DB_NAME`
- `JOOMLA_THEATER_TABLE`

---

## ✅ Solution 4: Export from Local and Import to Render

**If you want to copy your local data:**

1. **On your local computer, export data:**

```python
# Run locally
from app import app, db
from models import Theater
import json

with app.app_context():
    theaters = Theater.query.all()
    data = []
    for t in theaters:
        if t.latitude and t.longitude:
            data.append({
                'name': t.name,
                'latitude': t.latitude,
                'longitude': t.longitude,
                'city': t.city,
                'state': t.state
            })
    print(json.dumps(data, indent=2))
```

2. **Copy the output**
3. **In Render Shell, import:**

```python
from app import app, db
from models import Theater
import json

data = [...]  # Paste your JSON data here

with app.app_context():
    for item in data:
        theater = Theater.query.filter_by(name=item['name']).first()
        if theater:
            theater.latitude = item['latitude']
            theater.longitude = item['longitude']
            theater.city = item.get('city')
            theater.state = item.get('state')
        else:
            theater = Theater(
                name=item['name'],
                latitude=item['latitude'],
                longitude=item['longitude'],
                city=item.get('city'),
                state=item.get('state')
            )
            db.session.add(theater)
    db.session.commit()
    print("Data imported!")
```

---

## 🧪 Test After Fix

**After adding coordinates:**

1. **Visit actor page:** `https://playbill-app-test.onrender.com/public/actor/30`
2. **Map should now display**
3. **If still not showing:**
   - Check browser console (F12) for errors
   - Check Render logs
   - Verify coordinates are in database

---

## 📋 Quick Checklist

**To fix the map on Render:**

- [ ] Database is initialized (tables created)
- [ ] Theaters have latitude/longitude coordinates
- [ ] Coordinates are valid numbers
- [ ] Template is updated (already done)
- [ ] App is restarted after changes

---

## 🎯 Recommended Action

**For testing on Render:**

1. **Use Solution 1** - Add coordinates manually via Shell
2. **Or use Solution 2** - Run `add_sample_data.py` if you have it

**For production:**

1. **Use Solution 3** - Sync from Joomla database
2. **This ensures all theaters have coordinates**

---

## 💡 Why This Happened

**Local vs Render:**
- **Local:** You have data with coordinates (from testing)
- **Render:** Fresh database, no data yet
- **Solution:** Populate Render database with data

**The code works fine - it's just a data issue!**

