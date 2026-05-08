#!/usr/bin/env bash
set -euo pipefail
APP_PATH="${1:-release/AI Serviter.app}"
IDENTITY="${APPLE_DEVELOPER_ID_APPLICATION:-Developer ID Application: YOUR NAME (TEAMID)}"
PROFILE="${APPLE_NOTARY_PROFILE:-ai-serviter-notary}"
codesign --force --deep --options runtime --sign "$IDENTITY" "$APP_PATH"
ditto -c -k --keepParent "$APP_PATH" "release/AI-Serviter-macOS.zip"
xcrun notarytool submit "release/AI-Serviter-macOS.zip" --keychain-profile "$PROFILE" --wait
xcrun stapler staple "$APP_PATH"
