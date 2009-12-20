#!/bin/sh
# Copy all modules to download.webmin.com

fromdir=/usr/local/useradmin
todir=webadmin@download.webmin.com:domains/download.webmin.com/public_html/download
rsync="rsync --rsh=ssh -v"

$rsync $fromdir/umodules/*.wbm.gz $todir/umodules

