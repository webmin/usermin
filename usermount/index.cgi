#!/usr/local/bin/perl
# index.cgi
# Display a table of all filesystems that can be mounted/unmounted by
# a user, due to having the user flag set

require './usermount-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

@mounts = &list_mounts();
foreach $m (@mounts) {
	local %options;
	&parse_options($m->[2], $m->[3]);
	if (defined($options{'user'})) {
		push(@usermounts, $m);
		}
	}
foreach $m (&list_mounted()) {
	$mounted{$m->[0],$m->[1]}++;
	}
if (@usermounts) {
	print "<form action=mount.cgi>\n";
	@tds = ( "width=25%", "width=25%", "width=25%", "width=10%",
		 "width=15% nowrap" );
	print &ui_columns_start([ $text{'index_dir'},
				  $text{'index_type'},
				  $text{'index_dev'},
				  $text{'index_status'},
				  $text{'index_action'} ], 100, 0, \@tds);
	foreach $u (@usermounts) {
		local @cols;
		push(@cols, $u->[0]);
		local $fsn = &fstype_name($u->[2]);
		push(@cols, $u->[2] eq "*" ? $text{'index_auto'}
					   : $fsn);
		push(@cols, &device_name($u->[1]));
		if ($mounted{$u->[0],$u->[1]}) {
			# Mounted, show button to un-mount
			push(@cols, $text{'yes'});
			push(@cols, &ui_submit($text{'index_umount'},
					       "umount_$u->[0]"));
			}
		else {
			# Not mounted
			push(@cols, $text{'no'});
			if ($u->[3] =~ /encryption/) {
				# Assume a password is needed
				push(@cols, &ui_submit($text{'index_mount2'},
						       "mount_$u->[0]")." ".
					    &ui_textbox("pass_$u->[0]",
							undef, 15));
				}
			else {
				push(@cols, &ui_submit($text{'index_mount'},
						       "mount_$u->[0]"));
				}
			}
		print &ui_columns_row(\@cols);
		}
	print &ui_columns_end();
	print "</form>\n";
	}
else {
	print "<b>$text{'index_none'}</b><p>\n";
	}

&ui_print_footer("/", $text{'index'});

