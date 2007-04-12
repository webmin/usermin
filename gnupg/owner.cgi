#!/usr/local/bin/perl
# owner.cgi
# Add or delete an owner from a key

require './gnupg-lib.pl';
&ReadParse();

@keys = &list_keys();
$key = $keys[$in{'idx'}];

if ($in{'add'}) {
	# Adding details
	&error_setup($text{'owner_err1'});
	$in{'name'} =~ /\S/ || &error($text{'owner_ename'});
	if ($in{'name'} =~ s/\((.*)\)\s*$//) {
		$cmt = $1;
		$in{'name'} =~ s/\s+$//;
		}

	$cmd = "$gpgpath --edit-key \"$key->{'name'}->[0]\"";
	($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
	&wait_for($fh, "command>");
	syswrite($fh, "adduid\n");
	&wait_for($fh, "name:");
	syswrite($fh, "$in{'name'}\n");
	&wait_for($fh, "address:");
	syswrite($fh, "$in{'email'}\n");
	&wait_for($fh, "comment:");
	syswrite($fh, "$cmt\n");
	&wait_for($fh, "\\?");
	syswrite($fh, "o\n");
	&wait_for($fh, "command>");
	syswrite($fh, "quit\n");
	if (&wait_for($fh, "save changes") == 0) {
		syswrite($fh, "y\n");
		}
	sleep(1);
	close($fh);
	}
else {
	# Deleting details
	foreach $k (keys %in) {
		$delidx = $k if ($k =~ /^\d+$/);
		}
	&error_setup($text{'owner_err2'});
	if (@{$key->{'name'}} == 1) {
		&error($text{'owner_elast'});
		}
	$cmd = "$gpgpath --edit-key \"$key->{'name'}->[0]\"";
	($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
	local %keymap;
	while(1) {
		local $rv = &wait_for($fh, "command>", '\\((\d+)\\)[\\. ]+(.*)\\n');
		last if ($rv == 0);
		$matches[2] =~ s/<.*$//;
		$matches[2] =~ s/\s+$//;
		$keymap{$matches[2]} = $matches[1];
		}
	local $idx = $keymap{$key->{'name'}->[$delidx]};
	syswrite($fh, "uid $idx\n");
	&wait_for($fh, "command>");
	syswrite($fh, "deluid\n");
	&wait_for($fh, "\\?");
	syswrite($fh, "y\n");
	&wait_for($fh, "command>");
	syswrite($fh, "quit\n");
	if (&wait_for($fh, "save changes") == 0) {
		syswrite($fh, "y\n");
		}
	sleep(1);
	close($fh);
	}

&redirect("edit_key.cgi?idx=$in{'idx'}");

