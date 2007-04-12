#!/usr/local/bin/perl
# mail_search.cgi
# Find mail messages matching some pattern

require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
&ReadParse();
if ($in{'simple'}) {
	# Make sure a search was entered
	$in{'search'} ne "" || &error($mailbox::text{'search_ematch'});
	}
elsif (defined($in{'score'})) {
	# Make sure a score was entered
	$in{'score'} =~ /^\d+$/ || &error($text{'search_escore'});
	}
else {
	# Validate search fields
	for($i=0; defined($in{"field_$i"}); $i++) {
		if ($in{"field_$i"}) {
			$in{"what_$i"} || &error(&mailbox::text('search_ewhat', $i+1));
			$neg = $in{"neg_$i"} ? "!" : "";
			push(@fields, [ $neg.$in{"field_$i"}, $in{"what_$i"} ]);
			}
		}
	@fields || &error($mailbox::text{'search_enone'});
	}

&ui_print_header(undef, $mailbox::text{'search_title'}, "");
$folder = &spam_file_folder();

if ($in{'simple'}) {
	# Just search by Subject and From in one folder, or body, depending
	# on preferences
	($mode, $words) = &mailbox::parse_boolean($in{'search'});
	if ($userconfig{'search_body'} && $mode != 2) {
		# Do an 'and' or 'or' search of body
		@searchlist = map { [ 'body', $_ ] } @$words;
		@rv = &mailbox::mailbox_search_mail(\@searchlist, $mode,
						    $folder);
		}
	elsif ($mode == 0) {
		# Can just do a single 'or' search
		@searchlist = map { ( [ 'subject', $_ ],
				      [ 'from', $_ ] ) } @$words;
		@rv = &mailbox::mailbox_search_mail(\@searchlist, 0, $folder);
		}
	elsif ($mode == 1) {
		# Need to do two 'and' searches and combine
		@searchlist1 = map { ( [ 'subject', $_ ] ) } @$words;
		@rv1 = &mailbox::mailbox_search_mail(\@searchlist1, 1, $folder);
		@searchlist2 = map { ( [ 'from', $_ ] ) } @$words;
		@rv2 = &mailbox::mailbox_search_mail(\@searchlist2, 1, $folder);
		@rv = @rv1;
		%gotidx = map { $_->{'idx'}, 1 } @rv;
		foreach $mail (@rv2) {
			push(@rv, $mail) if (!$gotidx{$mail->{'idx'}});
			}
		}
	else {
		&error($mailbox::text{'search_eboolean'});
		}
	print "<p><b>",&mailbox::text('search_results2', scalar(@rv),
			     "<tt>$in{'search'}</tt>"),"</b><p>\n";
	}
elsif (defined($in{'score'})) {
	# Search by score
	@rv = &mailbox::mailbox_search_mail(
		[ [ 'x-spam-level', '*' x $in{'score'} ] ], 0, $folder);
	print "<p><b>",&text('search_results5', scalar(@rv), $in{'score'}),"</b><p>\n";
	}
else {
	# Complex search
	@rv = &mailbox::mailbox_search_mail(\@fields, $in{'and'}, $folder);
	print "<p><b>",&mailbox::text('search_results4', scalar(@rv)),"</b><p>\n";
	}
@rv = reverse(@rv);
&mailbox::set_sort_indexes($folder, \@rv);

print "<form action=process.cgi method=post>\n";
if ($mailbox::userconfig{'top_buttons'} && @rv) {
	&show_buttons(1);
	print "<a href='' onClick='document.forms[0].d.checked = true; for(i=0; i<document.forms[0].d.length; i++) { document.forms[0].d[i].checked = true; } return false'>$mailbox::text{'mail_all'}</a>&nbsp;\n";
	print "<a href='' onClick='document.forms[0].d.checked = !document.forms[0].d.checked; for(i=0; i<document.forms[0].d.length; i++) { document.forms[0].d[i].checked = !document.forms[0].d[i].checked; } return false'>$mailbox::text{'mail_invert'}</a>&nbsp;\n";
	}
if (@rv) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td>&nbsp;</td> ",
	      "<td><b>$mailbox::text{'mail_from'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_date'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_size'}</b></td> ",
	      "<td><b>$text{'mail_level'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_subject'}</b></td> </tr>\n";
	}
foreach $m (@rv) {
	local $idx = $m->{'sortidx'};
	print "<tr $cb>\n";
	print "<td><input type=checkbox name=d value=$idx></td>\n";
	print "<td nowrap><a href='view_mail.cgi?idx=$idx'>",
	      &mailbox::simplify_from($m->{'header'}->{$showto?'to':'from'}),"</td>\n";
	print "<td nowrap>",&mailbox::simplify_date($m->{'header'}->{'date'}),"</td>\n";
	print "<td nowrap>",int($m->{'size'}/1000)+1," kB","</td>\n";
	print "<td nowrap>",length($m->{'header'}->{'x-spam-level'}),"</td>\n";
	print "<td><table border=0 cellpadding=0 cellspacing=0 width=100%>",
	      "<tr><td>",&mailbox::simplify_subject($m->{'header'}->{'subject'}),
	      "</td> <td align=right>";
	if ($m->{'header'}->{'content-type'} =~ /multipart\/\S+/i) {
		print "<img src=/mailbox/images/attach.gif>";
		}
	local $p = int($m->{'header'}->{'x-priority'});
	if ($p == 1) {
		print "&nbsp;<img src=images/p1.gif>";
		}
	elsif ($p == 2) {
		print "&nbsp;<img src=images/p2.gif>";
		}
	print "</td></tr></table></td> </tr>\n";
	}
if (@rv) {
	print "</table>\n";
	print "<a href='' onClick='document.forms[0].d.checked = true; for(i=0; i<document.forms[0].d.length; i++) { document.forms[0].d[i].checked = true; } return false'>$mailbox::text{'mail_all'}</a>&nbsp;\n";
	print "<a href='' onClick='document.forms[0].d.checked = !document.forms[0].d.checked; for(i=0; i<document.forms[0].d.length; i++) { document.forms[0].d[i].checked = !document.forms[0].d[i].checked; } return false'>$mailbox::text{'mail_invert'}</a>&nbsp;\n";
	&show_buttons(2);
	}
else {
	print "<b>$text{'search_none'}</b> <p>\n";
	}
print "</form><p>\n";

&ui_print_footer("mail.cgi", $text{'mail_return'});

