#!/usr/local/bin/perl
# change_theme.cgi
# Change the theme for the current user

require './theme-lib.pl';
&ReadParse();
&ui_print_unbuffered_header(undef, $text{'change_title'}, "");

print "$text{'change_user'}<br>\n";
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
print "$text{'change_done'}<p>\n";

print "$text{'change_restart'}<br>\n";
&reload_miniserv();
print "$text{'change_done'}<p>\n";

if (defined(&theme_post_change_theme)) {
	&theme_post_change_theme();
	}
print "$text{'change_redirect'}<br>\n";
print &js_redirect("/", "top");
print "$text{'change_done'}<p>\n";

&ui_print_footer("/", $text{'index'});

