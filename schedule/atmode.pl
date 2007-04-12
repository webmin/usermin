#!/usr/local/bin/perl
# Check for one-off scheduled emails that have not run yet

$no_acl_check++;
$ENV{'REMOTE_USER'} = getpwuid($<);
require './schedule-lib.pl';

$now = time();
foreach $s (&list_schedules()) {
	if ($s->{'at'} && $s->{'at'} <= $now &&
	    (!$s->{'ran'} || $s->{'ran'} < $s->{'at'})) {
		# Can run this one
		if ($s->{'enabled'}) {
			$mail = &make_email($s);
			&mailbox::send_mail($mail);
			$s->{'ran'} = $s->{'at'};
			&save_schedule($s);
			}
		}
	}

