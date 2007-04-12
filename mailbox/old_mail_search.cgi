#!/usr/local/bin/perl
# mail_search.cgi
# Find mail messages matching some pattern

require './mailbox-lib.pl';
&ReadParse();
$limit = { };
if (!$in{'status_def'} && defined($in{'status'})) {
	$statusmsg = &text('search_withstatus',
			   $text{'view_mark'.$in{'status'}});
	}
if ($in{'simple'}) {
	# Make sure a search was entered
	$in{'search'} || &error($text{'search_ematch'});
	if ($userconfig{'search_latest'}) {
		$limit->{'latest'} = $userconfig{'search_latest'};
		}
	}
else {
	# Validate search fields
	for($i=0; defined($in{"field_$i"}); $i++) {
		if ($in{"field_$i"}) {
			$in{"what_$i"} || &error(&text('search_ewhat', $i+1));
			$neg = $in{"neg_$i"} ? "!" : "";
			push(@fields, [ $neg.$in{"field_$i"}, $in{"what_$i"} ]);
			}
		}
	@fields || $statusmsg || &error($text{'search_enone'});
	if (!defined($in{'limit'})) {
		if ($userconfig{'search_latest'}) {
			$limit = { 'latest' => $userconfig{'search_latest'} };
			}
		}
	elsif (!$in{'limit_def'}) {
		$in{'limit'} =~ /^\d+$/ || &error($text{'search_elatest'});
		$limit->{'latest'} = $in{'limit'};
		}
	}
if ($limit && $limit->{'latest'}) {
	$limitmsg = &text('search_limit', $limit->{'latest'});
	}

&set_module_index($in{'folder'} < 0 ? 0 : $in{'folder'});
&ui_print_header(undef, $text{'search_title'}, "");
@folders = &list_folders();
if ($in{'folder'} == -2) {
	print "<center><font size=+2>$text{'search_local'}</font></center>\n";
	}
elsif ($in{'folder'} == -1) {
	print "<center><font size=+2>$text{'search_all'}</font></center>\n";
	}
else {
	$folder = $folders[$in{'folder'}];
	print "<center><font size=+2>",
	      &text('mail_for', $folder->{'name'}),"</font></center>\n";
	}

if ($in{'simple'}) {
	# Just search by Subject and From (or To) in one folder
	($mode, $words) = &parse_boolean($in{'search'});
	local $who = $folder->{'sent'} ? 'to' : 'from';
	if ($mode == 0) {
		# Can just do a single 'or' search
		@searchlist = map { ( [ 'subject', $_ ],
				      [ $who, $_ ] ) } @$words;
		@rv = &mailbox_search_mail(\@searchlist, 0, $folder, $limit);
		}
	elsif ($mode == 1) {
		# Need to do two 'and' searches and combine
		@searchlist1 = map { ( [ 'subject', $_ ] ) } @$words;
		@rv1 = &mailbox_search_mail(\@searchlist1, 1, $folder, $limit);
		@searchlist2 = map { ( [ $who, $_ ] ) } @$words;
		@rv2 = &mailbox_search_mail(\@searchlist2, 1, $folder, $limit);
		@rv = @rv1;
		%gotidx = map { $_->{'idx'}, 1 } @rv;
		foreach $mail (@rv2) {
			push(@rv, $mail) if (!$gotidx{$mail->{'idx'}});
			}
		}
	else {
		&error($text{'search_eboolean'});
		}
	foreach $mail (@rv) {
		$mail->{'folder'} = $folder;
		}
	if ($statusmsg) {
		@rv = &filter_by_status(\@rv, $in{'status'});
		}
	print "<p><b>",&text('search_results2', scalar(@rv),
		     "<tt>$in{'search'}</tt>")," ",$limitmsg," ",$statusmsg,
		     " ..</b><p>\n";
	}
else {
	# Complex search, perhaps over multiple folders!
	if ($in{'folder'} == -2) {
		@sfolders = grep { !$_->{'remote'} } @folders;
		$multi_folder = 1;
		}
	elsif ($in{'folder'} == -1) {
		@sfolders = @folders;
		$multi_folder = 1;
		}
	else {
		@sfolders = ( $folder );
		}
	foreach $sf (@sfolders) {
		local @frv = &mailbox_search_mail(\@fields, $in{'and'}, $sf, $limit);
		foreach $mail (@frv) {
			$mail->{'folder'} = $sf;
			}
		push(@rv, @frv);
		}
	if ($statusmsg) {
		@rv = &filter_by_status(\@rv, $in{'status'});
		}
	print "<p><b>",&text('search_results4', scalar(@rv)),
	      " ",$limitmsg," ",$statusmsg," ..</b><p>\n";
	}
