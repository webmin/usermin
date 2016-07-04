#!/usr/local/bin/perl
# save_imap.cgi
# Create, modify or delete an IMAP folder
use strict;
use warnings;
our (%text, %in);
our %folder_types;

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my ($folder, $old);
if (!$in{'new'}) {
	$folder = $folders[$in{'idx'}];
	$old = { %$folder };
	}
else {
	$folder = { 'type' => 4,
		    'mode' => 0 };
	}
&error_setup($text{'save_err'});
$folder_types{'imap'} || &error($text{'save_ecannot'});

if ($in{'delete'}) {
	# Just delete this folder and cache
	&delete_folder($folder);
	}
else {
	# Validate inputs
	$in{'name'} =~ /\S/ || &error($text{'save_ename'});
	gethostbyname($in{'server'}) || &check_ipaddress($in{'server'}) ||
		&error($text{'save_eserver'});
	$in{'port_def'} || $in{'port'} =~ /^\d+$/ ||
		&error($text{'save_eport'});
	$in{'user_def'} || $in{'user'} =~ /\S/ || &error($text{'save_euser'});
	$in{'mailbox_def'} || $in{'mailbox'} =~ /^\S+$/ ||
		&error($text{'save_emailbox2'});
	&parse_folder_options($folder, 0, \%in);

	# Save the folder
	$folder->{'name'} = $in{'name'};
	$folder->{'server'} = $in{'server'};
	$folder->{'port'} = $in{'port_def'} ? undef : $in{'port'};
	$folder->{'user'} = $in{'user_def'} ? '*' : $in{'user'};
	$folder->{'pass'} = $in{'pass'};
	$folder->{'perpage'} = $in{'perpage_def'} ? undef : $in{'perpage'};
	$folder->{'fromaddr'} = $in{'fromaddr_def'} ? undef : $in{'fromaddr'};
	$folder->{'sent'} = $in{'sent'};
	$folder->{'mailbox'} = $in{'mailbox_def'} ? undef : $in{'mailbox'};
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
	&save_folder($folder, $old);
	}
&redirect("list_folders.cgi?refresh=".&urlize($folder->{'name'}));
