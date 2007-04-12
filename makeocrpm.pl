#!/usr/local/bin/perl
# Build an RPM file for OpenCountry

if (-r "/usr/src/OpenLinux") {
        $base_dir = "/usr/src/OpenLinux";
        }
else {
        $base_dir = "/usr/src/redhat";
        }
$spec_dir = "$base_dir/SPECS";
$source_dir = "$base_dir/SOURCES";
$rpms_dir = "$base_dir/RPMS/noarch";
$srpms_dir = "$base_dir/SRPMS";

$ver = $ARGV[0] || die "usage: makerpm.pl <version> [release]";
$rel = $ARGV[1] || "1";

$oscheck = <<EOF;
if (-r "/etc/.issue") {
	\$etc_issue = `cat /etc/.issue`;
	}
elsif (-r "/etc/issue") {
	\$etc_issue = `cat /etc/issue`;
	}
\$uname = `uname -a`;
EOF
open(OS, "os_list.txt");
while(<OS>) {
	chop;
	if (/^([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t*(.*)$/ && $5) {
		$if = $count++ == 0 ? "if" : "elsif";
		$oscheck .= "$if ($5) {\n".
			    "	print \"oscheck='$1'\\n\";\n".
			    "	}\n";
		}
	}
close(OS);
$oscheck =~ s/\\/\\\\/g;
$oscheck =~ s/`/\\`/g;
$oscheck =~ s/\$/\\\$/g;

open(TEMP, "maketemp.pl");
while(<TEMP>) {
	$maketemp .= $_;
	}
close(TEMP);
$maketemp =~ s/\\/\\\\/g;
$maketemp =~ s/`/\\`/g;
$maketemp =~ s/\$/\\\$/g;

system("cp tarballs/usermin-$ver.tar.gz $source_dir");
open(SPEC, ">$spec_dir/occolors-$ver.spec");
print SPEC <<EOF;
#%define BuildRoot /tmp/%{name}-%{version}
%define __spec_install_post %{nil}

Summary: A web-based user account administration interface
Name: occolors
Version: $ver
Release: $rel
Provides: %{name}-%{version}
PreReq: /bin/sh /usr/bin/perl
Requires: /bin/sh /usr/bin/perl
Copyright: Freeware
Group: System/Tools
Source: http://www.webmin.com/download/usermin-%{version}.tar.gz
Vendor: Open Country, Inc.
BuildRoot: /tmp/%{name}-%{version}
BuildArchitectures: noarch
AutoReq: 0
%description
A web-based user account administration interface for Unix systems.

After installation, enter the URL http://localhost:11283/ into your
browser and login as any user on your system.

%prep
%setup -q -n usermin-$ver

%build
cp -r /usr/local/useradmin/opencountry-theme .
cp -r /usr/local/useradmin/bordeaux-theme .
(find . -name '*.cgi' ; find . -name '*.pl') | perl perlpath.pl /usr/bin/perl -
rm -f mount/freebsd-mounts-*
rm -f mount/openbsd-mounts-*
rm -rf theme caldera mscstyle3
echo bordeaux-theme >defaulttheme
grep -v webmin_config= commands/config >commands/config.tmp
echo webmin_config=/etc/ocwebmin/custom >>commands/config.tmp
mv commands/config.tmp commands/config
grep -v webmin_apache= htaccess/config >htaccess/config.tmp
echo webmin_apache=/etc/ocwebmin/apache >>htaccess/config.tmp
mv htaccess/config.tmp htaccess/config
chmod -R og-w .

%install
mkdir -p %{buildroot}/usr/libexec/occolors
mkdir -p %{buildroot}/etc/rc.d/{rc0.d,rc1.d,rc2.d,rc3.d,rc5.d,rc6.d}
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/pam.d
cp -rp * %{buildroot}/usr/libexec/occolors
cat setup.sh | sed -e 's/Usermin/OC-Colors/' >%{buildroot}/usr/libexec/occolors/setup.sh
cp /usr/local/useradmin/occolors-init %{buildroot}/etc/init.d/occolors
cp usermin-pam %{buildroot}/etc/pam.d/occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc2.d/S99occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc3.d/S99occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc5.d/S99occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc0.d/K10occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc1.d/K10occolors
ln -s /etc/init.d/occolors %{buildroot}/etc/rc.d/rc6.d/K10occolors
echo rpm >%{buildroot}/usr/libexec/occolors/install-type

%clean
#%{rmDESTDIR}
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
/usr/libexec/occolors
/etc/init.d/occolors
/etc/rc.d/rc2.d/S99occolors
/etc/rc.d/rc3.d/S99occolors
/etc/rc.d/rc5.d/S99occolors
/etc/rc.d/rc0.d/K10occolors
/etc/rc.d/rc1.d/K10occolors
/etc/rc.d/rc6.d/K10occolors
/etc/pam.d/occolors

%pre
perl <<EOD;
$maketemp
EOD
if [ "\$?" != "0" ]; then
	echo "Failed to create or check temp files directory /tmp/.webmin"
	exit 1
fi
perl >/tmp/.webmin/\$\$.check <<EOD;
$oscheck
EOD
. /tmp/.webmin/\$\$.check
rm -f /tmp/.webmin/\$\$.check
if [ ! -r /etc/occolors/config ]; then
	if [ "\$oscheck" = "" ]; then
		echo Unable to identify operating system
		exit 2
	fi
	echo Operating system is \$oscheck
	if [ "\$USERMIN_PORT\" != \"\" ]; then
		port=\$USERMIN_PORT
	else
		port=11283
	fi
	perl -e 'use Socket; socket(FOO, PF_INET, SOCK_STREAM, getprotobyname("tcp")); setsockopt(FOO, SOL_SOCKET, SO_REUSEADDR, pack("l", 1)); bind(FOO, pack_sockaddr_in(\$ARGV[0], INADDR_ANY)) || exit(1); exit(0);' \$port
	if [ "\$?" != "0" ]; then
		echo Port \$port is already in use
		exit 3
	fi
fi

%post
inetd=`grep "^inetd=" /etc/occolors/miniserv.conf 2>/dev/null | sed -e 's/inetd=//g'`
if [ "\$1" != 1 ]; then
	# Upgrading the RPM, so stop the old occolors properly
	if [ "$inetd" != "1" ]; then
		/etc/init.d/occolors stop >/dev/null 2>&1
	fi
fi
cd /usr/libexec/occolors
config_dir=/etc/occolors
var_dir=/var/occolors
perl=/usr/bin/perl
autoos=3
if [ "\$USERMIN_PORT\" != \"\" ]; then
	port=\$USERMIN_PORT
else
	port=11283
fi
host=`hostname`
ssl=1
atboot=1
nochown=1
autothird=1
noperlpath=1
nouninstall=1
nostart=1
pam=occolors
export config_dir var_dir perl autoos port ssl nochown autothird noperlpath nouninstall nostart allow
./setup.sh >/tmp/.webmin/occolors-setup.out 2>&1
rm -f /var/lock/subsys/occolors
if [ "$inetd" != "1" ]; then
	/etc/init.d/occolors start >/dev/null 2>&1 </dev/null
fi
cat >/etc/occolors/uninstall.sh <<EOFF
#!/bin/sh
printf "Are you sure you want to uninstall OC-Colors? (y/n) : "
read answer
printf "\\n"
if [ "\\\$answer" = "y" ]; then
	echo "Removing OC-Colors RPM .."
	rpm -e --nodeps occolors
	echo "Done!"
fi
EOFF
chmod +x /etc/occolors/uninstall.sh
port=`grep "^port=" /etc/occolors/miniserv.conf | sed -e 's/port=//g'`
perl -e 'use Net::SSLeay' >/dev/null 2>/dev/null
if [ "\$?" = "0" ]; then
	echo "OC-Colors install complete. You can now login to https://\$host:\$port/"
else
	echo "OC-Colors install complete. You can now login to http://\$host:\$port/"
fi
echo "as any user on your system."

%preun
if [ "\$1" = 0 ]; then
	grep root=/usr/libexec/occolors /etc/occolors/miniserv.conf >/dev/null 2>&1
	if [ "\$?" = 0 ]; then
		# RPM is being removed, and no new version of occolors
		# has taken it's place. Stop the server
		/etc/init.d/occolors stop >/dev/null 2>&1
		/bin/true
	fi
fi

%postun
if [ "\$1" = 0 ]; then
	grep root=/usr/libexec/occolors /etc/occolors/miniserv.conf >/dev/null 2>&1
	if [ "\$?" = 0 ]; then
		# RPM is being removed, and no new version of occolors
		# has taken it's place. Delete the config files
		rm -rf /etc/occolors /var/occolors
	fi
fi

EOF
close(SPEC);

system("rpm -ba --target=noarch $spec_dir/occolors-$ver.spec") && exit;
if (-d "rpm") {
	system("mv /usr/src/OpenLinux/RPMS/noarch/occolors-$ver-$rel.noarch.rpm rpm/oc/occolors-$ver-$rel.noarch.rpm");
	print "Moved to rpm/oc/occolors-$ver-$rel.noarch.rpm\n";
	system("mv /usr/src/OpenLinux/SRPMS/occolors-$ver-$rel.src.rpm rpm/oc/occolors-$ver-$rel.src.rpm");
	print "Moved to rpm/oc/occolors-$ver-$rel.src.rpm\n";
	system("chown jcameron: rpm/oc/occolors-$ver-$rel.noarch.rpm rpm/oc/occolors-$ver-$rel.src.rpm");
	}


