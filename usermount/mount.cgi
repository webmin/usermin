#!/usr/local/bin/perl
# mount.cgi
# Mount or unmount a directory

require './usermount-lib.pl';
&ReadParse();
($d) = grep { /^(mount|umount)/ } (keys %in);
$d =~ /^(\S+)_(\S+)$/;
$fs = $2;
$cmd = $1 eq "mount" ? "mount ".quotemeta($fs) : "umount ".quotemeta($fs);
&error_setup($1 eq "mount" ? $text{'mount_err1'} : $text{'mount_err2'});
if ($in{'pass_'.$fs}) {
	$temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $in{'pass_'.$fs},"\n";
	close(TEMP);
	$out = `$cmd -p - <$temp 2>&1`;
	}
else {
	$out = `$cmd </dev/null 2>&1`;
	}
unlink($temp);
if ($?) {
	&error("<pre>$out</pre>");
	}
&redirect("");

