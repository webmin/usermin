#!/usr/local/bin/perl
# manual_save.cgi
# Save manually entered directives

require './htaccess-lib.pl';
&ReadParseMime();
if (defined($in{'idx'})) {
	# files within .htaccess file
	$hconf = &get_htaccess_config($in{'file'});
	$d = $hconf->[$in{'idx'}];
	$file = $in{'file'};
	$return = "files_index.cgi";
	$start = $d->{'line'}+1; $end = $d->{'eline'}-1;
	$logtype = 'files';
	$logname = "$in{'file'}:$d->{'words'}->[0]";
	}
else {
	# .htaccess file
	$file = $in{'file'};
	$return = "htaccess_index.cgi";
	$logtype = 'htaccess'; $logname = $in{'file'};
	}

$in{'directives'} =~ s/\r//g;
$in{'directives'} =~ s/\s+$//;
@dirs = split(/\n/, $in{'directives'});
$lref = &read_file_lines($file);
if (!defined($start)) {
	$start = 0;
	$end = @$lref - 1;
	}
splice(@$lref, $start, $end-$start+1, @dirs);
&flush_file_lines();

foreach $h ('virt', 'idx', 'file') {
	push(@args, "$h=$in{$h}") if (defined($in{$h}));
	}
&redirect("$return?".join("&", @args));

