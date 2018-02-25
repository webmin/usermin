#!/bin/sh
# support translators to check their module.info.lang files
# and decide if they can linked to existing webadmin version
[ "$EDITOR" == "" ] && EDITOR=vi
WEBMIN="../webadmin"

if [ ! -d $WEBMIN ]
then
	echo "$WEBMIN not found!"
	exit 1
fi

# $1 is LAMNG to check
if [ "$1" == "" ]
then
	echo "error: missing parameter!"
	echo "usage: $0 LANG"
	echo "    where LANG is the langcode to check, e.g. de de no fr"
	exit 1
fi

#get lang files
for file in `ls */module.info.$1 2>/dev/null`
do
	# skip if wbebmin/file not exsit ort already symlinked 
	[ ! -f "$WEBMIN/$file" -o -h "$file" ] && continue

	echo -e "\nprocessing file -> $file\n--------------------"
	cat $file
	echo -e "\nwebmin file -> $WEBMIN/$file \n--------------------"
	cat ../webadmin/$file

	echo -n -e "\nselect action: [e]dit webmin file, [l]ink, [S]kip ?\b"
	read ans
	if [ "$ans" = "l" ]
	then
		echo "linking $file -> $WEBMIN/$file"
		mv $file $file.sav
		ln -s ../$WEBMIN/$file $file
		if [ $? -ne 0 ]; then
			mv $file.sav $file
			echo "linking failed!"
		else
			echo -e "done!\n"
			rm -f $file.sav
		fi
	fi
	if [ "$ans" = "e" ]
	then
		echo "editing $WEBMIN/$file"
		${EDITOR} $WEBMIN/$file
	fi
done
