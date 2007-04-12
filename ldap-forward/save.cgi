#!/usr/local/bin/perl
# Update forwarding settings

require './ldap-forward-lib.pl';
&ReadParse();

# Validate inputs
&error_setup($text{'save_err'});
$uinfo = &mailbox::get_user_ldap();
if (!$in{'fwd_def'}) {
	@fwd = split(/\s+/, $in{'fwd'});
	foreach $f (@fwd) {
		$f =~ /^\S+\@\S+$/ || &error(&text('save_efwd', $f));
		}
	@fwd || &error($text{'save_efwds'});
	}

# Update in LDAP
@old = $uinfo->get_value("mailForwardingAddress");
$ldap = &mailbox::connect_qmail_ldap();
if (@fwd) {
	$rv = $ldap->modify($uinfo->dn(),
		"replace" => { "mailForwardingAddress" => \@fwd });
	}
elsif (@old && !@fwd) {
	$rv = $ldap->modify($uinfo->dn(),
		"delete" => [ "mailForwardingAddress" ]);
	}
if ($rv->code()) {
	&error(&text('save_eldap', $rv->error));
	}

# Tell the user
&ui_print_header(undef, $module_info{'desc'}, "");
if (@fwd) {
	print $text{'save_done1'},"<p>\n";
	}
else {
	print $text{'save_done2'},"<p>\n";
	}
&ui_print_footer("", $text{'index_return'});
