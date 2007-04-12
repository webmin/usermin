#!/usr/local/bin/perl
# Clear all sent emails

require './schedule-lib.pl';

foreach $s (&list_schedules()) {
	if ($s->{'at'} && $s->{'ran'} >= $s->{'at'}) {
		&delete_schedule($s);
		$cron = &find_cron_job($s);
		&cron::delete_cron_job($cron) if ($cron);
		}
	}
&redirect("");

