#!/usr/local/bin/perl
# Adjust the sort order and field, and return to the index
use strict;
use warnings;
our %in;

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
&save_sort_field($folder, $in{'field'}, $in{'dir'});
&redirect("index.cgi?folder=$in{'folder'}&start=$in{'start'}");
