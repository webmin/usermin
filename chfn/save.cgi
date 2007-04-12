#!/usr/local/bin/perl
# save.cgi
# Change the user's details and shell

require './chfn-lib.pl';
&ReadParse();
&error_setup($text{'save_err'});

# Force current values for those that can't be changed
@remote_user_info = getpwnam($remote_user);
@uinfo = split(/,/, $remote_user_info[6]);
$in{'real'} = $uinfo[0] if (!$config{'change_real'});
$in{'office'} = $uinfo[1] if (!$config{'change_office'});
$in{'ophone'} = $uinfo[2] if (!$config{'change_ophone'});
$in{'hphone'} = $uinfo[3] if (!$config{'change_hphone'});
$in{'shell'} = $remote_user_info[8] if (!$config{'change_shell'});

# Make sure values are set
$in{'shell'} =~ /\S/ || &error($text{'save_eshell2'});
$in{'real'} =~ /\S/ || &error($text{'save_ereal2'});

# Validate inputs
$in{'real'} =~ /[,:]/ && &error($text{'save_ereal'});
$in{'office'} =~ /[,:]/ && &error($text{'save_eoffice'});
$in{'ophone'} =~ /[,:]/ && &error($text{'save_eophone'});
$in{'hphone'} =~ /[,:]/ && &error($text{'save_ehphone'});
$in{'shell'} =~ /[,:]/ && &error($text{'save_eshell'});

# Change the details and shell
$err = &change_details($in{'real'}, $in{'office'}, $in{'ophone'}, $in{'hphone'},
		       $in{'shell'});
$err && &error("<tt>$err</tt>");

&ui_print_header(undef, $text{'save_title'}, "");

print &text($config{'change_shell'} ? 'save_desc' : 'save_desc2',
		  "<tt>$remote_user</tt>"),"<p>\n";

&ui_print_footer("/", $text{'index'});

