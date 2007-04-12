#!/usr/local/bin/perl
# save_address.cgi
# Save, add or delete an address book entry

require './mailbox-lib.pl';
&ReadParse();

if ($in{'delete'} ne '') {
	&delete_address($in{'delete'});
	}
else {
	&error_setup($text{'address_err'});
	$in{'addr'} =~ /^\S+\@\S+$/ || &error($text{'address_eaddr'});
	$in{'addr'} =~ /[,<>"'\(\)]/ && &error($text{'address_eaddr'});
	if ($in{'from'} == 2) {
		# Turn off default for all others
		foreach $a (&list_addresses()) {
			if ($a->[3] == 2 && $a->[2] != $in{'edit'}) {
				&modify_address($a->[2], $a->[0],
						$a->[1], 1);
				}
			}
		}
	if ($in{'add'}) {
		&create_address($in{'addr'}, $in{'name'}, $in{'from'});
		}
	else {
		&modify_address($in{'edit'}, $in{'addr'}, $in{'name'}, $in{'from'});
		}
	}
&redirect("list_addresses.cgi");


