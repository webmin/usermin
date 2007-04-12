#!/usr/local/bin/perl
# htaccess_index.cgi
# Display a menu of icons for a per-directory options file

require './htaccess-lib.pl';
&ReadParse();
$conf = &get_htaccess_config($in{'file'});
$desc = "<tt>".&html_escape($in{'file'})."</tt>";
&ui_print_header($desc, $text{'htindex_title'}, "",
	undef, undef, undef, undef, "<a href=\"delete_htaccess.cgi?file=".
	&urlize($in{'file'})."\">$text{'htindex_delete'}</a>");

print &ui_subheading($text{'htindex_opts'});
$sw_icon = { "icon" => "images/show.gif",
	     "name" => $text{'htindex_show'},
	     "link" => "show.cgi?file=".&urlize($in{'file'}) };
$ed_icon = { "icon" => "images/edit.gif",
	     "name" => $text{'htindex_edit'},
	     "link" => "manual_form.cgi?file=".&urlize($in{'file'}) };
&config_icons("htaccess", "edit_htaccess.cgi?file=".&urlize($in{'file'})."&",
	      $sw_icon, $ed_icon ? ( $ed_icon ) : ( ));

@file = ( &find_directive_struct("Files", $conf),
          &find_directive_struct("FilesMatch", $conf) );
if (@file && $httpd_modules{'core'} >= 1.2) {
	# Files sub-directives
	print "<hr>\n";
	print &ui_subheading($text{'htindex_file'});
	print "<table width=100% cellpadding=5>\n";
	foreach $f (@file) {
		if ($i%3 == 0) { print "<tr>\n"; }
		$what = &dir_name($f);
		substr($what, 0, 1) = uc(substr($what, 0, 1));
		print "<td valign=top align=center width=33%>\n";
		&generate_icon("images/dir.gif", $what,
		       	"files_index.cgi?idx=".&indexof($f, @$conf).
			"&file=".&urlize($in{'file'}));
		print "</td>\n";
		if ($i++%3 == 2) { print "</tr>\n"; }
		}
	while($i++%3) { print "<td width=33%><br></td>\n"; }
	print "</table><p>\n";
	}

if ($httpd_modules{'core'} >= 1.2) {
	print "<form action=create_files.cgi>\n";
	print "<input type=hidden name=file value=$in{'file'}>\n";
	print "<table border>\n";
	print "<tr $tb> <td><b>$text{'htindex_create'}</b></td> </tr>\n";
	print "<tr $cb> <td><table>\n";
	print "<tr> <td><b>$text{'htindex_regexp'}</b></td>\n";
	$regex = $d->{'words'}->[0] eq "~" || $d->{'name'} =~ /Match/;
	printf "<td colspan=3><input type=radio name=regexp value=0 %s> %s\n",
		$regex ? "" : "checked", $text{'htindex_exact'};
	printf "<input type=radio name=regexp value=1 %s> %s</td> </tr>\n",
		$regex ? "checked" : "", $text{'htindex_re'};
	print "<tr> <td><b>$text{'htindex_path'}</b></td>\n";
	printf "<td><input name=path size=40 value=\"%s\"></td>\n",
		$d->{'words'}->[0] eq "~" ? $d->{'words'}->[1]
					  : $d->{'words'}->[0];
	print "<td colspan=2 align=right>",
	      "<input type=submit value=\"$text{'create'}\"></td> </tr>\n";
	print "</table></td></tr></table></form>\n";
	}

&ui_print_footer("", $text{'index_return'});


