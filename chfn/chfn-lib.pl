# chfn-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
if ($gconfig{'os_type'} =~ /-linux$/) {
	do "linux-lib.pl";
	}
else {
	do "$gconfig{'os_type'}-lib.pl";
	}

1;

