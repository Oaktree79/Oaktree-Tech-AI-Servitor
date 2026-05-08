#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP="$ROOT/release/AI Serviter.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>CFBundleName</key><string>AI Serviter</string>
<key>CFBundleIdentifier</key><string>com.aiserviter.app</string>
<key>CFBundleVersion</key><string>1.2.0</string>
<key>CFBundleExecutable</key><string>ai-serviter-launcher</string>
</dict></plist>
EOF
cat > "$APP/Contents/MacOS/ai-serviter-launcher" <<'EOF'
#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
bash "$ROOT/installer/macos/install_one_click.command"
EOF
chmod +x "$APP/Contents/MacOS/ai-serviter-launcher"
