#!/bin/sh

# get desc lines
for file in `ls */module.info`
do
for lang in `grep -E -o --binary-files=text '^desc_.+=' $file | sed 's/desc_\(.*\)=/\1/'`
do
	echo $file.$lang
	grep -E --binary-files=text 'desc_'$lang'=' $file >$file.$lang
done
done
