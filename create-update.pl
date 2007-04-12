#!/usr/local/bin/perl
# create_update.pl

@ARGV == 3 || @ARGV ==2 ||
	die "usage: create_update.pl <module> <subversion> [description]";

chdir("/usr/local/useradmin");
$updates_dir = "/home/jcameron/webmin.com/uupdates";

open(VERSION, "version");
chop($version = <VERSION>);
close(VERSION);
$version = sprintf("%.2f0", $version);

if (&read_file($ifile = "$ARGV[0]/module.info", \%minfo)) {
	$ext = "wbm";
	}
elsif (&read_file($ifile = "$ARGV[0]/theme.info", \%minfo)) {
	$ext = "wbt";
	}
else {
	die "Module or theme $ARGV[0] not found";
	}

if (-r "$updates_dir/$ARGV[0]-$version-$ARGV[1].$ext.gz") {
	die "Update $ARGV[0]-$version-$ARGV[1].$ext.gz already exists";
	}

$minfo{'version'} = $version + $ARGV[1]/1000.0;
&write_file($ifile, \%minfo);

system("tar cvhzf $updates_dir/$ARGV[0]-$version-$ARGV[1].$ext.gz $ARGV[0]") && die "tar failed";

delete($minfo{'version'});
&write_file($ifile, \%minfo);

if ($ARGV[2]) {
	$os_support = $minfo{'os_support'} ? $minfo{'os_support'} : "0";
	open(UPDATES, "$updates_dir/uupdates.txt");
	@updates = <UPDATES>;
	close(UPDATES);
	open(UPDATES, ">$updates_dir/uupdates.txt");
	$vn = ($version + $ARGV[1]/1000.0);
	print UPDATES $ARGV[0],"\t",$vn,"\t","$ARGV[0]-$version-$ARGV[1].$ext.gz","\t",$os_support,"\t",$ARGV[2],"\n";
	print UPDATES @updates;
	close(UPDATES);

	open(UPDATES, "$updates_dir/../uupdates.html");
	@updates = <UPDATES>;
	close(UPDATES);
	open(UPDATES, ">$updates_dir/../uupdates.html");
	foreach $u (@updates) {
		print UPDATES $u;
		if ($u =~ /<!--\s+new\s+update/i) {
			print UPDATES "<tr class=mainbody> <td>$minfo{'desc'}</td> <td>$version</td> <td>$ARGV[2]</td> <td nowrap><a href=updates/$ARGV[0]-$version-$ARGV[1].$ext.gz>New module</a></td> </tr>\n\n";
			}
		}
	close(UPDATES);

	# Send off an email for Martin
	#open(MAIL, "| /usr/lib/sendmail -t -fjcameron\@webmin.com");
	#print MAIL "To: mm\@usermin.org\n";
	#print MAIL "Subject: Module $ARGV[0] updated\n";
	#print MAIL "From: jcameron\@webmin.com\n";
	#print MAIL "X-RSS-Webmin: update\n";
	#print MAIL "X-RSS-Version: usermin\n";
	#print MAIL "X-RSS-Module: $ARGV[0]\n";
	#print MAIL "X-RSS-Version: $vn\n";
	#print MAIL "\n";
	#print MAIL "<item>\n";
	#print MAIL "<title>$ARGV[0] version $vn : $ARGV[2]</title>\n";
	#print MAIL "<link>http://webmin.mamemu.de/updates.html</link>\n";
	#print MAIL "</item>\n";
	#close(MAIL);
	}

# read_file(file, &assoc, [&order], [lowercase])
# Fill an associative array with name=value pairs from a file
sub read_file
{
open(ARFILE, $_[0]) || return 0;
while(<ARFILE>) {
	s/\r|\n//g;
        if (!/^#/ && /^([^=]*)=(.*)$/) {
		$_[1]->{$_[3] ? lc($1) : $1} = $2;
		push(@{$_[2]}, $1) if ($_[2]);
        	}
        }
close(ARFILE);
return 1;
}
 
# write_file(file, array)
# Write out the contents of an associative array as name=value lines
sub write_file
{
local(%old, @order);
&read_file($_[0], \%old, \@order);
open(ARFILE, ">$_[0]");
foreach $k (@order) {
        print ARFILE $k,"=",$_[1]->{$k},"\n" if (exists($_[1]->{$k}));
	}
foreach $k (keys %{$_[1]}) {
        print ARFILE $k,"=",$_[1]->{$k},"\n" if (!exists($old{$k}));
        }
close(ARFILE);
}
