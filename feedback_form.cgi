#!/usr/local/bin/perl
# feedback_form.cgi
# Display a form so that the user can send in a webmin bug report

require './web-lib.pl';
&init_config();
require './ui-lib.pl';
&switch_to_remote_user();
&ReadParse();
&error_setup($text{'feedback_err'});
$gconfig{'feedback'} || &error($text{'feedback_ecannot'});
&ui_print_header(undef, $text{'feedback_title'}, "", undef, 0, 1);

#print &text('feedback_desc', "<tt>$gconfig{'feedback'}</tt>"),"<p>\n";

print "<form action=feedback.cgi method=post enctype=multipart/form-data>\n";
print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'feedback_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table width=100%>\n";

$remote_user_info[6] =~ s/,.*$//;
print "<tr> <td><b>$text{'feedback_name'}</b></td>\n";
print "<td><input name=name size=25 value='$remote_user_info[6]'></td>\n";

$host = $gconfig{'feedbackhost'} || &get_system_hostname();
$email = "$remote_user\@$host";
if (&foreign_installed("mailbox")) {
	&foreign_require("mailbox", "mailbox-lib.pl");
	($froms, $doms) = &mailbox::list_from_addresses();
	if (@$froms) { $email = $froms->[0]; }
	}
print "<td><b>$text{'feedback_email'}</b></td>\n";
print "<td><input name=email size=25 value='$email'></td> </tr>\n";

print "<tr> <td><b>$text{'feedback_module'}</b></td>\n";
print "<td><select name=module>\n";
printf "<option value='' %s>%s\n",
	$in{'module'} ? "" : "selected", $text{'feedback_all'};
foreach $minfo (&get_available_module_infos(1)) {
	if (&check_os_support($minfo)) {
		push(@modules, $minfo);
		}
	}
foreach $m (sort { $a->{'desc'} cmp $b->{'desc'} } @modules) {
	printf "<option %s value=%s>%s\n",
		$in{'module'} eq $m->{'dir'} ? "selected" : "",
		$m->{'dir'}, $m->{'desc'};
	}
print "</select></td> </tr>\n";

print "<tr> <td valign=top><b>$text{'feedback_text'}</b></td>\n";
print "<td colspan=3><textarea name=text rows=6 cols=70 wrap=on>",
      "</textarea></td> </tr>\n";

print "<tr> <td colspan=2 nowrap><b>$text{'feedback_config'}</b>&nbsp;&nbsp;\n";
printf "<input type=radio name=config value=1> $text{'yes'}\n";
printf "<input type=radio name=config value=0 checked> $text{'no'}</td>\n";
print "<td colspan=2>($text{'feedback_configdesc'})</td> </tr>\n";

print "<tr> <td><b>$text{'feedback_attach'}</b></td>\n";
print "<td><input type=file name=attach0></td>",
      "<td colspan=2><input type=file name=attach1></td> </tr>\n";

print "</table></td></tr></table>\n";
print "<input type=submit value='$text{'feedback_send'}'></form>\n";

&ui_print_footer("/", $text{'index'});

