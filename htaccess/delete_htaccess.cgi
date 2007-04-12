#!/usr/local/bin/perl
# delete_htaccess.cgi
# Delete some .htaccess or similar file

require './htaccess-lib.pl';
&ReadParse();
unlink($in{'file'});

@files = &get_htaccess_files();
&set_htaccess_files(grep { $_ ne $in{'file'} } @files);
&redirect("");

