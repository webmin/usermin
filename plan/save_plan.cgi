#!/usr/local/bin/perl
# save_plan.cgi
# Save the user's plan file

require './plan-lib.pl';
&ReadParseMime();

$in{'plan'} =~ s/\r//g;
if ($in{'plan'} =~ /\S/) {
	&open_tempfile(PLAN, ">$plan_file");
	&print_tempfile(PLAN, $in{'plan'});
	&close_tempfile(PLAN);
	}
else {
	unlink($plan_file);
	}
&redirect("");

