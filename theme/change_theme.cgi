#!/usr/local/bin/perl
# change_theme.cgi
# Change the theme for the current user

require './theme-lib.pl';
&ReadParse();

&get_miniserv_config(\%miniserv);
if ($in{'theme'} eq 'none') {
	delete($gconfig{'theme_'.$remote_user});
	delete($miniserv{'preroot_'.$remote_user});
	}
else {
	$gconfig{'theme_'.$remote_user} = $in{'theme'};
	$miniserv{'preroot_'.$remote_user} = $in{'theme'};
	}
&put_miniserv_config(\%miniserv);
&write_file("$config_directory/config", \%gconfig);
&restart_miniserv();

&redirect("/");

