#!/usr/local/bin/perl
# Show all scheduled messages

require './schedule-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

@scheds = &list_schedules();

# Apply selected sort mode
if ($userconfig{'sort_mode'} == 0) {
	@scheds = sort { $a->{'id'} <=> $b->{'id'} } @scheds;
	}
elsif ($userconfig{'sort_mode'} == 1) {
	@scheds = sort { &next_run($a) <=> &next_run($b) } @scheds;
	}
else {
	@scheds = sort { $a->{'to'} cmp $b->{'to'} } @scheds;
	}

@links = ( &select_all_link("d"),
	   &select_invert_link("d"),
	   "<a href='edit.cgi?new=1'>$text{'index_add'}</a>" );

if (@scheds) {
	print &ui_form_start("delete.cgi", "post");
	@tds = ( "width=5" );
	print &ui_links_row(\@links);
	print &ui_columns_start([ "",
				  $text{'index_subject'},
				  $text{'index_when'},
				  $text{'index_to'},
				  $text{'index_enabled'} ], 100, 0, \@tds);
	foreach $s (@scheds) {
		if ($s->{'at'}) {
			$when = localtime($s->{'at'});
			}
		else {
			$when = &cron::when_text($s, 1);
			}
		@to = ( );
		if ($s->{'to'}) {
			push(@to, map { $_->[0] }
				      &mailbox::split_addresses($s->{'to'}));
			}
		else {
			push(@to, $text{'index_self'});
			}
		push(@to, map { $_->[0] }
			      &mailbox::split_addresses($s->{'cc'}),
			      &mailbox::split_addresses($s->{'bcc'}));
		print &ui_checked_columns_row([
			"<a href='edit.cgi?id=$s->{'id'}'>".
		        $s->{'subject'}."</a>",
			$when,
			&html_escape(join(", ", @to)),
			$s->{'at'} &&
			 $s->{'ran'} >= $s->{'at'} ? $text{'index_ran'} :
			$s->{'enabled'} ? $text{'yes'}
					: $text{'no'} ], \@tds,
			"d", $s->{'id'});
		$sent++ if ($s->{'at'} && $s->{'ran'} >= $s->{'at'});
		}
	print &ui_columns_end();
	print &ui_links_row(\@links);
	print &ui_form_end([ [ "delete", $text{'index_delete'} ],
			     [ "disable", $text{'index_disable'} ],
			     [ "enable", $text{'index_enable'} ] ]);
	}
else {
	print "<b>$text{'index_none'}</b><p>\n";
	print &ui_links_row([ $links[2] ]);
	}

if ($sent) {
	print "<hr>\n";
	print &ui_buttons_start();
	print &ui_buttons_row("clear.cgi", $text{'index_clear'},
					   $text{'index_cleardesc'});
	print &ui_buttons_end();
	}

&ui_print_footer("/", $text{'index'});

