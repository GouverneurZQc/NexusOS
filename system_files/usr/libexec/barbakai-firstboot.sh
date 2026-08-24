#!/usr/bin/bash
# Runs once on a writable system (ISO install, qcow2, or bootc switch).
set -euo pipefail

STAMP="/var/lib/barbakai/firstboot-done"
mkdir -p /var/lib/barbakai

if [[ -f "${STAMP}" ]]; then
    exit 0
fi

hostnamectl set-hostname barbakai 2>/dev/null || echo barbakai >/etc/hostname

if ! id barbakai >/dev/null 2>&1; then
    if getent group gamemode >/dev/null 2>&1; then
        useradd -m -G wheel,video,audio,input,render,gamemode barbakai
    else
        useradd -m -G wheel,video,audio,input barbakai
    fi
    echo 'barbakai:Thegamecontrol!' | chpasswd
fi

touch "${STAMP}"
exit 0
