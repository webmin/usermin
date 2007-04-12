#!/usr/local/bin/perl
# index.cgi
# Just redirects to link.cgi, if a URL has been set

require './tunnel-lib.pl';
if ($config{'url'}) {
	&redirect("link.cgi/");
	}
else {
	&error($text{'index_elink'});
	}

