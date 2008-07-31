#!/usr/local/bin/perl
# Do the setup

require './spam-lib.pl';
&ReadParse();
&error_setup($text{'razor_err'});

# Validate inputs
$in{'user_def'} || $in{'user'} =~ /\S/ || &error($text{'razor_euser'});
$in{'pass_def'} || $in{'pass'} =~ /\S/ || &error($text{'razor_epass'});

# Do it
&ui_print_header(undef, $text{'razor_title'}, "");

print "<p>$text{'razor_doing'}<br>\n";
$cmd = "$config{'razor_admin'} -create -register";
$cmd .= " -user ".quotemeta($in{'user'}) if (!$in{'user_def'});
$cmd .= " -pass ".quotemeta($in{'pass'}) if (!$in{'pass_def'});
$out = `cd $remote_user_info[7] ; $cmd 2>&1 </dev/null`;
print "<pre>$out</pre>\n";
if ($? || !-r "$remote_user_info[7]/.razor/identity") {
	print "$text{'razor_failed'}<p>\n";
	}
else {
	print "$text{'razor_done'}<p>\n";
	}

&ui_print_footer("", $text{'index_return'});

