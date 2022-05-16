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
	copy_source_dest("usermin-systemd", "$systemd_root/$product.service");
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
if ($name) {
	foreach my $p (
		"/etc/systemd/system",
		"/usr/lib/systemd/system",
		"/lib/systemd/system") {
		if (-r "$p/$name.service" || -r "$p/$name") {
			return $p;
			}
		}
	}
if (-d "/etc/systemd/system") {
	return "/etc/systemd/system";
	}
if (-d "/usr/lib/systemd/system") {
	return "/usr/lib/systemd/system";
	}
return "/lib/systemd/system";
}
