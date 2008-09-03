#!/usr/local/bin/perl
# Change a key's trust level, add an email address, or set the passphrase

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
$key = $keys[$in{'idx'}];
($del) = grep { /^delete_(\d+)$/ } keys %in;

if ($in{'add'}) {
	# Add an owner
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
	$rv = &wait_for($fh, "command>", "passphrase:");
	if ($rv == 1) {
		$pass = &get_passphrase($key);
		syswrite($fh, $pass."\n");
		&wait_for($fh, "command>");
		}
	syswrite($fh, "quit\n");
	if (&wait_for($fh, "save changes") == 0) {
		syswrite($fh, "y\n");
		}
	sleep(1);
	close($fh);
	&redirect("edit_key.cgi?idx=$in{'idx'}");
	}
elsif ($del =~ /^delete_(\d+)$/) {
	# Remove an owner
	$main::wait_for_debug = 1;
	$delidx = $1;
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
	$rv = &wait_for($fh, "command>", "passphrase:");
	if ($rv == 1) {
		$pass = &get_passphrase($key);
		syswrite($fh, $pass."\n");
		&wait_for($fh, "command>");
		}
	syswrite($fh, "quit\n");
	if (&wait_for($fh, "save changes") == 0) {
		syswrite($fh, "y\n");
		}
	sleep(1);
	close($fh);
	&redirect("edit_key.cgi?idx=$in{'idx'}");
	}
elsif ($key->{'secret'}) {
	# Set passphrase
	&put_passphrase($in{'pass'}, $keys[$in{'idx'}]);
	&redirect("list_keys.cgi");
	}
else {
	# Set trust level
	$in{'trust'} || &error($text{'trust_echoice'});
	&ui_print_header(undef, $text{'trust_title'}, "");

	$cmd = "$gpgpath --edit-key \"$key->{'name'}->[0]\"";
	($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
	&wait_for($fh, "command>");
	syswrite($fh, "trust\n");
	&wait_for($fh, "decision");
	syswrite($fh, $in{'trust'}."\n");
	syswrite($fh, "quit\n");
	sleep(1);
	close($fh);

	print &text('trust_done', "<tt>$key->{'name'}->[0]</tt>"),"<p>\n";
	}

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

