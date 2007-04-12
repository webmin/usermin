# vacation-lib.pl

use File::Copy;

do '../web-lib.pl';
&init_config(); 
&switch_to_remote_user();

$vacation_file = "$remote_user_info[7]/.vacation.msg";
$vacation_db = "$remote_user_info[7]/.vacation.db";
$forward_file = "$remote_user_info[7]/.forward";
$forward_save_file = "$remote_user_info[7]/.forward.vacation.bak";
$vacation_active = &check_vacation_active;
%mailbox_cfg = &foreign_config('mailbox');

# get_from - checks mailbox module configuration to
#  determine user's appropriate From: address.
#  returns a scalar containing the user's from address.
sub get_from {

	local $http_host = $ENV{'HTTP_HOST'};
	$http_host =~ s/:\d+$//;
	$http_host =~ s/^(www|ftp|mail)\.//;

	$hostname = $mailbox_cfg{'server_name'} eq '*' ? $http_host :
		$mailbox_cfg{'server_name'} eq '' ? &get_system_hostname() :
		$mailbox_cfg{'server_name'};

	$from = $remote_user.'@'.$hostname;
	if ($mailbox_cfg{'from_map'}) {
		open(MAP, $mailbox_cfg{'from_map'});
		while(<MAP>) {
			s/\r|\n//g;
			s/#.*$//;
			if (/^\s*(\S+)\s+(\S+)/ && $from eq $1) {
				$from = $2;
				last;
				}
		}
		close(MAP);
	}
	$remote_user_info[6] =~ s/,.*$//;
	$from = "\"$remote_user_info[6]\" <$from>" if ($remote_user_info[6]);
	return $from;
}


# check_vacation_active - determines if vacation is currently active
#  returns 1 if yes, 0 if no.
sub check_vacation_active {

	$active=0;
	open (FORWARD, "$forward_file");
	while (<FORWARD>) {
		$active = 1 if (m/^[^#].*$config{'vacation_path'}/);
	}
	close (FORWARD);
	return $active;
}


# start_vacation - enables vacation by appending a line to their .forward
# to call vacation. Also makes the system call to vacation to init $vacation_db
sub start_vacation {

	if (-e $forward_file) {
		#backup existing .forward file and add vacation pipe.
		copy("$forward_file","$forward_save_file");
		open(FORWARD, ">>$forward_file");
		print FORWARD "\"|$config{'vacation_path'} $remote_user\"";
		close(FORWARD);
	} else {
		open(FORWARD, ">$forward_file");
		print FORWARD "\\$remote_user\n";
		print FORWARD "\"|$config{'vacation_path'} $remote_user\"";
		close(FORWARD);
	}
	# Now make the system call to vacation to init .vacation.db
	system("$config{'vacation_path'} -I");
}


# stop_vacation - if $forward_save_file exists, restore it; otherwise
# remove .forward file. Also, delete $vacation_db
sub stop_vacation {

	if (-e $forward_save_file) {
		copy("$forward_save_file","$forward_file");
		unlink($forward_save_file);
	} else {
		unlink($forward_file);
	}
	unlink($vacation_db);

}


1;

