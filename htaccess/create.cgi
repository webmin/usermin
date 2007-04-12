#!/usr/local/bin/perl
# create.cgi
# Create a .htaccess file

require './htaccess-lib.pl';
&ReadParse();

if (-d $in{'dir'}) {
	$file = "$in{'dir'}/$config{'htaccess'}";
	}
else {
	$file = $in{'dir'};
	}

if (!-r $file) {
	open(HTACCESS, ">$file") || &error($!);
	close(HTACCESS) || &error($!);
	chmod(0755, $file);
	}

@files = &get_htaccess_files();
@files = &unique(@files, $file);
&set_htaccess_files($file);

&redirect("htaccess_index.cgi?file=".&urlize($file));

