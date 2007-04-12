#!/usr/local/bin/perl
# Adjust the sort order and field, and return to the index

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
&save_sort_field($folder, $in{'field'}, $in{'dir'});
&redirect("index.cgi?folder=$in{'folder'}&start=$in{'start'}");

