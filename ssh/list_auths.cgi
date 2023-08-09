#!/usr/local/bin/perl
# list_auths.cgi
# List public keys that are allowed to login to this account

require './ssh-lib.pl';
&ui_print_header(undef, $text{'auths_title'}, "");

@links = ( "<a href='edit_auth.cgi?new=1&type=1'>$text{'auths_add1'}</a>",
	   "<a href='edit_auth.cgi?new=1&type=2'>$text{'auths_add2'}</a>" );

print "$text{'auths_desc'}<p>\n";
@auths = &list_auths();
if (@auths) {
	print &ui_links_row(\@links);
	print &ui_columns_start([ $text{'auths_name'},
				  $text{'auths_key'} ]);
	foreach $a (@auths) {
		print &ui_columns_row([ 
			"<a href='edit_auth.cgi?idx=$a->{'index'}'>".
			  "@{[&html_escape($a->{'name'})]}</a>",
			"<tt>".substr($a->{'key'}, 0, 40)." ... ".
			      substr($a->{'key'}, -40)."</tt>",
			]);
		}
	print &ui_columns_end();
	}
else {
	print "<b>$text{'auths_none'}</b> <p>\n";
	}
print &ui_links_row(\@links);

&ui_print_footer("", $text{'index_return'});

