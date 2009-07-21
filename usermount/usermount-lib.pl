# usermount-lib.pl
# Common functions for mounting and unmounting filesystems with the 'user'
# option set.

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
&switch_to_remote_user();
do 'linux-lib.pl';

# parse_options(type, options)
# Convert an options string for some filesystem into the associative
# array %options
sub parse_options
{
local($_);
undef(%options);
if ($_[1] ne "-") {
        foreach (split(/,/, $_[1])) {
                if (/^([^=]+)=(.*)$/) { $options{$1} = $2; }
                else { $options{$_} = ""; }
                }
        }
}

1;

