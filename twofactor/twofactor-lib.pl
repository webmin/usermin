
BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
require 'twofactor-funcs-lib.pl';

1;

