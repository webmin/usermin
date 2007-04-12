#!/usr/local/bin/perl
# Send a scheduled email

$no_acl_check++;
$ENV{'REMOTE_USER'} = getpwuid($<);
require './schedule-lib.pl';
$sched = &get_schedule($ARGV[0]);
$sched->{'id'} || die "Invalid scheduled email!";

if ($sched->{'enabled'}) {
	# Construct and send the email
	$mail = &make_email($sched);
	&mailbox::send_mail($mail);
	}

