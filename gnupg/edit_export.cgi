#!/usr/local/bin/perl
# export_form.cgi
# Show a form for exporting a key

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
$key = $keys[$in{'idx'}];

&ui_print_header(undef, $text{'export_title'}, "");

print &text('export_desc', "<tt>$key->{'name'}->[0]</tt>",
	    $key->{'email'}->[0] ? "&lt;<tt>$key->{'email'}->[0]</tt>&gt;" : "",
	    ),"<p>\n";
print "<form action=export.cgi>\n";
print "<input type=hidden name=idx value='$key->{'index'}'>\n";
print "<table>\n";

print "<tr> <td valign=top><b>$text{'export_to'}</b></td>\n";
print "<td><input type=radio name=mode value=0 checked> $text{'export_mode0'}<br>\n";
print "<input type=radio name=mode value=1> $text{'export_mode1'}\n";
print "<input name=to size=35> ",&file_chooser_button("to"),"</td> </tr>\n";

print "<tr> <td><b>$text{'export_format'}</b></td>\n";
print "<td><input type=radio name=format value=0 checked> ",
      "$text{'export_ascii'}\n";
print "<input type=radio name=format value=1> ",
      "$text{'export_binary'}</td> </tr>\n";

if ($key->{'secret'}) {
	print "<tr> <td><b>$text{'export_smode'}</b></td>\n";
	print "<td><input type=radio name=smode value=1> ",
	      "$text{'export_secret'}\n";
	print "<input type=radio name=smode value=0 checked> ",
	      "$text{'export_public'}</td> </tr>\n";
	}

print "</table>\n";
print "<input type=submit value='$text{'export_ok'}'></form>\n";

&ui_print_footer("list_keys.cgi", $text{'keys_return'});

