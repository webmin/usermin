#!/usr/local/bin/perl
# inbox_login.cgi
# Save inbox POP3 login and password
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %pop3);
our $user_module_config_directory;

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];

# Validate inputs
&error_setup($text{'mail_loginerr'});
$in{'user'} =~ /\S/ || &error($text{'save_euser'});
$folder->{'user'} = $pop3{'user'} = $in{'user'};
$folder->{'pass'} = $pop3{'pass'} = $in{'pass'};
if ($folder->{'type'} == 2) {
	# Try POP3 login
	my @err = &pop3_login($folder);
	if ($err[0] == 0) {
		&error($err[1]);
		}
	elsif ($err[0] == 2) {
		&error(&text('save_elogin', $err[1]));
		}
	else {
		&pop3_logout($err[1], 1);
		}

	# Save inbox .pop3 file
	&write_file("$user_module_config_directory/inbox.pop3", \%pop3);
	chmod(0700, "$user_module_config_directory/inbox.pop3");
	}
else {
	# Try IMAP login
	$folder->{'mailbox'} = $pop3{'mailbox'} = undef;
	my @err = &imap_login($folder);
	if ($err[0] == 0) {
		&error($err[1]);
		}
	elsif ($err[0] == 2) {
		&error(&text('save_elogin2', $err[1]));
		}
	elsif ($err[0] == 3) {
		&error(&text('save_emailbox', $err[1]));
		}
	else {
		&imap_logout($err[1], 1);
		}

	# Save inbox .imap file
	&write_file("$user_module_config_directory/inbox.imap", \%pop3);
	chmod(0700, "$user_module_config_directory/inbox.imap");
	}
&redirect("index.cgi?folder=$in{'folder'}");
