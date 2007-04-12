#!/bin/sh
# Copy all modules to download.webmin.com

fromdir=/usr/local/useradmin
todir=joe.webmin.com:htdocs/download
rsync="rsync --rsh=ssh -v"

$rsync $fromdir/umodules/*.wbm.gz $todir/umodules

