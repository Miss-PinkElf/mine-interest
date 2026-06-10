---
name: electron-local-cache-install
description: Handle Electron binary download failures during `npm install`, `pnpm install`, or other package-manager installs when `node_modules/electron` fails in `install.js` or `@electron/get`. Use when the exact Electron zip is already available locally and Codex needs a project-scoped cache-based fix on Windows, macOS, or Linux/WSL without changing global npm config.
---

# Electron Local Cache Install

Use Electron's local cache instead of retrying failed downloads.

## Confirm the failure type

Read the install output first.

Use this skill only when the failure is the Electron binary download stage, for example:

- `npm error path .../node_modules/electron`
- `npm error command ... node install.js`
- `ReadError: The server aborted pending request`
- `ECONNRESET`
- `ETIMEDOUT`
- other `@electron/get` download errors

Do not use this skill for TypeScript, Vite, Electron Forge, or app runtime failures.

## Align version and artifact name

Match the local zip exactly to the Electron version in `package.json`.

Example:

- dependency: `"electron": "40.4.1"`
- local zip: `electron-v40.4.1-darwin-arm64.zip`

If the version or filename does not match, the cache will not be reused.

Pick the artifact that matches the current machine:

- Windows x64: `electron-v<version>-win32-x64.zip`
- Windows arm64: `electron-v<version>-win32-arm64.zip`
- macOS Apple Silicon: `electron-v<version>-darwin-arm64.zip`
- macOS Intel: `electron-v<version>-darwin-x64.zip`
- Linux x64: `electron-v<version>-linux-x64.zip`

## Choose the cache root by platform

Detect the current platform before copying files.

- macOS: `~/Library/Caches/electron/`
- Linux: `${XDG_CACHE_HOME:-~/.cache}/electron/`
- Windows: `$env:LOCALAPPDATA\\electron\\Cache\\`

Use the platform that is actually running the install. Do not seed the macOS cache while installing on Windows, and vice versa.

## Compute the SHA-256 checksum

Electron cache folders are keyed by checksum.

On macOS or Linux:

```bash
shasum -a 256 /path/to/electron-v40.4.1-darwin-arm64.zip
```

On Windows PowerShell:

```powershell
(Get-FileHash "C:\path\to\electron-v40.4.1-win32-x64.zip" -Algorithm SHA256).Hash.ToLower()
```

Use the resulting lowercase hash as the cache subdirectory name.

## Seed the cache

Create `<cacheRoot>/<sha256>/` and copy the zip into that folder with its original filename.

macOS example:

```bash
SHA256="<sha256>"
ZIP="/path/to/electron-v40.4.1-darwin-arm64.zip"
mkdir -p "$HOME/Library/Caches/electron/$SHA256"
cp "$ZIP" "$HOME/Library/Caches/electron/$SHA256/electron-v40.4.1-darwin-arm64.zip"
```

Linux example:

```bash
SHA256="<sha256>"
ZIP="/path/to/electron-v40.4.1-linux-x64.zip"
CACHE_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/electron"
mkdir -p "$CACHE_ROOT/$SHA256"
cp "$ZIP" "$CACHE_ROOT/$SHA256/electron-v40.4.1-linux-x64.zip"
```

Windows PowerShell example:

```powershell
$sha256 = "<sha256>"
$zip = "C:\path\to\electron-v40.4.1-win32-x64.zip"
$cacheDir = Join-Path $env:LOCALAPPDATA "electron\Cache\$sha256"
New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
Copy-Item $zip (Join-Path $cacheDir "electron-v40.4.1-win32-x64.zip") -Force
```

If the zip is for macOS but the current install is on Windows, store it only in the macOS cache on the Mac machine. Keep platform-specific artifacts separate.

## Re-run install with the same package manager

After seeding the cache, rerun the install command that the project normally uses.

Examples:

```bash
npm install --prefix frontend
```

```bash
pnpm install --dir frontend
```

Use the same package manager that owns the lockfile when possible.

## Verify success

A successful outcome should satisfy all of these:

1. install completes without another Electron download failure
2. the `electron` package exists under the target project's `node_modules`
3. the app's next step starts working, such as `npm run start`, `pnpm run start`, or a build command

Optional checks:

- confirm the zip filename exactly matches the current platform and architecture
- confirm the cache file exists under the expected checksum directory
- confirm `package.json` still pins the version that matches the zip

## Fallbacks

Only fall back to mirror or proxy configuration if the exact local zip is not available.

Possible controls:

- `ELECTRON_MIRROR`
- `ELECTRON_CUSTOM_DIR`
- `ELECTRON_CUSTOM_FILENAME`
- `ELECTRON_GET_USE_PROXY`
- `electron_config_cache`

Prefer local cache seeding over global npm config changes when the problem is isolated to one project.
