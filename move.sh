#!/bin/sh

# get desc lines
for file in `ls */module.info`
do
for lang in `grep -E -o --binary-files=text '^desc_.+=' $file | sed 's/desc_\(.*\)=/\1/'`
do
	echo remove  desc_$lang from $file
	sed -i "/desc_$lang=/d" $file
done
done
