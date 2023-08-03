#!/usr/local/bin/perl
# save_vfile.cgi
# Save an vacation reply file

require './forward-lib.pl';
&ReadParseMime();
&error_setup($text{'vfile_err'});

$in{'from_def'} || $in{'from'} =~ /\S/ ||
	&error($text{'rfile_efrom'});
$in{'subject_def'} || $in{'subject'} =~ /\S/ ||
	&error($text{'vfile_esubject'});

$in{'text'} =~ s/\r//g;
&open_tempfile(FILE, ">$in{'vfile'}", 1) || &error(&text('rfile_ewrite', $!));
if (!$in{'from_def'}) {
	&print_tempfile(FILE, "From: $in{'from'}\n");
	$hl++;
	}
if (!$in{'subject_def'}) {
	&print_tempfile(FILE, "Subject: $in{'subject'}\n");
	$hl++;
	}
if ($hl && $in{'text'} !~ /^(\S+):\s+\S/) {
	&print_tempfile(FILE, "\n");
	}
&print_tempfile(FILE, $in{'text'});
&close_tempfile(FILE);
&redirect("edit_alias.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}");
