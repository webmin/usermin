#!/usr/local/bin/perl
# list_authusers.cgi
# Displays a list of users from a text file

require './htaccess-lib.pl';
require './auth-lib.pl';

&ReadParse();
$desc = &text('authu_header', "<tt>$in{'file'}</tt>");
&ui_print_header($desc, $text{'authu_title'}, "");
$f = $in{'file'};

@users = sort { $a cmp $b } &list_authusers($f);
if (@users) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>",&text('authu_header2', "<tt>$f</tt>"),
	      "</b></td> </tr>\n";
	print "<tr $cb> <td><table width=100%>\n";
	for($i=0; $i<@users; $i++) {
		$u = $users[$i];
		if ($i%4 == 0) { print "<tr>\n"; }
		printf "<td width=25%><a href=\"edit_authuser.cgi?user=$u&".
		  "file=%s&url=%s\">$u</a></td>\n",
		  &urlize($f), &urlize(&this_url());
		if ($i%4 == 3) { print "</tr>\n"; }
		}
	while($i++%4) { print "<td width=25%></td>\n"; }
	print "</table></td></tr></table>\n";
	}
else {
	print "<b>",&text('authu_none', "<tt>$f</tt>"),"</b><p>\n";
	}
printf "<a href=\"edit_authuser.cgi?file=%s&url=%s\">%s</a><p>\n",
        &urlize($f), &urlize(&this_url()), $text{'authu_add'};

&ui_print_footer($in{'url'}, $text{'auth_return'});

