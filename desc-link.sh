#!/bin/sh
# support translators to check their module.info.lang files
# and decide if they can linked to existing webadmin version
[ "$EDITOR" == "" ] && EDITOR=vi
FORCE=""
WEBMIN="../webmin"
[ -d "../webadmin" ] && WEBMIN="../webadmin"

if [ ! -d $WEBMIN ]
then
	echo "webmin not found! please check out webmin from github."
	exit 1
fi

# help
if [ "$1" == "-h" ]
then
	cat <<EOF

usage: $0 [-force] LANG

	this script helps translators to find out if descriptions
	for a given language already exsits in webmin and offers to:

	link	same description is used for webmin and usermin
	edit	edit description in webmin to fit both

parameters:
	force
		link all found possibilities
	LANG
		language code to process, e.g. $LANG 

how to:
	- checkout usermin and webmin from github:
	  # git clone https://github.com/<YOURNAME>/webmin.git
	  # git clone https://github.com/<YOURNAME>/usermin.git
	- cd to usermin and run script
	  # cd usermin; $0 de
	- push changes to repository
	  # git add; git commit -m "LANG xx"
	  # git push
	
EOF
	echo "availible languages:"
	( cd $WEBMIN/lang; ls )
	exit
fi


# check for force
if [ "$1" == "-force" ]
then
	FORCE="yes"
	shift
fi


# $1 is LAMNG to check
if [ "$1" == "" ]
then
	echo "error: missing parameter!"
	echo "usage: $0 LANG"
	echo "    where LANG is the langcode to check, e.g. de de no fr"
	exit 1
fi

LANG=$1

#get lang files
for module in `ls */module.info 2>/dev/null`
do
	file="$module.$LANG"
	# skip if wbebmin/file not exsit ort already symlinked 
	[ ! -f "$WEBMIN/$file" -o -h "$file" ] && continue

	echo -e "\nprocessing file -> $file\n--------------------"
	if [ ! -f "$file" ]
	then
		echo " -> missing translation for \"$LANG\" found!"
	else
		cat $file
	fi
	echo -e "\nwebmin file -> $WEBMIN/$file \n--------------------"
	cat ../webadmin/$file

	echo -n -e "\nselect action: [e]dit webmin file, [l]ink, [S]kip ?\b"
	if [ "$FORCE" == "" ]
	then
		read ans
	fi
	if [ "$ans" == "l" -o "$FORCE" != "" ]
	then
		echo "linking $file -> $WEBMIN/$file"
		[ -f "$file" ] && mv $file $file.sav 
		ln -s ../$WEBMIN/$file $file
		if [ $? -ne 0 ]; then
			[ -f "$file.sav" ] && mv $file.sav $file
			echo "linking failed!"
		else
			echo -e "done!\n"
			rm -f $file.sav
		fi
	fi
	if [ "$ans" == "e" ]
	then
		echo "editing $WEBMIN/$file"
		${EDITOR} $WEBMIN/$file
	fi
done
