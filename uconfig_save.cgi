#!/usr/local/bin/perl
# config_save.cgi
# Save inputs from config.cgi

require './web-lib.pl';
require './config-lib.pl';
&init_config();
&switch_to_remote_user();
&create_user_config_dirs();

&ReadParse();
$m = $in{'module'};
&read_acl(\%acl);
&error_setup($text{'config_err'});
%module_info = &get_module_info($m);
%module_info || &error($text{'config_emodule'});
$acl{$base_remote_user,$m} || &error($text{'config_eaccess'});
$mdir = &module_root_directory($m);

mkdir("$user_config_directory/$m", 0700);
&lock_file("$user_config_directory/$m/config");
&read_file("$user_config_directory/$m/config", \%config);
&read_file("$config_directory/$m/canconfig", \%canconfig);
%oldconfig = %config;

if (-r "$mdir/uconfig_info.pl") {
	# Module has a custom config editor
	&foreign_require($m, "uconfig_info.pl");
	local $fn = "${m}::config_form";
	if (defined(&$fn)) {
		local $pkg = $m;
		$pkg =~ s/[^A-Za-z0-9]/_/g;
		eval "\%${pkg}::in = \%in";
		$func++;
		&foreign_call($m, "config_save", \%config, \%canconfig);
		}
	}
if (!$func) {
	# Use config.info to parse config inputs
	&parse_config(\%config, "$mdir/uconfig.info", undef,
		      %canconfig ? \%canconfig : undef);
	}
&write_file("$user_config_directory/$m/config", \%config, undef, 1);
&unlock_file("$user_config_directory/$m/config");

# Call any post-config save function
local $pfn = "${m}::config_post_save";
if (defined(&$pfn)) {
	&foreign_call($m, "config_post_save", \%config, \%oldconfig,
					      \%canconfig);
	}

&redirect("/$m/");

