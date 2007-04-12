#!/usr/local/bin/perl
# import.cgi
# Import somebody's public key

require './gnupg-lib.pl';
&ReadParseMime();
&error_setup($text{'import_err'});

if ($in{'mode'} == 0) {
	$in{'key'} || &error($text{'import_ekey'});
	$temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $in{'key'};
	close(TEMP);
	$out = `$gpgpath --import $temp 2>&1`;
	unlink($temp);
	}
else {
	$in{'file'} = "$remote_user_info[7]/$in{'file'}"
		if ($in{'file'} !~ /^\//);
	-r $in{'file'} || &error($text{'import_efile'});
	$out = `$gpgpath --import '$in{'file'}' 2>&1`;
	}
if ($?) {
	&error(&text('import_egpg', "<tt>$out</tt>"));
	}
&redirect("list_keys.cgi");

