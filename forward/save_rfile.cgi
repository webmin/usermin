#!/usr/local/bin/perl
# save_rfile.cgi
# Save an autoreply file

require './forward-lib.pl';
&ReadParseMime();
&error_setup($text{'rfile_err'});

$in{'period_def'} || $in{'period'} =~ /^\d+$/ ||
	&error($text{'rfile_eperiod'});
$in{'from_def'} || $in{'from'} =~ /\S/ ||
	&error($text{'rfile_efrom'});

$in{'text'} =~ s/\r//g;
&open_tempfile(FILE, ">$in{'vfile'}", 1) || &error(&text('rfile_ewrite', $!));
if ($in{'replies'}) {
	$rfile = "$user_module_config_directory/replies";
	$rfile = $in{'replies_file'} if ($in{'replies_file'} &&
					 $in{'replies_file'} ne $rfile);
	&print_tempfile(FILE, "Reply-Tracking: $rfile\n");
	}
if (!$in{'period_def'}) {
	&print_tempfile(FILE, "Reply-Period: $in{'period'}\n");
	}
if ($in{'no_autoreply'}) {
	&print_tempfile(FILE, "No-Autoreply: $in{'no_autoreply'}\n");
	}
if (!$in{'from_def'}) {
	&print_tempfile(FILE, "From: $in{'from'}\n");
	}
&print_tempfile(FILE, $in{'text'});
&close_tempfile(FILE);
&redirect("edit_alias.cgi?num=$in{'num'}&file=$in{'file'}");
