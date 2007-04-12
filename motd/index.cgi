#!/usr/local/bin/perl
# index.cgi
# Just display the message of the day

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

open(FILE, $config{'motd_file'});
while(<FILE>) {
	$motd .= $_;
	}
close(FILE);

if ($motd !~ /\S/) {
	print "<b>",&text('index_none', "<tt>$config{'motd_file'}</tt>"),
	      "</b><p>\n";
	}
elsif ($config{'html'}) {
	$motd =~ s/^[\000-\377]*<BODY.*>//i;
	$motd =~ s/<\/BODY>[\000-\377]*$//i;
	print $motd;
	}
else {
	print "<pre>$motd</pre>\n";
	}

&ui_print_footer("/", $text{'index'});

