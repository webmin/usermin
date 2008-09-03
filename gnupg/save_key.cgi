#!/usr/local/bin/perl
# Change a key's trust level, add an email address, or set the passphrase

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
$key = $keys[$in{'idx'}];
($del) = grep { /^delete_(\d+)$/ } keys %in;

if ($in{'add'}) {
	# Add an owner
	# XXX
	}
elsif ($del =~ /^delete_(\d+)$/) {
	# Remove an owner
	$nameidx = $1;
	# XXX
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

