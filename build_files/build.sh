#!/bin/bash

set -ouex pipefail

# Save distro fields bootc-image-builder needs (ID, CPE_NAME, VERSION_ID)
BASE_OS_RELEASE=/tmp/os-release.base
cp /etc/os-release "${BASE_OS_RELEASE}"
# shellcheck disable=SC1090
. "${BASE_OS_RELEASE}"
BASE_VERSION_ID="${VERSION_ID:-44}"
BASE_ID="${ID:-fedora}"
BASE_ID_LIKE="${ID_LIKE:-fedora}"
BASE_CPE="${CPE_NAME:-cpe:/o:fedoraproject:fedora:${BASE_VERSION_ID}}"

# Copy the contents of system_files/ of the git repo to /
cp -avf "/ctx/system_files"/. /

# Branding names stay Barbakaï; keep a real Fedora/Bazzite ID so ISO builds work
sed -i "s/^VERSION_ID=.*/VERSION_ID=\"${BASE_VERSION_ID}\"/" /etc/os-release
sed -i "s/^ID=.*/ID=${BASE_ID}/" /etc/os-release
sed -i "s/^ID_LIKE=.*/ID_LIKE=\"${BASE_ID_LIKE}\"/" /etc/os-release
if grep -q '^CPE_NAME=' /etc/os-release; then
    sed -i "s|^CPE_NAME=.*|CPE_NAME=\"${BASE_CPE}\"|" /etc/os-release
else
    echo "CPE_NAME=\"${BASE_CPE}\"" >> /etc/os-release
fi

chmod 0755 /usr/bin/barbakai-info /usr/bin/barbakai-first-login /usr/bin/nexus-info /usr/libexec/barbakai-firstboot.sh

### Install packages

# Packages can be installed from any enabled yum repo on the image.
# RPMfusion repos are available by default in ublue main images

dnf5 install -y tmux plymouth-plugin-script btop

systemctl enable podman.socket
systemctl enable barbakai-firstboot.service

dnf5 config-manager setopt "terra-mesa".enabled=false
sed -i "/terra-mesa/,/^$/ s/^enabled=.*/enabled=0/" /etc/yum.repos.d/*.repo

# Keep a NextOS-named copy so leftover configs still resolve
if [[ -d /usr/share/plymouth/themes/barbakai ]]; then
    mkdir -p /usr/share/plymouth/themes/nextos
    cp -a /usr/share/plymouth/themes/barbakai/. /usr/share/plymouth/themes/nextos/ || true
fi

if command -v plymouth-set-default-theme; then
    plymouth-set-default-theme barbakai || plymouth-set-default-theme nextos || true
fi

mkdir -p /usr/share/barbakai
cp -rf /ctx/system_files/usr/share/barbakai/* /usr/share/barbakai/ 2>/dev/null || true

echo "Barbakaï OS branding applied"
