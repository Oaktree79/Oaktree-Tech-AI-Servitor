#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
rm -rf linux-package
mkdir -p release linux-package/opt/ai-serviter linux-package/usr/local/bin
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude release --exclude linux-package "$ROOT/" linux-package/opt/ai-serviter/
else
  cp -R . linux-package/opt/ai-serviter/
fi
cat > linux-package/usr/local/bin/ai-serviter <<'EOF'
#!/usr/bin/env bash
cd /opt/ai-serviter
bash installer/linux/install_one_click.sh
EOF
chmod +x linux-package/usr/local/bin/ai-serviter
if command -v dpkg-deb >/dev/null 2>&1; then
  mkdir -p linux-package/DEBIAN
  cat > linux-package/DEBIAN/control <<'EOF'
Package: ai-serviter
Version: 1.2.0
Section: utils
Priority: optional
Architecture: all
Maintainer: AI Serviter
Description: AI Serviter autonomous development platform
EOF
  dpkg-deb --build linux-package release/ai-serviter_1.2.0_all.deb
else
  tar -czf release/ai-serviter-linux.tar.gz -C linux-package .
fi
