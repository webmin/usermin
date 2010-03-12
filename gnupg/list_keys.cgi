#!/usr/local/bin/perl
# list_keys.cgi
# Display all keys in your keyring

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'keys_title'}, "");
&ReadParse();

print &ui_tabs_start([ [ "list", $text{'keys_tablist'} ],
		       [ "import", $text{'keys_tabimport'} ],
		       [ "recv", $text{'keys_tabrecv'} ],
		       [ "search", $text{'keys_tabsearch'} ] ],
		     'mode', $in{'mode'} || 'list', 1);

# List of existing keys
print &ui_tabs_start_tab('mode', 'list');
@keys = &list_keys_sorted();
print "$text{'keys_desc'}<p>\n";
print &ui_form_start("delete_keys.cgi", "post");
@links = ( &select_all_link("d"),
	   &select_invert_link("d") );
print &ui_links_row(\@links);
@tds = ( "width=5" );
print &ui_columns_start([ "",
			  $text{'keys_id'},
			  $text{'keys_secret'},
			  $text{'keys_date'},
			  $text{'keys_name'},
			  $text{'keys_email'} ], 100);
foreach $k (@keys) {
	local @cols;
	push(@cols, "<a href='edit_key.cgi?idx=$k->{'index'}'>$k->{'key'}</a>");
	push(@cols, $k->{'secret'} ? "<b>$text{'yes'}</b>"
				   : $text{'no'});
	push(@cols, $k->{'date'});
	push(@cols, join("<br>", map { &html_escape($_) } @{$k->{'name'}}));
	push(@cols, join("<br>", map { &html_escape($_) } @{$k->{'email'}}));
	if ($k->{'secret'}) {
		# Cannot delete secret keys this way
		print &ui_columns_row([ "", @cols ], \@tds);
		}
	else {
		print &ui_checked_columns_row(\@cols, \@tds, "d",$k->{'index'});
		}
	}
print &ui_columns_end();
print &ui_links_row(\@links);
print &ui_form_end([ [ "delete", $text{'keys_delete'} ] ]);
print &ui_tabs_end_tab('mode', 'list');

# Form for adding a key
print &ui_tabs_start_tab('mode', 'import');
print "$text{'keys_importdesc'}<p>\n";
print &ui_form_start("import.cgi", "form-data");
print &ui_table_start(undef, undef, 2);

# Source of key
print &ui_table_row($text{'keys_from'},
	&ui_radio_table("mode", 0,
		[ [ 0, $text{'encrypt_mode0'},
		       &ui_upload("upload", 40) ],
		  [ 1, $text{'encrypt_mode1'},
		       &ui_filebox("local", undef, 40) ],
		  [ 2, $text{'encrypt_mode2'},
		       &ui_textarea("text", undef, 5, 40) ] ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'keys_import'} ] ]);
print &ui_tabs_end_tab('mode', 'import');

# Form for fetching a key from a keyserver
print &ui_tabs_start_tab('mode', 'recv');
print &text('keys_recvdesc', "<tt>$config{'keyserver'}</tt>"),"<p>\n";
print &ui_form_start("recv.cgi");
print &ui_submit($text{'keys_recv'});
print &ui_textbox("id", undef, 20);
print &ui_form_end();
print &ui_tabs_end_tab('mode', 'recv');

# Key search and import page
print &ui_tabs_start_tab('mode', 'search');
print &text('keys_searchdesc', "<tt>$config{'keyserver'}</tt>"),"<p>\n";

print &ui_form_start('list_keys.cgi');
print &ui_hidden('mode', 'search');
print "<b>$text{'keys_search'}</b>\n",
      &ui_textbox("search", $in{'search'}, 30)," ",
      &ui_submit($text{'keys_searchok'}),"<p>\n";
print &ui_form_end();

if ($in{'search'}) {
	# See what matches
	@rv = &search_gpg_keys($in{'search'});
	if (@rv) {
		print $text{'keys_searchclick'},"<p>\n";
		}
	@data = ( );
	foreach $k (@rv) {
		push(@data, [
			"<a href='recv.cgi?id=$k->{'key'}'>$k->{'key'}</a>",
			$k->{'date'},
			join("<br>", map { &html_escape($_) } @{$k->{'name'}}),
			join("<br>", map { &html_escape($_) } @{$k->{'email'}}),
			]);
		}
	print &ui_columns_table(
		[ $text{'keys_id'}, $text{'keys_date'},
		  $text{'keys_name'}, $text{'keys_email'} ],
		"100%", \@data, undef, 0, undef,
		$text{'keys_searchnone'}
		);
	}

print &ui_tabs_end_tab('mode', 'search');

print &ui_tabs_end(1);

&ui_print_footer("", $text{'index_return'});

