#!/usr/local/bin/perl
# Output a key for download

require './ssh-lib.pl';
&ReadParse();
@keys = &list_ssh_keys();
($key) = grep { $_->{'private_file'} eq $in{'file'} } @keys;
$key || &error($text{'ekey_egone'});

print "Content-type: application/octet-stream\n\n";
print &read_file_contents($key->{'private_file'});

