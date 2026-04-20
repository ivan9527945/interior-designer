#!/usr/bin/env bash
# RenderStudio Agent macOS .pkg 打包
set -euo pipefail

AGENT_VERSION="0.1.0"
BUNDLE_ID="com.renderstudio.agent"
DIST_DIR="dist/renderstudio_agent"
PKG_DIR="dist/pkg"

echo "=== [1/4] PyInstaller 打包 ==="
pyinstaller \
  --onedir \
  --name renderstudio-agent \
  --hidden-import renderstudio_agent \
  --add-data "renderstudio_agent/sketchup/ruby_scripts:renderstudio_agent/sketchup/ruby_scripts" \
  --add-data "renderstudio_agent/vray/presets:renderstudio_agent/vray/presets" \
  renderstudio_agent/__main__.py

echo "=== [2/4] LaunchAgent plist 複製 ==="
mkdir -p "$DIST_DIR/LaunchAgents"
sed "s/VERSION_PLACEHOLDER/$AGENT_VERSION/g" installer/launch_agent.plist \
  > "$DIST_DIR/LaunchAgents/com.renderstudio.agent.plist"

echo "=== [3/4] pkgbuild ==="
mkdir -p "$PKG_DIR"
pkgbuild \
  --root "$DIST_DIR" \
  --identifier "$BUNDLE_ID" \
  --version "$AGENT_VERSION" \
  --install-location "/Applications/RenderStudio" \
  "$PKG_DIR/renderstudio-agent-$AGENT_VERSION.pkg"

echo "=== [4/4] 完成 ==="
echo "pkg: $PKG_DIR/renderstudio-agent-$AGENT_VERSION.pkg"
echo "若需 notarize，執行: bash installer/notarize.sh $PKG_DIR/renderstudio-agent-$AGENT_VERSION.pkg"
