#!/usr/local/bin/perl
# Show a form for setting up scheduled folder clearing
use strict;
use warnings;
our (%text, %in, %config);

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'idx'}];

# Validate inputs
my $auto = &get_auto_schedule($folder);
$auto ||= { };
$auto->{'enabled'} = $in{'enabled'};
$auto->{'mode'} = $in{'mode'};
if ($in{'mode'} == 0) {
	$in{'days'} =~ /^\d+$/ || &error($text{'auto_edays'});
	$auto->{'days'} = $in{'days'};
	$auto->{'invalid'} = $in{'invalid'};
	}
else {
	$in{'size'} =~ /^\d+$/ || &error($text{'auto_esize'});
	$auto->{'size'} = $in{'size'}*$in{'size_units'};
	}
$auto->{'all'} = $in{'all'};
if ($in{'all'} == 2) {
	$auto->{'dest'} = $in{'dest'};
	my ($dest) = grep { &folder_name($_) eq $in{'dest'} } @folders;
	$dest || &error($text{'auto_edest'});
	$dest->{'nowrite'} && &error($text{'auto_ewrite'});
	}

# Save schedule, and setup cron job
&save_auto_schedule($folder, $auto);
&setup_auto_cron() if ($auto->{'enabled'});

&redirect($config{'mail_system'} == 4 ? "list_ifolders.cgi"
				      : "list_folders.cgi");
