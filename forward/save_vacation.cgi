#!/usr/local/bin/perl
# Update a vacation alias command

require './forward-lib.pl';
&ReadParse();
&error_setup($text{'vacation_err'});

# Validate and parse args
$args = "";
$in{'aliases'} =~ s/\r//g;
foreach $a (split(/\n+/, $in{'aliases'})) {
	$a =~ /^\S+$/ || &error(&text('vacation_ealias', $a));
	$args .= " -a $a";
	}
if (!$in{'interval_def'}) {
	$in{'interval'} =~ /^\d+$/ || &error($text{'vacation_einterval'});
	$args .= " -r $in{'interval'}";
	}
if (!$in{'msg_def'}) {
	$in{'msg'} =~ /^\S+$/ || &error($text{'vacation_emsg'});
	$args .= " -m $in{'msg'}";
	}
foreach $u (split(/\0/, $in{'unknown'})) {
	$args .= " $u";
	}
if ($in{'user_def'}) {
	$args .= " $remote_user";
	}
else {
	$in{'user'} =~ /^\S+$/ || &error($text{'vacation_euser'});
	$args .= " $in{'user'}";
	}

# Update actual alias
if ($config{'mail_system'} == 0) {
	@aliases = &list_aliases();
	$a = $aliases[$in{'num'}];
	}
else {
	$a = &get_dotqmail($in{'file'});
	}
$a->{'values'}->[$in{'idx'}] = "|$vacation_path$args";
&modify_alias($a, $a);
&redirect("edit_alias.cgi?num=$in{'num'}file=$in{'file'}");

