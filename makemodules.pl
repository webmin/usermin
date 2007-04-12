#!/usr/local/bin/perl

if (@ARGV != 1) {
	die "usage: makemodules.pl <version>";
	}
$vers = $ARGV[0];
$dir = "usermin-$vers";
chdir("/usr/local/useradmin");
-d "tarballs/$dir" || die "No such version $vers";

# Create per-module .wbm files
print "Creating modules\n";
opendir(DIR, "tarballs/$dir");
while($d = readdir(DIR)) {
	local $minfo = "tarballs/$dir/$d/module.info";
	next if (!-r $minfo);
	unlink("umodules/$d.wbm");
	system("(cd tarballs/$dir ; tar chf - $d) >umodules/$d.wbm");
	}
closedir(DIR);

# read_file(file, &assoc, [&order])
# Fill an associative array with name=value pairs from a file
sub read_file
{
open(ARFILE, $_[0]) || return 0;
while(<ARFILE>) {
        chop;
        if (!/^#/ && /^([^=]+)=(.*)$/) {
		$_[1]->{$1} = $2;
		push(@{$_[2]}, $1);
        	}
        }
close(ARFILE);
return 1;
}
 
# write_file(file, array)
# Write out the contents of an associative array as name=value lines
sub write_file
{
local($arr);
$arr = $_[1];
open(ARFILE, "> $_[0]");
foreach $k (keys %$arr) {
        print ARFILE "$k=$$arr{$k}\n";
        }
close(ARFILE);
}
