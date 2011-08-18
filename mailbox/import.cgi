#!/usr/local/bin/perl
# Import addresses from a file

require './mailbox-lib.pl';
&ReadParseMime();
&error_setup($text{'import_err'});

# Get the data to import
if ($in{'src'} == 0) {
	$in{'upload'} || &error($text{'import_eupload'});
	$data = $in{'upload'};
	}
else {
	$in{'paste'} =~ s/\r//g;
	$in{'paste'} =~ /\S/ || &error($text{'import_epaste'});
	$data = $in{'paste'};
	}

# Parse the data
if ($in{'fmt'} eq 'csv') {
	# CSV or tab-separated format
	foreach $l (split(/\n/, $data)) {
		next if ($l !~ /\S/);
		@row = ( );
		while($l =~ s/^\s*"([^"]*)",?(.*)/$2/ ||
		      $l =~ s/^\s*'([^']*)',?(.*)/$2/ ||
		      $l =~ s/^\s*"([^"]*)"\t?(.*)/$2/ ||
		      $l =~ s/^\s*'([^']*)'\t?(.*)/$2/ ||
		      $l =~ s/^\s*([^,]+),?(.*)/$2/ ||
		      $l =~ s/^\s*([^\t]+)\t?(.*)/$2/) {
			push(@row, $1);
			}
		push(@addrs, [ $row[0], $row[1], int($row[2]) ]);
		}
	}
else {
	# Vcard
	eval "use Net::vCard";
	$@ && &error($text{'import_enetvcard'});
	$temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $data;
	close(TEMP);
	$cards = Net::vCard->loadFile($temp);
	&unlink_file($temp);
	foreach $card (@$cards) {
		my $n = $card->givenName;
		$n .= " " if ($n);
		$n .= $card->familyName;
		next if (!$n);
		push(@addrs, [ $card->{'EMAIL'}->{'internet'}, $n, 0 ]);
		}
	}
@addrs || &error($text{'import_enone'});

# Update addresses, and tell user
&ui_print_header(undef, $text{'import_title'}, "");

print $text{'import_doing'},"<p>\n";

%old = map { lc($_->[0]), $_ } &list_addresses();
print &ui_columns_start([ $text{'address_addr'}, $text{'address_name'},
			  $text{'import_action'} ], 100);
foreach $a (@addrs) {
	$o = $old{lc($a->[0])};
	$a->[0] =~ s/^\s+//; $a->[0] =~ s/\s+$//;
	$a->[1] =~ s/^\s+//; $a->[1] =~ s/\s+$//;
	if ($a->[0] !~ /^\S+\@\S+$/) {
		# Invalid email
		print &ui_columns_row([ &html_escape($a->[0]),
					&html_escape($a->[1]),
					$text{'import_noemail'} ]);
		}
	elsif (!$o) {
		# Missing, need to add
		print &ui_columns_row([ &html_escape($a->[0]),
					&html_escape($a->[1]),
					$text{'import_add'} ]);
		&create_address($a->[0], $a->[1], $a->[2]);
		}
	elsif ($in{'dup'}) {
		if ($o->[1] ne $a->[1] && $o->[2] ne '') {
			# Exists but is different .. update
			print &ui_columns_row([ &html_escape($a->[0]),
						&html_escape($a->[1]),
						$text{'import_update'} ]);
			&modify_address($o->[2], $a->[0], $a->[1], $a->[2]);
			}
		elsif ($o->[1] ne $a->[1] && $o->[2] eq '') {
			# Exists but cannot be updated
			print &ui_columns_row([ &html_escape($a->[0]),
						&html_escape($a->[1]),
						$text{'import_readonly'} ]);
			}
		else {
			# Exists and is same
			print &ui_columns_row([ &html_escape($a->[0]),
						&html_escape($a->[1]),
						$text{'import_same'} ]);
			}
		}
	else {
		# Exists, skip
		print &ui_columns_row([ &html_escape($a->[0]),
					&html_escape($a->[1]),
					$text{'import_skip'} ]);
		}
	}
print &ui_columns_end();

&ui_print_footer("list_addresses.cgi", $text{'address_return'});

