#!/usr/local/bin/perl
# list_knowns.cgi
# List trusted remote hosts

require './ssh-lib.pl';
&ui_print_header(undef, $text{'knowns_title'}, "");

@links = ( &select_all_link("d"),
	   &select_invert_link("d"),
	   "<a href='edit_known.cgi?new=1'>$text{'knowns_add'}</a>" );

print "$text{'knowns_desc'}<p>\n";

@knowns = &list_knowns();
if (@knowns) {
	print &ui_form_start("delete_knowns.cgi", "post");
	print &ui_links_row(\@links);
	@tds = ( "width=5", undef, "nowrap" );
	print &ui_columns_start([ "",
			 	  $text{'knowns_hosts'},
				  $text{'knowns_type'},
				  $text{'knowns_key'} ], undef, 0, \@tds);
	foreach $k (@knowns) {
		print &ui_checked_columns_row([
			"<a href='edit_known.cgi?idx=$k->{'index'}'>".
		      	  join("&nbsp;|&nbsp;",
			     map { &html_escape($_) } @{$k->{'hosts'}})."</a>",
			&html_escape($k->{'type'}),
			"<tt>".&html_escape(substr($k->{'key'}, 0, 40)).
			" ... ".
			&html_escape(substr($k->{'key'}, -40))."</tt>"
			], \@tds, "d", $k->{'index'});
		}
	print &ui_columns_end();
	print &ui_links_row(\@links);
	print &ui_form_end([ [ "delete", $text{'knowns_delete'} ] ]);
	}
else {
	print "<b>$text{'knowns_none'}</b> <p>\n";
	print &ui_links_row([ $links[2] ]);
	}

&ui_print_footer("", $text{'index_return'});

