#!/usr/bin/perl
# updateboot.pl
# Called by setup.sh to update boot script

$no_acl_check++;
$product = 'usermin';

BEGIN { push(@INC, "."); };
use WebminCore;
&init_config();

$< == 0 || die "updateboot.pl must be run as root";

# Update boot script
if (-d "/etc/systemd" &&
    &has_command("systemctl") &&
    &execute_command("systemctl list-units") == 0) {
	# Delete all possible service files
	my $systemd_root = &get_systemd_root();
	foreach my $p (
	        "/etc/systemd/system",
	        "/usr/lib/systemd/system",
	        "/lib/systemd/system") {
	    unlink("$p/$product.service");
	    unlink("$p/$product");
	    }

	my $temp = &transname();
	&copy_source_dest("$root_directory/usermin-systemd", $temp);
	my $lref = &read_file_lines($temp);
	foreach my $l (@{$lref}) {
		$l =~ s/(WEBMIN_[A-Z]+)/$ENV{$1}/g;
		}
	&flush_file_lines($temp);
	copy_source_dest($temp, "$systemd_root/$product.service");

	system("systemctl daemon-reload >/dev/null 2>&1");
	system("systemctl enable $product >/dev/null 2>&1");
	}
elsif (-d "/etc/init.d") {
	copy_source_dest("usermin-init", "/etc/init.d/$product");
	system("chkconfig --add $product >/dev/null 2>&1");
	}

sub get_systemd_root
{
my ($name) = @_;
# Default systemd paths 
my $systemd_local_conf = "/etc/systemd/system";
my $systemd_unit_dir1 = "/usr/lib/systemd/system";
my $systemd_unit_dir2 = "/lib/systemd/system";
if ($name) {
	foreach my $p (
		$systemd_local_conf,
		$systemd_unit_dir1,
		$systemd_unit_dir2) {
		if (-r "$p/$name.service" || -r "$p/$name") {
			return $p;
			}
		}
	}
# Debian prefers /lib/systemd/system
if ($gconfig{'os_type'} eq 'debian-linux' &&
    -d $systemd_unit_dir2) {
	return $systemd_unit_dir2;
	}
# RHEL and other systems /usr/lib/systemd/system
if (-d $systemd_unit_dir1) {
	return $systemd_unit_dir1;
	}
# Fallback path for other systems
return $systemd_unit_dir2;
}

