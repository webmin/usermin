
use strict;
use warnings;
require 'quota-lib.pl';
our (%text, %config, $remote_user, %filesys);

# list_system_info()
# Return some basic info about the system
sub list_system_info
{
my $n = &quota::user_filesystems($remote_user);
if ($n > 0) {
	my @chart;
	my $chart = { 'type' => 'chart',
		      'desc' => $text{'right_header'},
		      'chart' => \@chart };
	for(my $i=0; $i<$n; $i++) {
		my $quota = $filesys{$i,'hblocks'} ||
			    $filesys{$i,'sblocks'};
		next if (!$quota);
		my $usage = $filesys{$i,'ublocks'};
		my $bsize = $config{'block_size'};
		push(@chart, { 'desc' => $filesys{$i,'filesys'},
			       'chart' => [ $quota, $usage ],
			       'value' => &text('right_out',
					&nice_size($usage*$bsize),
					&nice_size($quota*$bsize)), });
		}
	return @chart ? ( $chart ) : ( );
	}
return ( );
}

1;
