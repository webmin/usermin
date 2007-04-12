#!/usr/local/bin/perl
# Offer to setup razor, if the user hasn't already

require './spam-lib.pl';
&ui_print_header(undef, $text{'razor_title'}, "");

if (!&has_command($config{'razor_admin'})) {
	# Not installed
	print "<p>",&text('razor_ecmd', "<tt>$config{'razor_admin'}</tt>"),"<p>\n";
	}
else {
	# Show form
	print "<form action=setup_razor.cgi>\n";
	print "$text{'razor_desc'}<p>\n";
	print "<table>\n";

	foreach $w ("user", "pass") {
		print "<tr> <td><b>",$text{'razor_'.$w},"</b></td> <td>\n";
		print "<input type=radio name=${w}_def value=1 checked> ",
		      "$text{'razor_auto'}\n";
		print "<input type=radio name=${w}_def value=0> ",
		      "$text{'razor_enter'}\n";
		$t = $w eq "user" ? "text" : "password";
		print "<input name=$w type=$t size=25></td> </tr>\n";
		}

	print "</table>\n";
	print "<input type=submit value='$text{'razor_ok'}'></form>\n";
	}

&ui_print_footer("", $text{'index_return'});

