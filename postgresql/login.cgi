#!/usr/local/bin/perl
# login.cgi
# Save PostgreSQL login and password

require './postgresql-lib.pl';
&ReadParse();
&error_setup($text{'login_err'});
$in{'login'} || &error($text{'login_elogin'});
$postgres_login = $userconfig{'login'} = $in{'login'};
$postgres_pass = $userconfig{'pass'} = $in{'pass'};
if (&is_postgresql_running() == -1) {
	&error($text{'login_epass'});
	}
&write_file("$user_module_config_directory/config", \%userconfig);
&redirect("");

