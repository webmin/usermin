#!/usr/local/bin/perl
# Show an attached file
use File::Basename;
require './schedule-lib.pl';
&ReadParse();
$sched = &get_schedule($in{'sched'});
@files = &list_schedule_files($sched);
($file) = grep { $_->{'id'} eq $in{'id'} } @files;
$file || &error($text{'view_efile'});

my $type = &guess_mime_type($file->{'id'});
if($type eq 'application/octet-stream') {
	my $filename = basename($file->{'id'});
	print "Content-Disposition: attachment; filename=$filename\n";
	}
print "Content-type: ",$type,"\n\n";
open(FILE, $file->{'file'});
while(<FILE>) { print; }
close(FILE);

