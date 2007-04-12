#!/usr/local/bin/perl
# save_auth.cgi
# Save, create or delete an authorized key

require './ssh-lib.pl';
&ReadParse();
@auths = &list_auths();
if ($in{'new'}) {
	$auth = { 'type' => $in{'type'} };
	}
else {
	$auth = $auths[$in{'idx'}];
	}

if ($in{'delete'}) {
	# Just delete this authorized key
	&delete_auth($auth);
	}
else {
	# Validate inputs
	&error_setup($text{'auth_err'});
	$in{'name'} =~ /^\S+$/ || &error($text{'auth_ename'});
	$auth->{'name'} = $in{'name'};
	if ($auth->{'type'} == 1) {
		$in{'bits'} =~ /^\d+$/ || &error($text{'auth_ebits'});
		$auth->{'bits'} = $in{'bits'};
		$in{'exp'} =~ /^\d+$/ || &error($text{'auth_eexp'});
		$auth->{'exp'} = $in{'exp'};
		}
	else {
		$auth->{'keytype'} = $in{'keytype'};
		}
	$in{'key'} =~ s/\s//g;
	if ($auth->{'type'} == 1) {
		$in{'key'} =~ /^\d+$/ || &error($text{'auth_ekey'});
		}
	else {
		$in{'key'} =~ /^[a-z0-9\+\/=]+$/i || &error($text{'auth_ekey2'});
		}
	$auth->{'key'} = $in{'key'};

	# Validate option inputs
	&parse_options($auth->{'opts'}, \%opts);
	if ($in{'from_def'}) {
		delete($opts{'from'});
		}
	else {
		$opts{'from'} = [ join(",", split(/\s+/, $in{'from'})) ];
		}
	if ($in{'command'}) {
		$opts{'command'} = [ $in{'command'} ];
		}
	else {
		delete($opts{'command'});
		}
	if ($in{'noport'}) { $opts{'no-port-forwarding'} = [ undef ]; }
	else { delete($opts{'no-port-forwarding'}); }
	if ($in{'nox11'}) { $opts{'no-x11-forwarding'} = [ undef ]; }
	else { delete($opts{'no-x11-forwarding'}); }
	if ($in{'noagent'}) { $opts{'no-agent-forwarding'} = [ undef ]; }
	else { delete($opts{'no-agent-forwarding'}); }
	if ($in{'nopty'}) { $opts{'no-pty'} = [ undef ]; }
	else { delete($opts{'no-pty'}); }
	$auth->{'opts'} = &join_options(\%opts);

	# Create or save the authorized key
	if ($in{'new'}) {
		&create_auth($auth);
		}
	else {
		&modify_auth($auth);
		}
	}
&redirect("list_auths.cgi");

