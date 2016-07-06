#!/usr/local/bin/perl
# inbox_logout.cgi
# Clear inbox POP3 login and password
use strict;
use warnings;
our %in;
our $user_module_config_directory;

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];

if ($folder->{'type'} == 2) {
	unlink("$user_module_config_directory/inbox.pop3");
	}
else {
	unlink("$user_module_config_directory/inbox.imap");
	}
&redirect("index.cgi?folder=$in{'folder'}");
