#!/usr/local/bin/perl
# Turn on or off two-factor

use strict;
use warnings;
require './twofactor-lib.pl';
our (%in, %text, $remote_user);
&error_setup($text{'enable_err'});
&ReadParse();

# Is it even enabled?
my %miniserv;
&get_miniserv_config(\%miniserv);
if (!$miniserv{'twofactor_provider'}) {
	&error($text{'twofactor_setup'});
	}

# Get the user's current state
my ($provid, $id, $api) = &get_user_twofactor($remote_user, \%miniserv);
my $user = { 'name' => $remote_user,
	     'twofactor_id' => $id,
	     'twofactor_apikey' => $api,
	     'twofactor_prov' => $provid };

if ($in{'enable'}) {
	# Validate enrollment inputs
	my $vfunc = "parse_twofactor_form_".
		    $miniserv{'twofactor_provider'};
	my $details;
	if (defined(&{\&{$vfunc}})) {
		$details = &{\&{$vfunc}}(\%in, $user);
		&error($details) if (!ref($details));
		}

	&ui_print_header(undef, $text{'enable_title'}, "");
	my ($prov) = grep { $_->[0] eq $miniserv{'twofactor_provider'} }
		       &list_twofactor_providers();

	# Register user
	print &text('twofactor_enrolling', $prov->[1]),"<br>\n";
	my $efunc = "enroll_twofactor_".$miniserv{'twofactor_provider'};
	my $err = &{\&{$efunc}}($details, $user);
	if ($err) {
		# Failed!
		print &text('twofactor_failed', $err),"<p>\n";
		}
	else {
		print &text('twofactor_done', $user->{'twofactor_id'}),"<p>\n";

		# Print provider-specific message
		my $mfunc = "message_twofactor_".
			    $miniserv{'twofactor_provider'};
		if (defined(&{\&{$mfunc}})) {
			print &{\&{$mfunc}}($user);
			}

		# Save user
		&save_user_twofactor($remote_user, \%miniserv,
			$miniserv{'twofactor_provider'},
			$user->{'twofactor_id'},
			$user->{'twofactor_apikey'});
		&reload_miniserv();
		}

	&ui_print_footer("/", $text{'index'});
	}
elsif ($in{'disable'}) {
	# Turn off for this user
	&save_user_twofactor($remote_user, \%miniserv);
	&reload_miniserv();
	&redirect("");
	}
else {
	&error($text{'twofactor_ebutton'});
	}
