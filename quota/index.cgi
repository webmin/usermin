#!/usr/local/bin/perl
# index.cgi
# Just display the current user's quotas

require './quota-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

@st = stat($remote_user_info[7]);	# force mount of home dir
$n = &user_filesystems($remote_user);
if ($n) {
	print &ui_subheading(&text('index_quotas', "<tt>$remote_user</tt>"));
	&quotas_table();
	}
else {
	print "<p><b>$text{'index_none'}</b><p>\n";
	}

if (&quotas_supported() >= 2) {
	foreach $gid ($remote_user_info[3], &other_groups($remote_user)) {
		($g = getgrgid($gid)) || next;
		$n = &group_filesystems($g);
		if ($n > 0) {
			print &ui_subheading(&text('index_gquotas', "<tt>$g</tt>"));
			&quotas_table();
			}
		}
	}

&ui_print_footer("/", $text{'index'});

sub quotas_table
{
print "<table border width=100%>\n";
print "<tr $tb> <td><br></td>\n";
$cols = 3 + ($config{'show_grace'} ? 1 : 0);
print "<td colspan=$cols align=center><b>$text{'ufilesys_blocks'}</b></td>\n";
print "<td colspan=$cols align=center><b>$text{'ufilesys_files'}</b></td> </tr>\n";
print "<tr $tb> <td><b>$text{'ufilesys_fs'}</b></td>\n";
print "<td><b>$text{'ufilesys_used'}</b></td> <td><b>$text{'ufilesys_soft'}</b></td>\n";
print "<td><b>$text{'ufilesys_hard'}</b></td>\n";
print "<td><b>$text{'ufilesys_grace'}</b></td>\n"
	if ($config{'show_grace'});
print "<td><b>$text{'ufilesys_used'}</b></td> <td><b>$text{'ufilesys_soft'}</b></td>\n";
print "<td><b>$text{'ufilesys_hard'}</b></td>\n";
print "<td><b>$text{'ufilesys_grace'}</b></td>\n"
	if ($config{'show_grace'});
print "</tr>\n";
for($i=0; $i<$n; $i++) {
	$f = $filesys{$i,'filesys'};
	$bsize = $config{'block_size'};
	print "<tr $cb>\n";
	print "<td>$f</td>\n";
	if ($bsize) {
		print "<td>",&nice_size($filesys{$i,'ublocks'}*$bsize),"</td>\n";
		}
	else {
		print "<td>$filesys{$i,'ublocks'}</td>\n";
		}
	&print_limit($filesys{$i,'sblocks'});
	&print_limit($filesys{$i,'hblocks'});
	&print_grace($filesys{$i,'gblocks'}) if ($config{'show_grace'});
	print "<td>$filesys{$i,'ufiles'}</td>\n";
	&print_limit($filesys{$i,'sfiles'});
	&print_limit($filesys{$i,'hfiles'});
	&print_grace($filesys{$i,'gfiles'}) if ($config{'show_grace'});
	print "</tr>\n";
        if ($filesys{$i,'sblocks'} or $filesys{$i,'hblocks'} or $filesys{$i,'sfiles'} or $filesys{$i,'hfiles'}) {
		my ($b,$bmax);
		print "<tr $cb><td>&nbsp;</td>";
		my $cols = $config{'show_grace'} ? 4 : 3;
		if ($bmax = ($filesys{$i,'hblocks'} or $filesys{$i,'sblocks'})) {
			$b = int(($filesys{$i,'ublocks'}/$bmax*100)+0.5);
			print "<td align=left colspan=$cols><table width=\"$b%\"><tr><td bgcolor=#66ff66>&nbsp;</td></tr></table></td>";
			}
		else {
			print "<td colspan=$cols>&nbsp;</td>";
			}
		if ($bmax = ($filesys{$i,'hfiles'} or $filesys{$i,'sfiles'})) {
			$b = int(($filesys{$i,'ufiles'}/$bmax*100)+0.5);
			print "<td align=left colspan=$cols><table width=\"$b%\"><tr><td bgcolor=#66ff66>&nbsp;</td></tr></table></td>";
			}
		else {
			print "<td colspan=$cols>&nbsp;</td>";
			}
		print "</tr>\n";
		}
	}
print "</table><br>\n";
}
