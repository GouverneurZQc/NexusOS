#!/bin/bash

set -ouex pipefail

# Keep the base image version id before branding overwrites os-release
BASE_VERSION_ID="44"
if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    BASE_VERSION_ID="$(. /etc/os-release && echo "${VERSION_ID:-44}")"
fi

# Copy the contents of system_files/ of the git repo to /
cp -avf "/ctx/system_files"/. /

if [[ -f /etc/os-release ]]; then
    sed -i "s/^VERSION_ID=.*/VERSION_ID=\"${BASE_VERSION_ID}\"/" /etc/os-release
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
