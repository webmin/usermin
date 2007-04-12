#!/usr/local/bin/perl
# Show form for editing vacation command options

require './forward-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'vacation_title'}, "");

if ($config{'mail_system'} == 0) {
	@aliases = &list_aliases();
	$a = $aliases[$in{'num'}];
	}
else {
	$a = &get_dotqmail($in{'file'});
	}
$dst = $a->{'values'}->[$in{'idx'}];
($type, $args) = &alias_type($dst);
$type == 8 || &error("Not a vacation alias!");

# Parse command-line args
@args = split(/\s+/, $args);
$user = pop(@args);
while(@args) {
	$arg = shift(@args);
	if ($arg eq "-m") {
		$msg = shift(@args);
		}
	elsif ($arg eq "-a") {
		$alias = shift(@args);
		push(@als, $alias);
		}
	elsif ($arg eq "-r") {
		$interval = shift(@args);
		}
	else {
		push(@unknown, $arg);
		}
	}

print &ui_form_start("save_vacation.cgi", "post");
print &ui_table_start($text{'vacation_header'}, undef, 2);
print &ui_hidden("file", $in{'file'});
print &ui_hidden("num", $in{'num'});
print &ui_hidden("idx", $in{'idx'});
foreach $u (@unknown) {
	print &ui_hidden("unknown", $u);
	}

# Username for this user
print &ui_table_row($text{'vacation_user'},
		    &ui_radio("user_def", $user eq $remote_user ? 1 : 0,
			      [ [ 1, $text{'default'} ],
				[ 0, $text{'vacation_usersel'} ] ])."\n".
		    &ui_textbox("user", $user eq $remote_user ? undef : $user,
				20));

# Extra aliases
print &ui_table_row($text{'vacation_aliases'},
		    &ui_textarea("aliases", join("\n", @als), 5, 30));

# Message file
$defmsg = ".vacation.msg";
print &ui_table_row($text{'vacation_msg'},
		    &ui_radio("msg_def", $msg ? 0 : 1,
			      [ [ 1, $text{'default'}." (<tt>$defmsg</tt>)" ],
				[ 0, " " ] ])."\n".
		    &ui_textbox("msg", $msg, 30)." ".
		    "<a href='edit_vfile.cgi?vfile=".
		    &urlize($msg || $defmsg)."&num=$a->{'num'}&".
		    "file=$in{'file'}&idx=$in{'idx'}'>".
		    "$text{'aform_afile'}</a>\n");

# Autoreply interval
print &ui_table_row($text{'vacation_interval'},
		    &ui_radio("interval_def", $interval ? 0 : 1,
			      [ [ 1, $text{'default'} ],
				[ 0, " " ] ])."\n".
		    &ui_textbox("interval", $interval, 5)." ".
			        $text{'vacation_days'});

print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("edit_alias.cgi?num=$in{'num'}file=$in{'file'}",
		 $text{'aform_return'});

