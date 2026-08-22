#!/bin/bash

WALL="/usr/share/nextos/wallpapers/nextos-wallpaper.jpeg"

if [ -f "$WALL" ]; then
    kwriteconfig6 --file kdeglobals --group General --key Name "NEXUS"
fi