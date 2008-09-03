#!/usr/local/bin/perl
# signkey.cgi
# Sign a key, after asking the user if he is sure

require './gnupg-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'signkey_title'}, "");

@keys = &list_keys();
$key = $keys[$in{'idx'}];
($secret) = grep { $_->{'secret'} } @keys;

if ($in{'confirm'}) {
	# Do it!
	$cmd = "$gpgpath --edit-key \"$key->{'name'}->[0]\"";
	($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
	&wait_for($fh, "command>");
	syswrite($fh, "sign\n");
	while(1) {
		$rv = &wait_for($fh, "really sign all",
				'really sign\?', "already", "your selection",
				"passphrase", "nothing to sign", "command>",
				"(error|failed).*", "expire at the same time");
		sleep(1);
		if ($rv == 0 || $rv == 1) {
			syswrite($fh, "y\n");
			}
		elsif ($rv == 2 || $rv == 5) {
			print "<p>",&text('signkey_already',
				  "<tt>$key->{'name'}->[0]</tt>"),"<p>\n";
			last;
			}
		elsif ($rv == 3) {
			syswrite($fh, $in{'trust'}."\n");
			}
		elsif ($rv == 4) {
			$pass = &get_passphrase();
			syswrite($fh, "$pass\n");
			}
		elsif ($rv == 6) {
			print "<p>",&text('signkey_success',
			  "<tt>$key->{'name'}->[0]</tt>"),"<p>\n";
			last;
			}
		elsif ($rv == 7) {
			print "<p>",&text('signkey_failed',
			  "<tt>$key->{'name'}->[0]</tt>",
			  "<pre>$wait_for_input</pre>"),"<p>\n";
			last;
			}
		elsif ($rv == 8) {
			syswrite($fh, "y\n");
			}
		else {
			# Unknown response!
			last;
			}
		}
	syswrite($fh, "quit\n");
	$rv = &wait_for($fh, "save changes");
	if ($rv == 0) {
		syswrite($fh, "y\n");
		sleep(1);
		}
	close($fh);
	}
else {
	# Ask the user if he is sure
	print &ui_confirmation_form("signkey.cgi", 
	  &text('signkey_confirm', "<tt>$key->{'name'}->[0]</tt>",
	  $key->{'email'}->[0] ? "&lt;<tt>$key->{'email'}->[0]</tt>&gt;" : "",
	  "<tt>".&key_fingerprint($key)."</tt>"),
	  [ [ "idx", $key->{'index'} ] ],
	  [ [ "confirm", $text{'key_sign'} ] ],
	  $text{'signkey_trustlevel'}." ".
	  &ui_select("trust", 0,
		     [ map { [ $_, $text{'signkey_trust'.$_} ] } (0..3) ])
	  );
	}

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

