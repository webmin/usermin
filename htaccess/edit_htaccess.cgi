#!/usr/local/bin/perl
# edit_htaccess.cgi
# Display a form for editing some kind of per-directory options file

require './htaccess-lib.pl';
&ReadParse();
$conf = &get_htaccess_config($in{'file'});
@dirs = &editable_directives($in{'type'}, 'htaccess');
$desc = &text('htindex_header', "<tt>$in{'file'}</tt>");
&ui_print_header($desc, $text{"type_$in{'type'}"}, "");

print "<form method=post action=save_htaccess.cgi>\n";
print "<input type=hidden name=type value=$in{'type'}>\n";
print "<input type=hidden name=file value=$in{'file'}>\n";
print "<table border width=100%>\n";
print "<tr $tb> <td><b>",&text('htindex_header2', $text{"type_$in{'type'}"},
			       "<tt>$in{'file'}</tt>"),"</td> </tr>\n";
print "<tr $cb> <td><table>\n";
&generate_inputs(\@dirs, $conf);
print "</table></td> </tr></table><br>\n";
print "<input type=submit value=\"$text{'save'}\"></form>\n";

&ui_print_footer("htaccess_index.cgi?file=$in{'file'}", "options file index");


