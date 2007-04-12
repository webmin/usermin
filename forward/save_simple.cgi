#!/usr/local/bin/perl
# Save simple email forwarding options

require './forward-lib.pl';
&error_setup($text{'simple_err'});
&ReadParse();

# Validate and store inputs
$simple = &get_simple();
$simple->{'local'} = $in{'local'};
if ($in{'forward'}) {
	$in{'forwardto'} || &error($text{'simple_eforward'});
	$in{'forwardto'} =~ /^\S+$/ || &error($text{'simple_eforward2'});
	$simple->{'forward'} = $in{'forwardto'};
	}
else {
	delete($simple->{'forward'});
	}
$userconfig{'forwardto'} = $in{'forwardto'};
$in{'autotext'} =~ s/\r//g;
if ($in{'autotext'}) {
	$simple->{'autotext'} = $in{'autotext'};
	if (!$simple->{'from'}) {
		($froms, $doms) = &mailbox::list_from_addresses();
		$simple->{'from'} = $froms->[0];
		}
	if ($in{'period_def'}) {
		delete($simple->{'replies'});
		delete($simple->{'period'});
		}
	else {
		$in{'period'} =~ /^\d+$/ || &error($text{'simple_eperiod'});
		$simple->{'period'} = $in{'period'}*60;
		$simple->{'replies'} ||=
			"$user_module_config_directory/replies";
		}
	if ($in{'from_def'}) {
		delete($simple->{'from'});
		}
	else {
		$in{'from'} =~ /\S/ || &error($text{'simple_efrom'});
		$simple->{'from'} = $in{'from'};
		}
	}
if ($in{'auto'}) {
	$in{'autotext'} =~ /\S/ || &error($text{'simple_eautotext'});
	}
$simple->{'auto'} = $in{'auto'};

# Save attached files
if ($config{'attach'}) {
	$simple->{'autoreply_file'} = [ ];
	for($i=0; defined($f = $in{"file_$i"}); $i++) {
		next if (!$f);
		if ($f !~ /^\//) {
			$f = "$remote_user_info[7]/$f";
			}
		-r $f || &error(&text('simple_efile', $f));
		$in{'autotext'} || &error($text{'simple_eautotextfile'});
		push(@{$simple->{'autoreply_file'}}, $f);
		}
	}

# Save settings
&save_simple($simple);
&save_user_module_config();
&redirect("index.cgi?simple=1");

