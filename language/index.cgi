#!/usr/local/bin/perl
# edit_lang.cgi
# Language config form

require './language-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

print $text{'index_intro'},"<p>\n";

print "<form action=change_lang.cgi>\n";

$ulang = $gconfig{'lang_'.$remote_user};
print "<b>$text{'index_lang'}</b>\n";
print "<select name=lang>\n";
printf "<option value='' %s>%s\n",
	$ulang ? '' : 'selected', $text{'index_global'};
foreach $l (&list_languages()) {
	printf "<option value=%s %s>%s (%s)\n",
		$l->{'lang'},
		$ulang eq $l->{'lang'} ? 'selected' : '',
		$l->{'desc'}, uc($l->{'lang'});
	}
print "</select>\n";
print "<input type=submit value=\"$text{'index_ok'}\"></form>\n";

&ui_print_footer("/", $text{'index'});

