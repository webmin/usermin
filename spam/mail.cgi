#!/usr/local/bin/perl
# mail.cgi
# Display messages that have been categorized as spam

require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
&ReadParse();
$folder = &spam_file_folder();
&disable_indexing($folder);
dbmopen(%read, "$user_config_directory/mailbox/read", 0600);

$ref = $userconfig{'refresh'} || $mailbox::userconfig{'refresh'};
if ($ref) {
	print "Refresh: $ref\r\n";
	&ui_print_header(undef, $text{'mail_title'}, "", undef, 0, 0, 0,
		$ref > 60 ? &text('mail_will', int($ref/60)) :
			    &text('mail_wills', $ref));
	}
else {
	&ui_print_header(undef, $text{'mail_title'}, "");
	}
print &check_clicks_function() if (defined(&check_clicks_function));

#print "$text{'mail_desc'}<p>\n";

# View mail from the most recent
$perpage = $folder->{'perpage'} || $mailbox::userconfig{'perpage'};
@mail = &mailbox::mailbox_list_mails_sorted($in{'start'},
				    $in{'start'}+$perpage-1,
				    $folder, 1, \@error);
print "<form action=mail.cgi><center>\n";
if ($in{'start'}+$perpage < @mail) {
	printf "<a href='mail.cgi?start=%d'>%s</a>\n",
		$in{'start'}+$perpage,
		'<img src=/images/left.gif border=0 align=middle>';
	}

local $s = @mail-$in{'start'};
local $e = @mail-$in{'start'}-$perpage+1;
print "<font size=+1>\n";
if (@mail) {
	print &text('mail_pos', $s, $e < 1 ? 1 : $e, scalar(@mail));
	}
else {
	print &text('mail_none');
	}
print "</font> <input type=submit value='$text{'mail_refresh'}'>\n";

if ($in{'start'}) {
	printf "<a href='mail.cgi?start=%d'>%s</a>\n",
		$in{'start'}-$perpage,
		'<img src=/images/right.gif border=0 align=middle>';
	}
print "</center></form>\n";

print "<form action=process.cgi method=post>\n";
if ($mailbox::userconfig{'top_buttons'} && @mail) {
	&show_buttons(1);
	print &select_all_link("d", 1, $mailbox::text{'mail_all'}),"&nbsp;\n";
	print &select_invert_link("d", 1, $mailbox::text{'mail_invert'}),"&nbsp;\n";
	}

if (@mail) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td>&nbsp;</td> ",
	      "<td><b>$mailbox::text{'mail_from'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_date'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_size'}</b></td> ",
	      "<td><b>$text{'mail_level'}</b></td> ",
	      "<td><b>$mailbox::text{'mail_subject'}</b></td> </tr>\n";
	}

for($i=int($in{'start'}); $i<@mail && $i<$in{'start'}+$perpage; $i++) {
	local $idx = $mail[$i]->{'idx'};
	print "<tr $cb>\n";
	print "<td><input type=checkbox name=d value=$i></td>\n";
	if ($userconfig{'full_from'}) {
		print "<td nowrap><a href='view_mail.cgi?idx=$i'>",
		      &html_escape($mail[$i]->{'header'}->{'from'}),
		      "</td>\n";
		}
	else {
		print "<td nowrap><a href='view_mail.cgi?idx=$i'>",
		      &mailbox::simplify_from($mail[$i]->{'header'}->{'from'}),
		      "</td>\n";
		}
	print "<td nowrap>",&mailbox::simplify_date($mail[$i]->{'header'}->{'date'}),
	      "</td>\n";
	print "<td nowrap>",int($mail[$i]->{'size'}/1000)+1," kB","</td>\n";
	print "<td nowrap>",length($mail[$i]->{'header'}->{'x-spam-level'}),"</td>\n";
	print "<td><table border=0 cellpadding=0 cellspacing=0 width=100%>",
	      "<tr><td>",&mailbox::simplify_subject($mail[$i]->{'header'}->{'subject'}),
	      "</td> <td align=right>";
	if ($mail[$i]->{'header'}->{'content-type'} =~ /multipart\/\S+/i) {
		print "<img src=/mailbox/images/attach.gif>";
		}
	local $p = int($mail[$i]->{'header'}->{'x-priority'});
	if ($p == 1) {
		print "&nbsp;<img src=/mailbox/images/p1.gif>";
		}
	elsif ($p == 2) {
		print "&nbsp;<img src=/mailbox/images/p2.gif>";
		}
	if (!$showto) {
		if ($read{$mail[$i]->{'header'}->{'message-id'}} == 2) {
			print "&nbsp;<img src=/mailbox/images/special.gif>";
			}
		elsif ($read{$mail[$i]->{'header'}->{'message-id'}} == 1) {
			print "&nbsp;<img src=/mailbox/images/read.gif>";
			}
		}
	print "</td></tr></table></td> </tr>\n";
	}
if (@mail) {
	print "</table>\n";
	print &select_all_link("d", 1, $mailbox::text{'mail_all'}),"&nbsp;\n";
	print &select_invert_link("d", 1, $mailbox::text{'mail_invert'}),"&nbsp;\n";
	&show_buttons(2);
	}

print "</form>\n";

# Show search field
print "<table width=100%><tr>\n";
print "<form action=mail_search.cgi><td width=33%>\n";
print "<input type=hidden name=simple value=1>\n";
print "<input type=submit value='$mailbox::text{'mail_search2'}'>\n";
print "<input name=search size=20></td></form>\n";

# Show score search field
print "<form action=mail_search.cgi><td align=center width=33%>\n";
print "<input type=submit value='$text{'mail_search3'}'>\n";
print "<input name=score size=5></td></form>\n";

# Show delete all button
print "<form action=delete_all.cgi><td align=right width=33%>\n";
print "<input type=submit value='$text{'mail_delall'}'></td>\n";
print "</form>\n";

print "</tr></table>\n";

&ui_print_footer("", $text{'index_return'});


