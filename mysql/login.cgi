#!/usr/local/bin/perl
# login.cgi
# Save MySQL login and password

require './mysql-lib.pl';
&ReadParse();
&error_setup($text{'login_err'});
$in{'login'} || &error($text{'login_elogin'});
$mysql_login = $userconfig{'login'} = $in{'login'};
$mysql_pass = $userconfig{'pass'} = $in{'pass'};
$authstr = &make_authstr();
if (&is_mysql_running() == -1) {
	&error($text{'login_epass'});
	}
&write_file("$user_module_config_directory/config", \%userconfig);
chmod(0700, "$user_module_config_directory/config");
&redirect("");

