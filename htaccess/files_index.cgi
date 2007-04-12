#!/usr/local/bin/perl
# files_index.cgi
# Display a menu of icons for per-files options

require './htaccess-lib.pl';
&ReadParse();
$conf = &get_htaccess_config($in{'file'});
$d = $conf->[$in{'idx'}];
$desc = &text('htfile_header', &dir_name($d), "<tt>$in{'file'}</tt>");
&ui_print_header($desc, $text{'htfile_title'}, "");

print &ui_subheading($text{'htfile_title'});
$sw_icon = { "icon" => "images/show.gif",
	     "name" => $text{'htfile_show'},
	     "link" => "show.cgi?file=".&urlize($in{'file'})."&idx=$in{'idx'}" };
$ed_icon = { "icon" => "images/edit.gif",
	     "name" => $text{'htfile_edit'},
	     "link" =>
		"manual_form.cgi?file=".&urlize($in{'file'})."&idx=$in{'idx'}" };
&config_icons("directory", "edit_files.cgi?file=".&urlize($in{'file'})."&idx=$in{'idx'}&",
	      $sw_icon, $ed_icon ? ( $ed_icon ) : ( ));

print "<hr>\n";
print "<form action=change_files.cgi>\n";
print "<input type=hidden name=file value=$in{'file'}>\n";
print "<input type=hidden name=idx value=$in{'idx'}>\n";
print "<table border>\n";
print "<tr $tb> <td><b>$text{'htfile_apply'}</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";
print "<tr> <td><b>$text{'htindex_regexp'}</b></td>\n";
$regex = $d->{'words'}->[0] eq "~" || $d->{'name'} =~ /Match/i;
printf "<td colspan=3><input type=radio name=regexp value=0 %s> %s\n",
	$regex ? "" : "checked", $text{'htindex_exact'};
printf "<input type=radio name=regexp value=1 %s> %s</td> </tr>\n",
	$regex ? "checked" : "", $text{'htindex_re'};
print "<tr> <td><b>$text{'htindex_path'}</b></td>\n";
printf "<td><input name=path size=40 value=\"%s\"></td>\n",
	$d->{'words'}->[0] eq "~" ? $d->{'words'}->[1] : $d->{'words'}->[0];
print "<td colspan=2 align=right>",
      "<input type=submit value=\"$text{'save'}\">&nbsp;",
      "<input type=submit value=\"$text{'delete'}\" name=delete></td> </tr>\n";
print "</table></td></tr></table></form>\n";

&ui_print_footer("htaccess_index.cgi?file=".&urlize($in{'file'}), $text{'htindex_return'});


