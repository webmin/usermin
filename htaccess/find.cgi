#!/usr/local/bin/perl
# find.cgi
# Find .htaccess files

require './htaccess-lib.pl';
&ReadParse();

# Search for files
open(FIND, "find '$in{'dir'}' -name '$config{'htaccess'}' -print 2>/dev/null |");
while(<FIND>) {
	s/\r|\n//g;
	push(@found, $_);
	}
close(FIND);

# Save and tell the user
@files = &get_htaccess_files();
@files = &unique(@files, @found);
&set_htaccess_files(@files);

&ui_print_header(undef, $text{'find_title'}, "");

if (@found) {
	print "<b>",&text('find_list', "<tt>$in{'dir'}</tt>"),"</b><p>\n";
	foreach $f (@found) {
		print "<tt>$f</tt><br>\n";
		}
	}
else {
	print "<b>",&text('find_none', "<tt>$config{'htaccess'}</tt>",
			     "<tt>$in{'dir'}</tt>"),"</b><p>\n";
	}

&ui_print_footer("", $text{'index_return'});

