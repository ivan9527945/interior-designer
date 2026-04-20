#!/usr/bin/env bash
set -euo pipefail
PKG="$1"
BUNDLE_ID="com.renderstudio.agent"

# 需要環境變數: APPLE_ID, APPLE_TEAM_ID, APPLE_APP_PASSWORD
xcrun notarytool submit "$PKG" \
  --apple-id "$APPLE_ID" \
  --team-id "$APPLE_TEAM_ID" \
  --password "$APPLE_APP_PASSWORD" \
  --wait

xcrun stapler staple "$PKG"
echo "Notarize 完成: $PKG"
