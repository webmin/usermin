#!/usr/local/bin/perl
# change_trust.cgi
# Change the trust level for a key

require './gnupg-lib.pl';
&ReadParse();
$in{'trust'} || &error($text{'trust_echoice'});
&ui_print_header(undef, $text{'trust_title'}, "");

@keys = &list_keys();
$key = $keys[$in{'idx'}];

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

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

