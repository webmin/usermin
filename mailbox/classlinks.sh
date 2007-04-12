#!/bin/sh
classes=`cd /usr/local/webadmin/mailboxes ; ls *.class`
for c in $classes; do
	ln -s ../../webadmin/mailboxes/$c /usr/local/useradmin/mailbox/$c
done
