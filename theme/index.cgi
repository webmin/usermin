#!/usr/local/bin/perl
# index.cgi
# Display all themes for the user to choose

require './theme-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

@themes = sort { $a->{'desc'} cmp $b->{'desc'} } &list_visible_themes($current_theme);
$uth = $gconfig{'theme_'.$remote_user};

print "$text{'index_desc'}<p>\n";
print &ui_form_start("change_theme.cgi");
print &ui_table_start(undef, "width=100%", 2);
print &ui_table_row($text{'index_sel'},
	&ui_select("theme", $uth,
	[ [ "", $text{'index_global'} ],
	  map { [ $_->{'dir'}, $_->{'desc'}."" ] }
	      @themes ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'index_change'} ] ]);

&ui_print_footer("/", $text{'index'});

