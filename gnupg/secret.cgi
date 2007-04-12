#!/usr/local/bin/perl
# setup.sh
# Call gnupg to setup a key initially

require './gnupg-lib.pl';
&ReadParse();
$pfx = $in{'newkey'} ? 'secret' : 'setup';
&error_setup($text{$pfx.'_err'});

# Validate inputs
$in{'name'} || &error($text{'setup_ename'});
length($in{'name'}) >= 5 || &error(&text('setup_enamelen', 5));
#$in{'email'} || &error($text{'setup_eemail'});

# Run gpg --list-keys to create the directory
&list_keys();
&list_keys();

# Create .gnupg directory if missing
if (!-d "$remote_user_info[7]/.gnupg") {
	mkdir("$remote_user_info[7]/.gnupg", 0700) ||
		&error(&text('setup_emkdir', $!));
	}

$pid = fork();
if (!$pid) {
	# Run the find command in a subprocess to generate some entropy
	untie(*STDOUT);
	untie(*STDERR);
	close(STDOUT);
	close(STDERR);
	exec("find / -type f");
	exit(0);
	}

foreach $k (&list_secret_keys()) {
	$oldid{$k->{'key'}}++;
	}

# Run the gpg --gen-key command
$SIG{ALRM} = "gpg_timeout";
alarm(90);
&foreign_require("proc", "proc-lib.pl");
($fh, $fpid) = &foreign_call("proc", "pty_process_exec", "$gpgpath --gen-key");
&wait_for($fh, "Your selection");
syswrite($fh, "\n");
&wait_for($fh, "you want");
if ($in{'keysize'}) {
	syswrite($fh, "$in{'keysize'}\n");
	}
else {
	syswrite($fh, "\n");
	}
&wait_for($fh, "valid for");
syswrite($fh, "\n");
&wait_for($fh, "correct");
syswrite($fh, "y\n");
&wait_for($fh, "Real name");
syswrite($fh, "$in{'name'}\n");
&wait_for($fh, "Email address");
syswrite($fh, "$in{'email'}\n");
&wait_for($fh, "Comment");
syswrite($fh, "$in{'comment'}\n");
&wait_for($fh, "Change");
syswrite($fh, "O\n");
&wait_for($fh, "passphrase");
sleep(1);
syswrite($fh, "$in{'pass'}\n");
&wait_for($fh, "passphrase");
sleep(1);
syswrite($fh, "$in{'pass'}\n");
&wait_for($fh);
close($fh);
$err = $?;
alarm(0);
kill('TERM', $pid);

&ui_print_header(undef, $text{$pfx.'_title'}, "");

if ($err || $timed_out) {
	print "<p>",&text('setup_failed', "<pre>$wait_for_input</pre>"),"<p>\n";
	}
else {
	print "<p>$text{$pfx.'_ok'}<p>\n";
	@keys = &list_secret_keys();
	($key) = grep { !$oldid{$_->{'key'}} } @keys;
	&put_passphrase($in{'pass'}, $key);
	}

&ui_print_footer("", $text{'index_return'});

sub gpg_timeout
{
kill('KILL', $fpid) if ($fpid);
$timed_out++;
}

