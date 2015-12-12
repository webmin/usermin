
# acl_security_form(&options)
# Output HTML for editing global security options
sub acl_security_form
{
my ($o) = @_;

# Root directory for file browser
print &ui_table_row($text{'acl_root'},
	&ui_opt_textbox("root", $o->{'root'}, 40, $text{'acl_home'})." ".
	&file_chooser_button("root", 1), 3);

# Can see dot files?
print &ui_table_row($text{'acl_nodot'},
	&ui_yesno_radio("nodot", int($o->{'nodot'})));

# Users visible in chooser
print &ui_table_row($text{'acl_uedit'},
  &ui_radio_table("uedit_mode", int($o->{'uedit_mode'}),
	[ [ 0, $text{'acl_uedit_all'} ],
	  [ 1, $text{'acl_uedit_none'} ],
	  [ 2, $text{'acl_uedit_only'},
	       &ui_textbox("uedit_can",
			   $o->{'uedit_mode'} == 2 ? $o->{'uedit'} : "", 40).
	       " ".&user_chooser_button("uedit_can", 1) ],
	  [ 3, $text{'acl_uedit_except'},
	       &ui_textbox("uedit_cannot",
			   $o->{'uedit_mode'} == 3 ? $o->{'uedit'} : "", 40).
	       " ".&user_chooser_button("uedit_cannot", 1) ],
	  [ 4, $text{'acl_uedit_uid'},
	       &ui_textbox("uedit_uid",
			   $o->{'uedit_mode'} == 4 ? $o->{'uedit'} : "", 6).
	       " - ".
	       &ui_textbox("uedit_uid2",
			   $o->{'uedit_mode'} == 4 ? $o->{'uedit2'} : "", 6) ],
	  [ 5, $text{'acl_uedit_group'},
	       &ui_group_textbox("uedit_group",
		$o->{'uedit_mode'} == 5 ? $dummy=getgrgid($o->{'uedit'}) : "")],
	]), 3);

# Groups visible in chooser
print &ui_table_row($text{'acl_gedit'},
    &ui_radio_table("gedit_mode", int($o->{'gedit_mode'}),
	[ [ 0, $text{'acl_gedit_all'} ],
	  [ 1, $text{'acl_gedit_none'} ],
	  [ 2, $text{'acl_gedit_only'},
	       &ui_textbox("gedit_can",
			   $o->{'gedit_mode'} == 2 ? $o->{'gedit'} : "", 40).
	       " ".&group_chooser_button("gedit_can", 1) ],
	  [ 3, $text{'acl_gedit_except'},
	       &ui_textbox("gedit_cannot",
			   $o->{'gedit_mode'} == 3 ? $o->{'gedit'} : "", 40).
	       " ".&group_chooser_button("gedit_cannot", 1) ],
	  [ 4, $text{'acl_gedit_gid'},
	       &ui_textbox("gedit_gid",
			   $o->{'gedit_mode'} == 4 ? $o->{'gedit'} : "", 6).
	       " - ".
	       &ui_textbox("gedit_gid2",
			   $o->{'gedit_mode'} == 4 ? $o->{'gedit2'} : "", 6) ],
	]), 3);
}

# acl_security_save(&options)
# Parse the form for global security options
sub acl_security_save
{
$_[0]->{'root'} = $in{'root_def'} ? undef : $in{'root'};
$_[0]->{'nodot'} = $in{'nodot'};

$_[0]->{'uedit_mode'} = $in{'uedit_mode'};
$_[0]->{'uedit'} = $in{'uedit_mode'} == 2 ? $in{'uedit_can'} :
		   $in{'uedit_mode'} == 3 ? $in{'uedit_cannot'} :
		   $in{'uedit_mode'} == 4 ? $in{'uedit_uid'} :
		   $in{'uedit_mode'} == 5 ? getgrnam($in{'uedit_group'}) : "";
$_[0]->{'uedit2'} = $in{'uedit_mode'} == 4 ? $in{'uedit_uid2'} : undef;

$_[0]->{'gedit_mode'} = $in{'gedit_mode'};
$_[0]->{'gedit'} = $in{'gedit_mode'} == 2 ? $in{'gedit_can'} :
		   $in{'gedit_mode'} == 3 ? $in{'gedit_cannot'} :
		   $in{'gedit_mode'} == 4 ? $in{'gedit_gid'} : "";
$_[0]->{'gedit2'} = $in{'gedit_mode'} == 4 ? $in{'gedit_gid2'} : undef;
}

