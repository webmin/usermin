#!/usr/local/bin/perl
# edit_virt.cgi
# Display a form for editing some kind of per-directory options file

require './htaccess-lib.pl';
&ReadParse();
$hconf = &get_htaccess_config($in{'file'});
$d = $hconf->[$in{'idx'}];
$conf = $d->{'members'};
@dirs = &editable_directives($in{'type'}, 'directory');
$desc = &text('htfile_header', &dir_name($d), "<tt>$in{'file'}</tt>");
&ui_print_header($desc, $text{"type_$in{'type'}"}, "");

print "<form method=post action=save_files.cgi>\n";
print "<input type=hidden name=type value=$in{'type'}>\n";
print "<input type=hidden name=file value=$in{'file'}>\n";
print "<input type=hidden name=idx value=$in{'idx'}>\n";
print "<table border width=100%>\n";
print "<tr $tb> <td><b>",&text('htfile_header2', $text{"type_$in{'type'}"},
	&dir_name($d)),"</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";
&generate_inputs(\@dirs, $conf);
print "</table></td> </tr></table><br>\n";
print "<input type=submit value=\"$text{'save'}\"></form>\n";

&ui_print_footer("htaccess_index.cgi?file=$in{'file'}", $text{'htindex_return'});


