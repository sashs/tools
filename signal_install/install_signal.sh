#!/bin/sh
CWD=$(pwd)
DIR="signal_$(date +'%s')"
TEMP_PATH="/tmp/$DIR"
mkdir -p $TEMP_PATH
cd $TEMP_PATH
MAIN_URL="https://updates.signal.org/desktop/apt/"

# Download Packages
PACKAGES_URL="dists/xenial/main/binary-amd64/Packages.bz2"
wget "$MAIN_URL$PACKAGES_URL"
bzip2 -d Packages.bz2

# Download deb
FILE_URL=$(cat Packages | grep Filename | head -n 1 | awk '{print $2}')
FILE_NAME=$(echo $FILE_URL | awk 'BEGIN { FS = "/" } ; { print $NF }')
wget "$MAIN_URL$FILE_URL"


# Generate PKGBUILD
HASH=$(sha512sum "$TEMP_PATH/$FILE_NAME" | awk '{print $1}')
SED="s/HASH_VALUE/$HASH/"
sed -e "$SED" $CWD/PKGBUILD_TEMPLATE > PKGBUILD
SED="s/URL_VALUE/file:\/\/\/tmp\/$DIR\/$FILE_NAME/"
sed -i -e "$SED" PKGBUILD

cp $CWD/signal-desktop.install $TEMP_PATH
sudo pacman -S gconf libappindicator-gtk2 libnotify libxss libxtst nss
makepkg && sudo pacman -U *.pkg.tar.xz
