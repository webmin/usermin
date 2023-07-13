#!/usr/local/bin/perl
# import.cgi
# Import somebody's public key

require './gnupg-lib.pl';
&ReadParseMime();
&error_setup($text{'import_err'});

if ($in{'mode'} == 0) {
	# From uploaded file, saved to temp
	$in{'upload'} || &error($text{'import_ekey'});
	$temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $in{'upload'};
	close(TEMP);
	$out = &backquote_command(
		"$gpgpath --import ".quotemeta($temp)." 2>&1");
	unlink($temp);
	}
elsif ($in{'mode'} == 1) {
	# From local file
	$in{'local'} = "$remote_user_info[7]/$in{'local'}"
		if ($in{'local'} !~ /^\//);
	-r $in{'local'} || &error($text{'import_efile'});
	$out = &backquote_command(
		"$gpgpath --import ".quotemeta($in{'local'})." 2>&1");
	}
elsif ($in{'mode'} == 2) {
	# From pasted text
	$in{'text'} || &error($text{'import_etext'});
	$in{'text'} =~ s/\r//g;
	$temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $in{'text'};
	close(TEMP);
	$out = &backquote_command(
		"$gpgpath --import ".quotemeta($temp)." 2>&1");
	unlink($temp);
	}
if ($?) {
	&error(&text('import_egpg', "<tt>$out</tt>"));
	}
&redirect("list_keys.cgi");

