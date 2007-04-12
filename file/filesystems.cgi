#!/usr/local/bin/perl
# List all filesystems and their types

require './file-lib.pl';
print "Content-type: text/plain\n\n";
if (!&foreign_check("usermount")) {
	print "0\n";
	exit;
	}
&foreign_require("usermount", "usermount-lib.pl");
@mtab = &usermount::list_mounted();
%mtab = map { $_->[0], $_ } @mtab;
@fstab = &usermount::list_mounts();
%fstab = map { $_->[0], $_ } @fstab;
@mounts = ( @fstab, grep { !$fstab{$_->[0]} } @mtab );

print "1\n";
foreach $m (sort { length($a->[0]) <=> length($b->[0]) } @mounts) {
	next if ($m->[0] !~ /^\//);

	# Check if this is user-mountable
	local %usermount::options;
	&usermount::parse_options($m->[2], $m->[3]);
	next if (!defined($usermount::options{'user'}));

	$m->[1] =~ s/\\/\//g;
	$chrooted = &make_chroot($m->[0]);
	if ($chrooted) {
		print join(" ", $chrooted, @$m[1..3], 0, 0, 0,
				$mtab{$m->[0]} ? 1 : 0,
				$fstab{$m->[0]} ? 1 : 0),"\n";
		}
	}

