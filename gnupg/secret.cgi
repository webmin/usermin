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
my $temp = &transname();
$in{'size'} ||= 2048;
&open_tempfile(TEMP, ">$temp", 0, 1);
&print_tempfile(TEMP, "Key-Type: default\n");
&print_tempfile(TEMP, "Key-Length: $in{'size'}\n");
&print_tempfile(TEMP, "Key-Usage: sign,encrypt,auth\n");
&print_tempfile(TEMP, "Name-Real: $in{'name'}\n");
&print_tempfile(TEMP, "Name-Email: $in{'email'}\n");
if ($in{'comment'}) {
	&print_tempfile(TEMP, "Name-Comment: $in{'comment'}\n");
	}
&print_tempfile(TEMP, "Expire-Date: 0\n");
if ($in{'pass'}) {
	&print_tempfile(TEMP, "Passphrase: $in{'pass'}\n");
	}
else {
	&print_tempfile(TEMP, "%no-protection\n");
	}
&print_tempfile(TEMP, "%commit\n");
&print_tempfile(TEMP, "%echo done\n");
&close_tempfile(TEMP);
($out, $timed_out) = &backquote_with_timeout(
                "$gpgpath --gen-key --batch $temp 2>&1 </dev/null", 90);
$err = $?;

&ui_print_header(undef, $text{$pfx.'_title'}, "");

if ($err || $timed_out) {
	print "<p>",&text('setup_failed', "<pre>$out</pre>"),"<p>\n";
	}
else {
	print "<p>$text{$pfx.'_ok'}<p>\n";
	@keys = &list_secret_keys();
	($key) = grep { !$oldid{$_->{'key'}} } @keys;
	&put_passphrase($in{'pass'}, $key);
	}

&ui_print_footer("", $text{'index_return'});