@rv = reverse(@rv);

$showto = $folder->{'sent'} || $folder->{'drafts'} || $userconfig{'show_to'};
$showfrom = !($folder->{'sent'} || $folder->{'drafts'}) || $userconfig{'show_to'};
if (@rv) {
	print "<form action=delete_mail.cgi method=post>\n";
	print "<input type=hidden name=folder value='$in{'folder'}'>\n";
	if ($userconfig{'top_buttons'}) {
		if (!$multi_folder) {
			&show_mailbox_buttons(1, \@folders, $folder, \@rv);

			print &select_all_link("d", 0, $text{'mail_all'}),"\n";
			print &select_invert_link("d", 0, $text{'mail_invert'});
			print "<br>\n";
			}
		}
	print "<table border width=100%>\n";
	print "<tr $tb> ",
	      $multi_folder ? "<td><b>$text{'mail_folder'}</b></td>"
			    : "<td>&nbsp;</td> ",
	      ($showfrom ? "<td><b>$text{'mail_from'}</b></td> " : ""),
	      ($showto ? "<td><b>$text{'mail_to'}</b></td> " : ""),
	      "<td><b>$text{'mail_date'}</b></td> ",
	      "<td><b>$text{'mail_size'}</b></td> ",
	      "<td><b>$text{'mail_subject'}</b></td> </tr>\n";
	}
foreach $m (@rv) {
	local $idx = $m->{'idx'};
	local $mf = $m->{'folder'};
	print "<tr $cb>\n";
	if ($multi_folder) {
		print "<td>$mf->{'name'}</td>\n";
		}
	else {
		print "<td><input type=checkbox name=d value=$idx></td>\n";
		}
	if ($showfrom) {
		print "<td nowrap><a href='view_mail.cgi?idx=$idx&".
		      "folder=$mf->{'index'}'>",
		      &simplify_from($m->{'header'}->{'from'}),"</td>\n";
		}
	if ($showto) {
		print "<td nowrap><a href='view_mail.cgi?idx=$idx&".
		      "folder=$mf->{'index'}'>",
		      &simplify_from($m->{'header'}->{'to'}),"</td>\n";
		}
	print "<td nowrap>",&simplify_date($m->{'header'}->{'date'}),"</td>\n";
	print "<td nowrap>",int($m->{'size'}/1000)+1," kB","</td>\n";
	print "<td><table border=0 cellpadding=0 cellspacing=0 width=100%>",
	      "<tr><td>",&simplify_subject($m->{'header'}->{'subject'}),
	      "</td> <td align=right>";
	local @icons = &message_icons($m,
				      $mf->{'drafts'} || $mf->{'sent'});
	print join("&nbsp;", @icons);
	print "</td></tr></table></td> </tr>\n";
	&update_delivery_notification($m, $m->{'folder'});
	$anyvirt++ if ($m->{'folder'}->{'type'} == 6);
	}
if (@rv) {
	print "</table>\n";
	if (!$multi_folder) {
		print &select_all_link("d", 0, $text{'mail_all'}),"\n";
		print &select_invert_link("d", 0, $text{'mail_invert'});
		print "<br>\n";

		&show_mailbox_buttons(2, \@folders, $folder, \@rv);
		}
	print "</form><p>\n";

	if (!$anyvirt) {
		# Show button to turn into virtual folder
		print "<hr>\n";
		print &ui_form_start("virtualize.cgi");
		$i = 0;
		foreach $m (reverse(@rv)) {
			print &ui_hidden("idx_$i", $m->{'idx'}." ".$m->{'folder'}->{'index'}),"\n";
			$i++;
			}
		print &ui_submit($text{'search_virtualize'}),"\n";
		print &ui_textbox("virtual", "", 40),"\n";
		print &ui_form_end();
		}
	}
else {
	print "<b>$text{'search_none'}</b> <p>\n";
	}

&ui_print_footer($in{'simple'} ? ( ) : ( "search_form.cgi?folder=$in{'folder'}",
				$text{'sform_return'} ),
	"index.cgi?folder=$in{'folder'}", $text{'mail_return'});
&pop3_logout_all();

