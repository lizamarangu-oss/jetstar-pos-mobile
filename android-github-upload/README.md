# JETSTAR POS - Android Build via GitHub Actions

## Quick Start - Get Your APK in 5 Minutes! 🚀

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `jetstar-pos-mobile`
3. Description: `JETSTAR POS Android Application`
4. Choose **Public** (free GitHub Actions minutes)
5. Click **Create repository**

### Step 2: Upload Files to GitHub

**Option A - Using GitHub Web Interface:**

1. On your new repo page, click **"uploading an existing file"**
2. Drag and drop these files:
   - `jetstar_pos_mobile.py`
   - `buildozer.spec`
   - `.gitignore`
   - `.github/workflows/build-android.yml`
3. Click **Commit changes**

**Option B - Using Git Command Line:**

```powershell
# Initialize git in your project folder
cd D:\myimportantsoftwares\jetstarpos\jetpos
git init
git add jetstar_pos_mobile.py buildozer.spec .gitignore .github/
git commit -m "Initial commit - JETSTAR POS Android"

# Add your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/jetstar-pos-mobile.git
git branch -M main
git push -u origin main
```

### Step 3: Build APK Automatically

1. **GitHub Actions will start automatically!**
2. Go to your repo → **Actions** tab
3. You'll see "Build Android APK" running
4. Wait ~15-20 minutes for build to complete
5. Build status: ⏳ Orange = Building, ✅ Green = Success

### Step 4: Download Your APK

**Option 1 - From Artifacts (Available Immediately):**
1. Click on the completed workflow run
2. Scroll down to **Artifacts**
3. Download `jetstar-pos-apk.zip`
4. Extract and get your APK!

**Option 2 - From Releases (If pushed to main branch):**
1. Go to your repo → **Releases** (right sidebar)
2. Latest release will be there
3. Download the APK file directly

### Step 5: Install on Android

1. Transfer APK to your Android device
2. Open the APK file
3. Allow "Install from Unknown Sources" if prompted
4. Install and enjoy! 📱

---

## File Structure for GitHub

```
jetstar-pos-mobile/
├── .github/
│   └── workflows/
│       └── build-android.yml    ← GitHub Actions config
├── jetstar_pos_mobile.py        ← Main app file
├── buildozer.spec               ← Android build config
├── .gitignore                   ← Ignore build files
└── README.md                    ← This file (optional)
```

---

## Troubleshooting

### Build Failed?

**Check the Actions log:**
1. Go to Actions tab
2. Click on the failed run
3. Read the error message

**Common fixes:**
- Ensure `buildozer.spec` has correct `source.include_exts = py`
- Check that `jetstar_pos_mobile.py` is in the root folder
- Make sure workflow file is in `.github/workflows/` folder

### Need to Rebuild?

**Manual trigger:**
1. Go to **Actions** tab
2. Select "Build Android APK" workflow
3. Click **Run workflow** button
4. Click green **Run workflow**

### Want Faster Builds?

Use **self-hosted runner** with cached dependencies:
- First build: ~15-20 minutes
- Subsequent builds: ~5-8 minutes

---

## What the GitHub Action Does

1. ✅ Sets up Ubuntu Linux environment
2. ✅ Installs Python 3.11
3. ✅ Installs all Android build dependencies (Java, SDK, etc.)
4. ✅ Installs Buildozer and Cython
5. ✅ Builds your APK using `buildozer android debug`
6. ✅ Uploads APK as downloadable artifact
7. ✅ Creates a GitHub Release (if pushed to main branch)

---

## Alternative: Use Replit

If GitHub Actions doesn't work:

1. Go to https://replit.com
2. Create new Repl → Import from GitHub
3. Paste your repo URL
4. Open Shell and run:
   ```bash
   pip install buildozer cython
   buildozer android debug
   ```
5. Download APK from `bin/` folder

---

## App Features

✅ Dashboard with statistics
✅ POS/Sell screen with cart
✅ Stock management
✅ Expenses tracking
✅ Sales reports
✅ SQLite database
✅ Touch-optimized interface
✅ Professional design

---

## Support

- **Desktop Version**: Already working as `JETSTAR_POS_Complete.exe`
- **Mobile Preview**: Run `python jetstar_pos_mobile.py` on desktop
- **Build Locally**: Use WSL Ubuntu + Buildozer (see ANDROID_BUILD.md)

---

## Build Configuration

Edit `buildozer.spec` to customize:
- App name: `title = JETSTAR POS`
- Package name: `package.name = jetstarpos`
- Version: `version = 1.0`
- Permissions: `android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE`
- Icon: Add `icon.filename = icon.png`

---

**Ready to build? Push to GitHub and watch the magic happen!** ✨
