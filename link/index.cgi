#!/usr/local/bin/perl
# index.cgi
# Redirect to another URL

do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
$url = $config{'link'};
$host = $ENV{'HTTP_HOST'};
$host =~ s/:.*$//;
$url =~ s/\$REMOTE_USER/$remote_user/g;
$url =~ s/\$HTTP_HOST/$host/g;
if ($config{'window'}) {
	&ui_print_header(undef, $module_info{'desc'}, "", undef, 0, 1);

	print &text('index_desc', "<tt>$url</tt>"),"<p>\n";
	print "<script>\n";
	print "window.open(\"$url\", \"$module_name\", \"$config{'opts'}\");\n";
	print "</script>\n";

	&ui_print_footer("/", $text{'index'});
	}
else {
	&redirect($url);
	}

