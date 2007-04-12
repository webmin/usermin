#!/bin/sh
classes=`cd /usr/local/webadmin/file ; ls *.class`
for c in $classes; do
	ln -s ../../webadmin/file/$c /usr/local/useradmin/file/$c
done
