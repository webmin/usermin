#!/usr/local/bin/perl
# uconfig.cgi
# Like config.cgi, but works on a user's personal config file

require './web-lib.pl';
require './config-lib.pl';
require './ui-lib.pl';
$m = $ARGV[0];
&init_config();
require './ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();

%module_info = &get_module_info($m);
$desc = &text('config_dir', $module_info{'desc'});
&ui_print_header($desc, $text{'config_title'}, "", undef, 0, 1);

print &ui_form_start("uconfig_save.cgi", "post");
print &ui_hidden("module", $m);
print &ui_table_start(&text('config_header', $module_info{'desc'}),
		      "width=100%", 2);
&read_file("$m/defaultuconfig", \%config);
&read_file("$config_directory/$m/uconfig", \%config);
&read_file("$user_config_directory/$m/config", \%config);
&read_file("$config_directory/$m/canconfig", \%canconfig);

if (-r "$m/uconfig_info.pl") {
	# Module has a custom config editor
	&foreign_require($m, "uconfig_info.pl");
	&foreign_call($m, "config_form", \%config, \%canconfig);
	}
else {
	# Use config.info to create config inputs
	&generate_config(\%config, "$m/uconfig.info", undef,
			 %canconfig ? \%canconfig : undef);
	}
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&footer("/$m", $text{'index'});

