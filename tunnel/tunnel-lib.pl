# tunnel-lib.pl
# Common functions for the HTTP-tunnel module

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
&switch_to_remote_user();
&create_user_config_dirs();

1;

