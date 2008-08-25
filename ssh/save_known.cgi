#!/usr/local/bin/perl
# save_known.cgi
# Save, create or delete a known host

require './ssh-lib.pl';
&ReadParse();
@knowns = &list_knowns();
$known = $knowns[$in{'idx'}] if (!$in{'new'});

if ($in{'delete'}) {
	# Just delete this known host key
	&delete_known($known);
	}
else {
	# Validate inputs
	&error_setup($text{'known_err'});
	if ($in{'hosts'}) {
		$in{'hosts'} =~ /\S/ || &error($text{'known_ehosts'});
		$known->{'hosts'} = [ split(/\s+/, $in{'hosts'}) ];
		}
		if ($in{type} eq 'ssh-rsa1') {
		$in{'bits'} =~ /^\d+$/ || &error($text{'auth_ebits'});
		$known->{'bits'} = $in{'bits'};
		$in{'exp'} =~ /^\d+$/ || &error($text{'auth_eexp'});
		$known->{'exp'} = $in{'exp'};
		$in{'key'} =~ s/\r|\n//g;
		$in{'key'} =~ /^\d+$/ || &error($text{'auth_ekey'});
		}
	else {
		$known->{'type'} = $in{'type'};
		$in{'key'} =~ s/\r|\n//g;
		$in{'key'} =~ /^\S+$/ || &error($text{'auth_ekey'});
		}
	$known->{'key'} = $in{'key'};
	$known->{'comment'} = $in{'comment'};

	# Create or save the known host
	if ($in{'new'}) {
		&create_known($known);
		}
	else {
		&modify_known($known);
		}
	}
&redirect("list_knowns.cgi");

