# plan-lib.pl

do '../web-lib.pl';
&init_config(); 
require '../ui-lib.pl';
&switch_to_remote_user();

$plan_file = "$remote_user_info[7]/.plan";

1;

