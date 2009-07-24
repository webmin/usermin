# todolist-lib.pl
# Common functions for managing a TODO list
#
# Ideas
#  - Simple list of tasks, each with name, status (new, started, done), date
#  - Each task can have a text box and attachments
#  - Tasks can have project, importance too
#  - View mode to show different statuses
#  - Sorting modes
#  - Option in email module to create TODO task from mail
#  - Can have shared tasks (common directory), assigned to people

do '../web-lib.pl';
&init_config();
&switch_to_remote_user();
&create_user_config_dirs();

$user_todo_directory = "$user_module_config_directory/todo";
$global_todo_directory = $config{'global_todo'};

# list_todos()
# Returns a list of all tasks
sub list_todos
{
local $d;
foreach $d ($user_todo_directory, $global_todo_directory) {
	next if (!$d);
	local $f;
	opendir(DIR, $d);
	foreach $f (readdir(DIR)) {
		next if ($f !~ /^(\S+)\.todo$/);
		local $todo = { 'id' => $1 };

		# XXX separate dir for attachments, and function to get
		}
	closedir(DIR);
	}
}

1;

