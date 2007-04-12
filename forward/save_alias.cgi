#!/usr/local/bin/perl
# save_alias.cgi
# Save or delete a new or existing .forward entry

require './forward-lib.pl';
&ReadParse();
&error_setup($text{'asave_err'});
if (!$in{'new'}) {
	if ($config{'mail_system'} == 0) {
		@aliases = &list_aliases();
		$a = $aliases[$in{'num'}];
		}
	else {
		$a = &get_dotqmail($in{'file'});
		}
	}

if ($in{'delete'}) {
	# delete some alias
	$loga = $a;
	&delete_alias($a);
	}
else {
	# saving or creating .. check inputs
	local %types = map { $_, 1 } split(/\,/, $config{'types'});
	$types{8} = $types{5};
	for($i=0; defined($t = $in{"type_$i"}); $i++) {
		!$t || $types{$t} || &error($text{'asave_ecannot'});
		$v = $in{"val_$i"};
		if ($t == 1 && $v !~ /^([^\/\|:]\S*)$/) {
			&error(&text('asave_etype1', $v));
			}
		elsif ($t == 3 && $v !~ /^\/(\S+)$/ && $config{'mail_system'} == 0) {
			&error(&text('asave_etype3', $v));
			}
		elsif ($t == 3 && $v !~ /^[\/\.](\S+)$/ && $config{'mail_system'} == 1) {
			&error(&text('asave_etype3', $v));
			}
		elsif ($t == 4) {
			$v =~ /^(\S+)/ || &error($text{'asave_etype4none'});
			-x $1 || &error(&text('asave_etype4', $1));
			}
		elsif ($t == 5 && !$v) {
			&error(&text('asave_etype5'));
			}
		elsif ($t == 6 && !$v) {
			&error(&text('asave_etype6'));
			}
		elsif ($t == 2 &&  $config{'mail_system'} == 1) {
			&error(&text('asave_etype1q', $v));
			}
		elsif ($t == 7 &&  $config{'mail_system'} == 1 && !$mail_path) {
			&error(&text('asave_etype2q', $v));
			}
		if ($t >= 2 && $t <= 6 && $v !~ /^\//) {
			# Path is relative to home dir
			$v = "$remote_user_info[7]/$v";
			}
		if ($t == 1 || $t == 3) { push(@values, $v); }
		elsif ($t == 2) { push(@values, ":include:$v"); }
		elsif ($t == 4) { push(@values, "|$v"); }
		elsif ($t == 5) {
			# Setup autoreply script
			push(@values, "|$module_config_directory/autoreply.pl $v $remote_user");
			}
		elsif ($t == 6) {
			# Setup filter script
			push(@values, "|$module_config_directory/filter.pl $v $remote_user");
			}
		elsif ($t == 7) {
			# Just write to user's mail file
			push(@values, $config{'mail_system'} ? $mail_path : "\\$remote_user");
			}
		elsif ($t == 8) {
			# Set up vacation program
			if ($a && $a->{'values'}->[$i] &&
			    &alias_type($a->{'values'}->[$i]) == 8) {
				# Use old settings
				push(@values, $a->{'values'}->[$i]);
				}
			else {
				# Default vacation setup
				push(@values, "|$vacation_path $remote_user");
				system("vacation -i >/dev/null 2>&1");
				}
			}
		}

	@values || &error($text{'asave_enone'});
	$newa{'values'} = \@values;
	if ($config{'mail_system'} == 0) {
		$newa{'enabled'} = $in{'enabled'};
		}
	else {
		$in{'name_def'} || $in{'name'} =~ /^\S+$/ ||
			&error($text{'asave_ename'});
		$newa{'name'} = $in{'name_def'} ? undef : $in{'name'};
		if ($in{'new'} || $newa{'name'} ne $a->{'name'}) {
			@aliases = &list_dotqmails();
			($same) = grep { $_->{'name'} eq $newa{'name'} } @aliases;
			$same && &error($text{'asave_esame'});
			}
		}
	if ($in{'new'}) { &create_alias(\%newa); }
	else { &modify_alias($a, \%newa); }
	$loga = \%newa;
	}
&redirect("");

