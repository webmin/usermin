#!/usr/local/bin/perl
# Set or clear the user's recovery address

require './changepass-lib.pl';
&error_setup($text{'recovery_err'});
&ReadParse();

# Save or clear
if ($in{'recovery_def'}) {
	&save_recovery_address(undef);
	}
else {
	$in{'recovery'} =~ /^\S+\@\S+$/ || &error($texy{'recovery_eemail'});
	&save_recovery_address($in{'recovery'});
	}

# Tell the user
&ui_print_header(undef, $text{'recovery_title'}, "");

if ($in{'recovery_def'}) {
	print $text{'recovery_cleared'},"<p>\n";
	}
else {
	print &text('recovery_set',
		"<tt>".&html_escape($in{'recovery'})."</tt>"),"<p>\n";
	}

&ui_print_footer("", $text{'index_return'});
