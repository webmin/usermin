# tunnel-lib.pl
# Common functions for the HTTP-tunnel module

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();

1;

