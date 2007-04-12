#!/usr/local/bin/perl
# Mount or un-mount some filesystem

require './file-lib.pl';
$disallowed_buttons{'mount'} && &error($text{'ebutton'});
&ReadParse();
print "Content-type: text/plain\n\n";

# Get current status
$dir = &unmake_chroot($in{'dir'});
&foreign_require("usermount", "usermount-lib.pl");
@fstab = &usermount::list_mounts();
@mtab = &usermount::list_mounted();
($fstab) = grep { $_->[0] eq $dir } @fstab;
if (!$fstab) {
	# Doesn't exist!
	print "$text{'mount_efstab'}\n";
	exit;
	}
($mtab) = grep { $_->[0] eq $dir } @mtab;

if ($mtab) {
	# Attempt to un-mount now
	$cmd = "umount ".quotemeta($dir);
	}
else {
	# Attempt to mount now
	$cmd = "mount ".quotemeta($dir);
	}
$out = `$cmd </dev/null 2>&1`;
if ($?) {
	$out =~ s/\n/ /g;
	print $out,"\n";
	}
else {
	print "\n";
	}

