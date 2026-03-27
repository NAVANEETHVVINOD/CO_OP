# How to Run the Desktop App - Step by Step

## The Issue You Had

You were running `pnpm tauri dev` from the **root directory** (`F:\kannan\projects\CO_OS`).

The `tauri` command only works when you're in the **desktop app directory** (`F:\kannan\projects\CO_OS\apps\desktop`).

## Correct Way to Run Desktop App

### Step 1: Navigate to Desktop App Directory

```powershell
cd F:\kannan\projects\CO_OS\apps\desktop
```

### Step 2: Add Rust to PATH (if needed)

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
```

### Step 3: Run the Desktop App

```powershell
pnpm tauri dev
```

## All-in-One Command

Copy and paste this entire block:

```powershell
cd F:\kannan\projects\CO_OS\apps\desktop
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
pnpm tauri dev
```

## Or Use the Helper Script

```powershell
cd F:\kannan\projects\CO_OS\apps\desktop
.\run-desktop.ps1
```

## Why It Didn't Work

**What you did**:
```powershell
(base) PS F:\kannan\projects\CO_OS> pnpm tauri dev
# ❌ Wrong directory - you're in the root
```

**What you should do**:
```powershell
(base) PS F:\kannan\projects\CO_OS> cd apps/desktop
(base) PS F:\kannan\projects\CO_OS\apps\desktop> pnpm tauri dev
# ✅ Correct directory - you're in apps/desktop
```

## Directory Structure

```
F:\kannan\projects\CO_OS\           ← Root (where you were)
├── apps/
│   ├── desktop/                    ← Desktop app (where you need to be)
│   │   ├── package.json           ← Contains tauri script
│   │   ├── src-tauri/             ← Rust/Tauri code
│   │   └── run-desktop.ps1        ← Helper script
│   └── web/                        ← Web app
├── services/
└── ...
```

## Verification

After navigating to `apps/desktop`, verify you're in the right place:

```powershell
# Check current directory
Get-Location
# Should show: F:\kannan\projects\CO_OS\apps\desktop

# Check if package.json exists
Test-Path package.json
# Should show: True

# Check if tauri script exists in package.json
Get-Content package.json | Select-String "tauri"
# Should show: "tauri": "tauri"
```

## Alternative - Just Use Web App

If the desktop app is too much hassle, the web interface is already running:

**Web App**: http://localhost:3000

It has all the same features and requires no setup!

---

## Summary

**Problem**: Running `pnpm tauri dev` from wrong directory  
**Solution**: Navigate to `apps/desktop` first  
**Command**: `cd F:\kannan\projects\CO_OS\apps\desktop`  
**Then run**: `pnpm tauri dev`
