#!/usr/local/bin/perl
# save_vacation.cgi
# Save the user's vacation file

require './vacation-lib.pl';
&ReadParseMime();

$in{'vacation_subject'} =~ s/\r//g;
$in{'vacation_from'} =~ s/\r//g;
$in{'vacation_body'} =~ s/\r//g;

open(VACATION, ">$vacation_file");
print VACATION "Subject: ",$in{'subject'},"\n";
if ($mailbox_cfg{'edit_from'}) {
	print VACATION "From: ",$in{'from'},"\n";
} else {
	print VACATION "From: ",&get_from,"\n";
}
print VACATION $in{'body'},"\n";
close(VACATION);

# Activate vacation by tweaking .forward
&start_vacation if ($in{'start_vacation'} == 1 && !$in{'update'});
&stop_vacation if ($in{'stop_vacation'} == 1 && !$in{'update'});

&redirect("");

