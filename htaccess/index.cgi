#!/usr/local/bin/perl
# index.cgi
# Display a list of all .htaccess files

require './htaccess-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

# Check if version info can be gotten from webmin
if (!$httpd_modules{'core'}) {
	print "<b>",&text('index_apache', "<tt>$config{'webmin_apache'}</tt>"),
	      "</b><p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}

# Show known config files
print &text('index_desc', "<tt>$config{'htaccess'}</tt>"),"<p>\n";
@files = &get_htaccess_files();
if (@files) {
	print &ui_subheading($text{'index_header'});
	@icons = map { "images/dir.gif" } @files;
	@links = map { "htaccess_index.cgi?file=".&urlize($_) } @files;
	@titles = map { /^(.*)\//; $1 } @files;
	&icons_table(\@links, \@titles, \@icons);
	}
else {
	print "<b>$text{'index_none'}</b><p>\n";
	}
print "<form action=create.cgi>\n";
print "<input type=submit value='$text{'index_create'}'>\n";
print "<input name=dir size=50> ",&file_chooser_button("dir", 1),"<br>\n";
print "</form>\n";

print "<hr>\n";
print &text('index_finddesc', "<tt>$config{'htaccess'}</tt>"),"<br>\n";
print "<form action=find.cgi>\n";
print "<input type=submit value='$text{'index_find'}'>\n";
print "<input name=dir size=50 value='$www_root'> ",
	&file_chooser_button("dir", 1),"<br>\n";
print "</form>\n";

&ui_print_footer("/", $text{'index'});

