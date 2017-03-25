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
	print "<b>$text{'index_none'}</b><p>\n";
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
# Generate top header (showing blocks/files)
$bsize = $config{'block_size'};
@hcols = ( undef,
	   $bsize ? $text{'ufilesys_space'} : $text{'ufilesys_blocks'},
	   $config{'show_grace'} ? ( undef ) : ( ),
	   $text{'ufilesys_files'},
	   $config{'show_grace'} ? ( undef ) : ( ) );
print &ui_columns_start(\@hcols, 100, 0,
                [ undef, "colspan=3 align=center", "colspan=3 align=center" ]);

# Generate second header
@hcols = ( $text{'ufilesys_fs'}, $text{'ufilesys_used'},
	   $text{'ufilesys_soft'}, $text{'ufilesys_hard'},
	   $config{'show_grace'} ? ( $text{'ufilesys_grace'} ) : ( ),
	   $text{'ufilesys_used'},
	   $text{'ufilesys_soft'}, $text{'ufilesys_hard'},
	   $config{'show_grace'} ? ( $text{'ufilesys_grace'} ) : ( ),
	 );
print &ui_columns_header(\@hcols);

# Generate one row per filesystem the user has quota on
for($i=0; $i<$n; $i++) {
	$f = $filesys{$i,'filesys'};
	local @cols;
	push(@cols, $f);
	if ($bsize) {
		push(@cols, &nice_size($filesys{$i,'ublocks'}*$bsize));
		}
	else {
		push(@cols, $filesys{$i,'ublocks'});
		}
	push(@cols, &nice_limit($filesys{$i,'sblocks'}, $bsize));
	push(@cols, &nice_limit($filesys{$i,'hblocks'}, $bsize));
	push(@cols, $filesys{$i,'gblocks'}) if ($config{'show_grace'});
	push(@cols, $filesys{$i,'ufiles'});
	push(@cols, &nice_limit($filesys{$i,'sfiles'}, $bsize, 1));
	push(@cols, &nice_limit($filesys{$i,'hfiles'}, $bsize, 1));
	push(@cols, $filesys{$i,'gfiles'}) if ($config{'show_grace'});
	print &ui_columns_row(\@cols);
	}
print &ui_columns_end();
}
