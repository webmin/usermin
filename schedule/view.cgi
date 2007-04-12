#!/usr/local/bin/perl
# Show an attached file

require './schedule-lib.pl';
&ReadParse();
$sched = &get_schedule($in{'sched'});
@files = &list_schedule_files($sched);
($file) = grep { $_->{'id'} eq $in{'id'} } @files;
$file || &error($text{'view_efile'});

print "Content-type: ",&guess_mime_type($file->{'id'}),"\n\n";
open(FILE, $file->{'file'});
while(<FILE>) { print; }
close(FILE);

