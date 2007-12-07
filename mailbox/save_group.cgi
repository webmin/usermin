#!/usr/local/bin/perl
# save_group.cgi
# Save, add or delete an address group entry

require './mailbox-lib.pl';
&ReadParse();

if ($in{'gdelete'} ne '') {
	&delete_address_group($in{'gdelete'});
	}
else {
	&error_setup($text{'group_err'});
	$in{'group'} =~ /\S/ || &error($text{'group_egroup'});
	$in{'members'} =~ /\S/ || &error($text{'group_emembers'});
	if ($in{'gadd'}) {
		&create_address_group($in{'group'}, $in{'members'});
		}
	else {
		&modify_address_group($in{'gedit'}, $in{'group'}, $in{'members'});
		}
	}
&redirect("list_addresses.cgi?mode=groups");


