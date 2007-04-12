#!/usr/local/bin/perl
# Delete a bunch of schedules

require './schedule-lib.pl';
&ReadParse();
&error_setup($text{'delete_err'});
@d = split(/\0/, $in{'d'});
@d || &error($text{'delete_enone'});

foreach $d (@d) {
	$sched = &get_schedule($d);
	$cron = &find_cron_job($sched);
	if ($in{'delete'}) {
		# Delete email and cron job
		&delete_schedule($sched);
		&cron::delete_cron_job($cron) if ($cron);
		}
	elsif ($in{'disable'}) {
		# Clear enabled flag
		$sched->{'enabled'} = 0;
		&save_schedule($sched);
		}
	elsif ($in{'enable'}) {
		# Set enabled flag
		$sched->{'enabled'} = 1;
		&save_schedule($sched);
		}
	}

&redirect("");

