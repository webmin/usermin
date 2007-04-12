# chfn-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
if ($gconfig{'os_type'} =~ /-linux$/) {
	do "linux-lib.pl";
	}
else {
	do "$gconfig{'os_type'}-lib.pl";
	}

1;

