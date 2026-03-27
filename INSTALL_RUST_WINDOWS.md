# Install Rust on Windows for Desktop App

## Method 1: Using Rustup Installer (Recommended)

1. **Download Rustup Installer**:
   - Visit: https://rustup.rs/
   - Click "Download rustup-init.exe (64-bit)"
   - Or direct link: https://win.rustup.rs/x86_64

2. **Run the Installer**:
   - Double-click `rustup-init.exe`
   - Follow the prompts (press Enter for default installation)
   - This will install Rust and Cargo

3. **Install Visual Studio C++ Build Tools** (Required):
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Or install Visual Studio Community with "Desktop development with C++" workload
   - Restart your terminal after installation

4. **Verify Installation**:
   ```powershell
   rustc --version
   cargo --version
   ```

## Method 2: Using Chocolatey (If you have Chocolatey)

```powershell
choco install rust
```

## Method 3: Using Scoop (If you have Scoop)

```powershell
scoop install rust
```

## After Installing Rust

### Option 1: Use the Helper Script (Easiest)

1. **Navigate to desktop app**:
   ```powershell
   cd F:\kannan\projects\CO_OS\apps\desktop
   ```

2. **Run the helper script**:
   ```powershell
   .\run-desktop.ps1
   ```

This script automatically adds Rust to your PATH and starts the app.

### Option 2: Manual Method

1. **Close and reopen your terminal** (PowerShell or CMD)
   - This is required for PATH changes to take effect

2. **Navigate to desktop app**:
   ```powershell
   cd F:\kannan\projects\CO_OS\apps\desktop
   ```

3. **Verify Rust is available**:
   ```powershell
   cargo --version
   rustc --version
   ```

4. **If cargo is not found**, add it to PATH for this session:
   ```powershell
   $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
   ```

5. **Install dependencies**:
   ```powershell
   pnpm install
   ```

6. **Run desktop app**:
   ```powershell
   pnpm tauri dev
   ```

## Troubleshooting

### "cargo not found" after installation
- Close and reopen your terminal
- Or restart your computer
- Check PATH: `$env:PATH` should include `.cargo\bin`

### "link.exe not found" error
- Install Visual Studio C++ Build Tools
- Restart terminal after installation

### WebView2 Missing
- Windows 10/11 usually have WebView2 pre-installed
- If missing, download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## Alternative: Use Web Interface

If you don't want to set up the desktop app, you can use the web interface which is already running:

**Web Interface**: http://localhost:3000

The web interface has all the same features as the desktop app.
