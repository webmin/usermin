#!/usr/local/bin/perl
# signkey.cgi
# Sign a key, after asking the user if he is sure

require './gnupg-lib.pl';
&ReadParse();

@keys = &list_keys();
$key = $keys[$in{'idx'}];
@secrets = grep { $_->{'secret'} } @keys;
($secret) = grep { defined(&signkey_passphrase($_)) } @secrets;
$secret ||= $secrets[0];

&ui_print_header(undef, $text{'signkey_title'}, "");
$keytext = "<tt>".&html_escape($key->{'name'}->[0])."</tt>";

if ($in{'confirm'}) {
	# Do it!
	$secret || &error($text{'gnupg_esignpass'});
	$pass = &signkey_passphrase($secret);
	defined($pass) || &error($text{'gnupg_esignpass'}.". ".
		&text('gnupg_canset', "/gnupg/edit_key.cgi?idx=$secret->{'index'}").".");
	$trust = $in{'trust'} =~ /^[0-3]$/ ? $in{'trust'} : 0;
	if (&gpg_supports_option("--quick-sign-key")) {
		# Use GnuPG's unattended signing mode to avoid hanging on prompt changes.
		$fpr = &key_primary_fingerprint($key);
		$was_signed = &key_signed_by($key, $secret);
		if ($was_signed) {
			print "<p>",&text('signkey_already', $keytext),"<p>\n";
			}
		elsif (!$fpr) {
			print "<p>",&text('signkey_failed', $keytext,
				"<pre>Unable to determine key fingerprint</pre>"),"<p>\n";
			}
		else {
			$cmd = "$gpgpath --batch --yes --no-tty ".
			       "--pinentry-mode loopback ".
			       "--passphrase-file ".quotemeta(&signkey_passphrase_file($secret))." ".
			       "--local-user ".quotemeta($secret->{'key'})." ".
			       "--default-cert-level ".quotemeta($trust)." ".
			       "--quick-sign-key ".quotemeta($fpr);
			&clean_language();
			($out, $timed_out) = &backquote_with_timeout("$cmd 2>&1", 60);
			&reset_environment();
			$is_signed = &key_signed_by($key, $secret);
			if ($is_signed) {
				print "<p>",&text('signkey_success', $keytext),"<p>\n";
				}
			else {
				$out ||= $timed_out ? "Timed out waiting for GnuPG" : "";
				print "<p>",&text('signkey_failed', $keytext,
					"<pre>".&html_escape($out)."</pre>"),"<p>\n";
				}
			}
		}
	else {
		# Older GnuPG fallback.
		$seen_pass = 0;
		$keyid = &key_edit_id($key);
		$cmd = "$gpgpath --edit-key ".quotemeta($keyid);
		($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
		&wait_for($fh, "command>", "gpg>");
		syswrite($fh, "sign\n");
		while(1) {
			$rv = &wait_for($fh, "really sign all",
					'really sign\?', "already",
					"your selection", "your decision",
					"passphrase", "nothing to sign",
					"command>", "gpg>",
					"(error|failed).*", "expire at the same time");
			sleep(1);
			if ($rv == 0 || $rv == 1) {
				syswrite($fh, "y\n");
				}
			elsif ($rv == 2 || $rv == 6) {
				print "<p>",&text('signkey_already', $keytext),"<p>\n";
				last;
				}
			elsif ($rv == 3 || $rv == 4) {
				syswrite($fh, $trust."\n");
				}
			elsif ($rv == 5) {
				if ($seen_pass++) {
					print "<p>",&text('signkey_failed',
					  $keytext,
					  "<pre>".&html_escape($wait_for_input)."</pre>"),"<p>\n";
					last;
					}
				syswrite($fh, "$pass\n");
				}
			elsif ($rv == 7 || $rv == 8) {
				print "<p>",&text('signkey_success', $keytext),"<p>\n";
				last;
				}
			elsif ($rv == 9) {
				print "<p>",&text('signkey_failed',
				  $keytext,
				  "<pre>".&html_escape($wait_for_input)."</pre>"),"<p>\n";
				last;
				}
			elsif ($rv == 10) {
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
	}
else {
	# Ask the user if he is sure
	$email = $key->{'email'}->[0] ?
		 "&lt;<tt>".&html_escape($key->{'email'}->[0])."</tt>&gt;" : "";
	print &ui_confirmation_form("signkey.cgi", 
	  &text('signkey_confirm', $keytext, $email,
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

sub key_signed_by
{
my ($key, $signer) = @_;
my $fpr = &key_primary_fingerprint($key);
return 0 if (!$fpr);
&clean_language();
my $out = &backquote_command("$gpgpath --with-colons --list-sigs ".
			     quotemeta($fpr)." 2>/dev/null");
&reset_environment();
foreach my $line (split(/\r?\n/, $out)) {
	next if ($line !~ /^sig:/);
	my @fields = split(/:/, $line, -1);
	return 1 if (&key_matches_id($fields[4], $signer));
	return 1 if ($fields[12] && &key_matches_id($fields[12], $signer));
	}
return 0;
}

sub signkey_passphrase
{
my ($key) = @_;
my $file = &signkey_passphrase_file($key);
open(PASS, "<", $file) || return undef;
my $pass = <PASS>;
close(PASS);
chomp($pass);
return $pass;
}

sub signkey_passphrase_file
{
my ($key) = @_;
my @files;
if ($key && $key->{'key'}) {
	push(@files, "$user_module_config_directory/pass.$key->{'key'}");
	if ($key->{'key'} =~ /([A-F0-9]{16})$/i) {
		push(@files, "$user_module_config_directory/pass.$1");
		}
	if ($key->{'key'} =~ /([A-F0-9]{8})$/i) {
		push(@files, "$user_module_config_directory/pass.$1");
		}
	}
push(@files, "$user_module_config_directory/pass");
foreach my $file (@files) {
	return $file if (-r $file);
	}
return $key && $key->{'key'} ? &get_passphrase_file($key) : $files[-1];
}

sub key_primary_fingerprint
{
my ($key) = @_;
my $fpr = $key->{'key'} =~ /^[A-F0-9]{40}$/i ? $key->{'key'} :
					    &key_fingerprint($key);
$fpr =~ s/\s+//g;
return $fpr =~ /^[A-F0-9]{40}$/i ? $fpr : undef;
}

sub key_edit_id
{
my ($key) = @_;
return &key_primary_fingerprint($key) || $key->{'key'} || $key->{'name'}->[0];
}

sub gpg_supports_option
{
my ($option) = @_;
my $opts = &backquote_command("$gpgpath --dump-options 2>/dev/null");
return $opts =~ /^\Q$option\E$/m;
}
