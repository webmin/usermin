# plan-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config(); 
&switch_to_remote_user();

$plan_file = "$remote_user_info[7]/.plan";

1;

