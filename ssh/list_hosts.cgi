#!/usr/local/bin/perl
# Display client host sections

require './ssh-lib.pl';
&ui_print_header(undef, $text{'hosts_title'}, "");

@rowlinks = ( "<a href='edit_host.cgi?new=1'>$text{'hosts_add'}</a>" );
$hconf = &get_client_config();
$i = 0;
foreach $h (@$hconf) {
	if (lc($h->{'name'}) eq 'host') {
		push(@links, "edit_host.cgi?idx=$i");
		push(@icons, "images/host.gif");
		push(@titles, $h->{'values'}->[0] eq '*' ? "<i>$text{'hosts_all'}</i>" : &html_escape($h->{'values'}->[0]));
		}
	$i++;
	}
if (@links) {
	print &ui_links_row(\@rowlinks);
	&icons_table(\@links, \@titles, \@icons);
	}
else {
	print "<b>$text{'hosts_none'}</b><p>\n";
	}
print &ui_links_row(\@rowlinks);

&ui_print_footer("", $text{'index_return'});
