#!/usr/local/bin/perl
# index.cgi
# Display all themes for the user to choose

require './theme-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

@themes = sort { $a->{'desc'} cmp $b->{'desc'} } &list_visible_themes($current_theme);
$uth = $gconfig{'theme_'.$remote_user};

print "$text{'index_desc'}<br>\n";
print "<form action=change_theme.cgi>\n";
print "<b>$text{'index_sel'}</b> <select name=theme>\n";
printf "<option value=none %s> %s\n",
	defined($uth) ? "" : "checked", $text{'index_global'};
foreach $t ( { 'desc' => $text{'index_default'} }, @themes) {
	printf "<option value='%s' %s>%s\n",
		$t->{'dir'},
		defined($uth) && $uth eq $t->{'dir'} ? 'selected' : '',
		$t->{'desc'};
	}
print "</select>\n";
print "<input type=submit value='$text{'index_change'}'></form>\n";

&ui_print_footer("/", $text{'index'});

