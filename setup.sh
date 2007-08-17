#!/bin/sh
# setup.sh
# This script should be run after the usermin archive is unpacked, in order
# to setup the various config files

# Find install directory
LANG=
export LANG
cd `dirname $0`
if [ -x /bin/pwd ]; then
	wadir=`/bin/pwd`
else
	wadir=`pwd`;
fi
srcdir=$wadir
ver=`cat "$wadir/version"`

# Find temp directory
if [ "$tempdir" = "" ]; then
	tempdir=$tempdir
fi

if [ $? != "0" ]; then
	echo "ERROR: Cannot find the Usermin install directory";
	echo "";
	exit 1;
fi

echo "***********************************************************************"
echo "*            Welcome to the Usermin setup script, version $ver       *"
echo "***********************************************************************"
echo "Usermin is a web-based interface that allows Unix-like operating"
echo "systems and common Unix services to be easily administered."
echo ""

# Only root can run this
id | grep "uid=0(" >/dev/null
if [ $? != "0" ]; then
	uname -a | grep -i CYGWIN >/dev/null
	if [ $? != "0" ]; then
		echo "ERROR: The Usermin install script must be run as root";
		echo "";
		exit 1;
	fi
fi

# Use the supplied destination directory, if any
if [ "$1" != "" ]; then
	wadir=$1
	echo "Installing Usermin from $srcdir to $wadir ..."
	if [ ! -d "$wadir" ]; then
		mkdir "$wadir"
		if [ "$?" != "0" ]; then
			echo "ERROR: Failed to create $wadir"
			echo ""
			exit 1
		fi
	else
		# Make sure dest dir is not in use
		ls "$wadir" | grep -v rpmsave >/dev/null 2>&1
		if [ "$?" = "0" -a ! -r "$wadir/setup.sh" ]; then
			echo "ERROR: Installation directory $wadir contains other files"
			echo ""
			exit 1
		fi
	fi
else
	echo "Installing Usermin in $wadir ..."
fi
cd "$wadir"

# Display install directory
allmods=`cd "$srcdir"; echo */module.info | sed -e 's/\/module.info//g'`
if [ "$allmods" = "" ]; then
	echo "ERROR: Failed to get module list"
	echo ""
	exit 1
fi
echo ""

# Ask for usermin config directory
echo "***********************************************************************"
echo "Usermin uses separate directories for configuration files and log files."
echo "Unless you want to run multiple versions of Usermin at the same time"
echo "you can just accept the defaults."
echo ""
printf "Config file directory [/etc/usermin]: "
if [ "$config_dir" = "" ]; then
	read config_dir
fi
if [ "$config_dir" = "" ]; then
	config_dir=/etc/usermin
fi
abspath=`echo $config_dir | grep "^/"`
if [ "$abspath" = "" ]; then
	echo "Config directory must be an absolute path"
	echo ""
	exit 2
fi
if [ ! -d $config_dir ]; then
	mkdir $config_dir;
	if [ $? != 0 ]; then
		echo "ERROR: Failed to create directory $config_dir"
		echo ""
		exit 2
	fi
fi
if [ -r "$config_dir/config" ]; then
	echo "Found existing Usermin configuration in $config_dir"
	echo ""
	upgrading=1
fi

# Check if upgrading from an old version
if [ "$upgrading" = 1 ]; then
	echo ""

	# Get current var path
	var_dir=`cat $config_dir/var-path`

	# Force creation if non-existant
	mkdir -p $var_dir >/dev/null 2>&1

	# Get current perl path
	perl=`cat $config_dir/perl-path`

	# Create temp files directory
	$perl "$srcdir/maketemp.pl"
	if [ "$?" != "0" ]; then
		echo "ERROR: Failed to create or check temp files directory $tempdir"
		echo ""
		exit 2
	fi

	# Get old os name and version
	os_type=`grep "^os_type=" $config_dir/config | sed -e 's/os_type=//g'`
	os_version=`grep "^os_version=" $config_dir/config | sed -e 's/os_version=//g'`
	real_os_type=`grep "^real_os_type=" $config_dir/config | sed -e 's/real_os_type=//g'`
	real_os_version=`grep "^real_os_version=" $config_dir/config | sed -e 's/real_os_version=//g'`

	# Get old root, host, port, ssl and boot flag
	oldwadir=`grep "^root=" $config_dir/miniserv.conf | sed -e 's/root=//g'`
	port=`grep "^port=" $config_dir/miniserv.conf | sed -e 's/port=//g'`
	ssl=`grep "^ssl=" $config_dir/miniserv.conf | sed -e 's/ssl=//g'`
	atboot=`grep "^atboot=" $config_dir/miniserv.conf | sed -e 's/atboot=//g'`
	inetd=`grep "^inetd=" $config_dir/miniserv.conf | sed -e 's/inetd=//g'`

	if [ "$inetd" != "1" ]; then
		# Stop old version
		$config_dir/stop >/dev/null 2>&1
	fi

	# Copy files to target directory
	if [ "$wadir" != "$srcdir" ]; then
		echo "Copying files to $wadir .."
		(cd "$srcdir" ; tar cf - . | (cd "$wadir" ; tar xf -))
		echo "..done"
		echo ""
	fi

	# Update ACLs
	$perl "$wadir/newmods.pl" $config_dir $allmods

	# Update miniserv.conf with new root directory and mime types file
	grep -v "^root=" $config_dir/miniserv.conf | grep -v "^mimetypes=" >$tempdir/$$.miniserv.conf
	mv $tempdir/$$.miniserv.conf $config_dir/miniserv.conf
	echo "root=$wadir" >> $config_dir/miniserv.conf
	echo "mimetypes=$wadir/mime.types" >> $config_dir/miniserv.conf
	grep logout= $config_dir/miniserv.conf >/dev/null
	if [ $? != "0" ]; then
		echo "logout=$config_dir/logout-flag" >> $config_dir/miniserv.conf
	fi
	
	# Check for third-party modules in old version
	if [ "$wadir" != "$oldwadir" ]; then
		echo "Checking for third-party modules .."
		if [ "$webmin_upgrade" != "" ]; then
			autothird=1
		fi
		$perl "$wadir/thirdparty.pl" "$wadir" "$oldwadir" $autothird
		echo "..done"
		echo ""
	fi

	# Remove old cache of module infos
	rm -f $config_dir/module.infos.cache
else
	# Config directory exists .. make sure it is not in use
	ls $config_dir | grep -v rpmsave >/dev/null 2>&1
	if [ "$?" = "0" -a "$config_dir" != "/etc/usermin" ]; then
		echo "ERROR: Config directory $config_dir is not empty"
		echo ""
		exit 2
	fi

	# Ask for log directory
	printf "Log file directory [/var/usermin]: "
	if [ "$var_dir" = "" ]; then
		read var_dir
	fi
	if [ "$var_dir" = "" ]; then
		var_dir=/var/usermin
	fi
	abspath=`echo $var_dir | grep "^/"`
	if [ "$abspath" = "" ]; then
		echo "Log file directory must be an absolute path"
		echo ""
		exit 3
	fi
	if [ "$var_dir" = "/" ]; then
		echo "Log directory cannot be /"
		exit ""
		exit 3
	fi
	if [ ! -d $var_dir ]; then
		mkdir $var_dir
		if [ $? != 0 ]; then
			echo "ERROR: Failed to create directory $var_dir"
			echo ""
			exit 3
		fi
	fi
	echo ""

	# Ask where perl is installed
	echo "***********************************************************************"
	echo "Usermin is written entirely in Perl. Please enter the full path to the"
	echo "Perl 5 interpreter on your system."
	echo ""
	if [ -x /usr/bin/perl ]; then
		perldef=/usr/bin/perl
	elif [ -x /usr/local/bin/perl ]; then
		perldef=/usr/local/bin/perl
	else
		perldef=""
	fi
	if [ "$perl" = "" ]; then
		if [ "$perldef" = "" ]; then
			printf "Full path to perl: "
			read perl
			if [ "$perl" = "" ]; then
				echo "ERROR: No path entered!"
				echo ""
				exit 4
			fi
		else
			printf "Full path to perl (default $perldef): "
			read perl
			if [ "$perl" = "" ]; then
				perl=$perldef
			fi
		fi
	fi
	echo ""

	# Test perl 
	echo "Testing Perl ..."
	if [ ! -x $perl ]; then
		echo "ERROR: Failed to find perl at $perl"
		echo ""
		exit 5
	fi
	$perl -e 'print "foobar\n"' 2>/dev/null | grep foobar >/dev/null
	if [ $? != "0" ]; then
		echo "ERROR: Failed to run test perl script. Maybe $perl is"
		echo "not the perl interpreter, or is not installed properly"
		echo ""
		exit 6
	fi
	$perl -e 'exit ($] < 5.002 ? 1 : 0)'
	if [ $? = "1" ]; then
		echo "ERROR: Detected old perl version. Usermin requires"
		echo "perl 5.002 or better to run"
		echo ""
		exit 7
	fi
	$perl -e 'use Socket; print "foobar\n"' 2>/dev/null | grep foobar >/dev/null
	if [ $? != "0" ]; then
		echo "ERROR: Perl Socket module not installed. Maybe Perl has"
		echo "not been properly installed on your system"
		echo ""
		exit 8
	fi
	$perl -e '$c = crypt("xx", "yy"); exit($c ? 0 : 1)'
        if [ $? != "0" ]; then
                $perl -e 'use Crypt::UnixCrypt' >/dev/null 2>&1
        fi
	if [ $? != "0" ]; then
		echo "ERROR: Perl crypt function does not work. Maybe Perl has"
		echo "not been properly installed on your system"
		echo ""
		exit 8
	fi
	echo "Perl seems to be installed ok"
	echo ""

	# Create temp files directory
	$perl "$srcdir/maketemp.pl"
	if [ "$?" != "0" ]; then
		echo "ERROR: Failed to create or check temp files directory $tempdir"
		echo ""
		exit 2
	fi

	# Ask for operating system type
	echo "***********************************************************************"
	if [ "$os_type" = "" ]; then
		if [ "$autoos" = "" ]; then
			autoos=2
		fi
		$perl "$srcdir/oschooser.pl" "$srcdir/os_list.txt" $tempdir/$$.os $autoos
		if [ $? != 0 ]; then
			exit $?
		fi
		. $tempdir/$$.os
		rm -f $tempdir/$$.os
	fi
	echo "Operating system name:    $real_os_type"
	echo "Operating system version: $real_os_version"
	echo ""

	# Ask for web server port, name and password
	echo "***********************************************************************"
	echo "Usermin uses its own password protected web server to provide access"
	echo "to the administration programs. The setup script needs to know :"
	echo " - What port to run the web server on. There must not be another"
	echo "   web server already using this port."
	echo " - If the webserver should use SSL (if your system supports it)."
	echo ""
	printf "Web server port (default 20000): "
	if [ "$port" = "" ]; then
		read port
		if [ "$port" = "" ]; then
			port=20000
		fi
	fi
	if [ $port -lt 1 ]; then
		echo "ERROR: $port is not a valid port number"
		echo ""
		exit 11
	fi
	if [ $port -gt 65535 ]; then
		echo "ERROR: $port is not a valid port number. Port numbers cannot be"
		echo "       greater than 65535"
		echo ""
		exit 12
	fi
	$perl -e 'use Socket; socket(FOO, PF_INET, SOCK_STREAM, getprotobyname("tcp")); setsockopt(FOO, SOL_SOCKET, SO_REUSEADDR, pack("l", 1)); bind(FOO, pack_sockaddr_in($ARGV[0], INADDR_ANY)) || exit(1); exit(0);' $port
	if [ $? != "0" ]; then
		echo "ERROR: TCP port $port is already in use by another program"
		echo ""
		exit 13
	fi

	# Ask the user if SSL should be used
	if [ "$ssl" = "" ]; then
		ssl=0
		$perl -e 'use Net::SSLeay' >/dev/null 2>/dev/null
		if [ $? = "0" ]; then
			printf "Use SSL (y/n): "
			read sslyn
			if [ "$sslyn" = "y" -o "$sslyn" = "Y" ]; then
				ssl=1
			fi
		else
			echo "The Perl SSLeay library is not installed. SSL not available."
			rm -f core
		fi
	fi

	# Don't use SSL if missing Net::SSLeay
	if [ "$ssl" = "1" ]; then
		$perl -e 'use Net::SSLeay' >/dev/null 2>/dev/null
		if [ $? != "0" ]; then
			ssl=0
		fi
	fi

	# Copy files to target directory
	echo "***********************************************************************"
	if [ "$wadir" != "$srcdir" ]; then
		echo "Copying files to $wadir .."
		(cd "$srcdir" ; tar cf - . | (cd "$wadir" ; tar xf -))
		echo "..done"
		echo ""
	fi

	# Create webserver config file
	echo $perl > $config_dir/perl-path
	echo $var_dir > $config_dir/var-path
	echo "Creating web server config files.."
	cfile=$config_dir/miniserv.conf
	echo "port=$port" >> $cfile
	echo "root=$wadir" >> $cfile
	echo "mimetypes=$wadir/mime.types" >> $cfile
	echo "addtype_cgi=internal/cgi" >> $cfile
	echo "realm=Usermin Server" >> $cfile
	echo "logfile=$var_dir/miniserv.log" >> $cfile
	echo "errorlog=$var_dir/miniserv.error" >> $cfile
	echo "pidfile=$var_dir/miniserv.pid" >> $cfile
	echo "logtime=168" >> $cfile
	echo "ppath=$ppath" >> $cfile
	echo "ssl=$ssl" >> $cfile
	echo "env_WEBMIN_CONFIG=$config_dir" >> $cfile
	echo "env_WEBMIN_VAR=$var_dir" >> $cfile
	echo "atboot=$atboot" >> $cfile
	echo "logout=$config_dir/logout-flag" >> $cfile
	echo "listen=20000" >> $cfile
	echo "denyfile=\\.pl\$" >> $cfile
	echo "log=1" >> $cfile
	echo "blockhost_failures=5" >> $cfile
	echo "blockhost_time=60" >> $cfile
	if [ "$allow" != "" ]; then
		echo "allow=$allow" >> $cfile
	fi
	if [ "$session" != "" ]; then
		echo "session=$session" >> $cfile
	else
		echo "session=1" >> $cfile
	fi
	echo "unixauth=user" >> $cfile
	echo "localauth=1" >> $cfile
	echo "pam=usermin" >> $cfile
	#echo "denyusers=root" >> $cfile

	# Append package-specific info to config file
	if [ -r "$wadir/miniserv-conf" ]; then
		cat "$wadir/miniserv-conf" >>$cfile
	fi

	ufile=$config_dir/miniserv.users
	echo "user:x:0::" > $ufile
	chmod 644 $ufile
	echo "userfile=$ufile" >> $cfile

	kfile=$config_dir/miniserv.pem
	openssl version >/dev/null 2>&1
	if [ "$?" = "0" ]; then
		# We can generate a new SSL key for this host
		host=`hostname`
		openssl req -newkey rsa:512 -x509 -nodes -out $tempdir/cert -keyout $tempdir/key -days 1825 >/dev/null 2>&1 <<EOF
.
.
.
Usermin Webserver on $host
.
*
root@$host
EOF
		if [ "$?" = "0" ]; then
			cat $tempdir/cert $tempdir/key >$kfile
		fi
		rm -f $tempdir/cert $tempdir/key
	fi
	if [ ! -r $kfile ]; then
		# Fall back to the built-in key
		cp "$wadir/miniserv.pem" $kfile
	fi
	chmod 600 $kfile
	echo "keyfile=$config_dir/miniserv.pem" >> $cfile

	chmod 644 $cfile
	echo "..done"
	echo ""

	echo "Creating access control file.."
	defmods=`cat "$wadir/defaultmodules" 2>/dev/null`
	if [ "$defmods" = "" ]; then
		defmods="$allmods"
	fi
	afile=$config_dir/webmin.acl
	rm -f $afile
	echo "user: $defmods" >> $afile
	chmod 644 $afile
	echo "..done"
	echo ""

fi

if [ "$noperlpath" = "" ]; then
	echo "Inserting path to perl into scripts.."
	(find "$wadir" -name '*.cgi' -print ; find "$wadir" -name '*.pl' -print) | $perl "$wadir/perlpath.pl" $perl -
	echo "..done"
	echo ""
fi

echo "Creating start and stop scripts.."
rm -f $config_dir/stop $config_dir/start
echo "#!/bin/sh" >>$config_dir/start
echo "echo Starting Usermin server in $wadir" >>$config_dir/start
echo "trap '' 1" >>$config_dir/start
echo "LANG=" >>$config_dir/start
echo "export LANG" >>$config_dir/start
echo "#PERLIO=:raw" >>$config_dir/start
echo "unset PERLIO" >>$config_dir/start
echo "export PERLIO" >>$config_dir/start
uname -a | grep -i 'HP/*UX' >/dev/null
if [ $? = "0" ]; then
	echo "exec "$wadir/miniserv.pl" $config_dir/miniserv.conf &" >>$config_dir/start
else
	uname -a | grep -i FreeBSD >/dev/null
	if [ "$?" = "0" ]; then
		echo "LD_PRELOAD=`echo /usr/lib/libpam.so.?`" >>$config_dir/start
		echo "export LD_PRELOAD" >>$config_dir/start
	fi
	echo "exec "$wadir/miniserv.pl" $config_dir/miniserv.conf" >>$config_dir/start
fi

echo "#!/bin/sh" >>$config_dir/stop
echo "echo Stopping Usermin server in $wadir" >>$config_dir/stop
echo "pidfile=\`grep \"^pidfile=\" $config_dir/miniserv.conf | sed -e 's/pidfile=//g'\`" >>$config_dir/stop
echo "kill \`cat \$pidfile\`" >>$config_dir/stop
chmod 755 $config_dir/start $config_dir/stop
echo "..done"
echo ""

if [ "$upgrading" = 1 ]; then
	echo "Updating config files.."
else
	echo "Copying config files.."
fi
$perl "$wadir/copyconfig.pl" "$os_type" "$os_version" "$wadir" $config_dir "" $allmods
if [ "$upgrading" != 1 ]; then
	# Store the OS and version
	echo "os_type=$os_type" >> $config_dir/config
	echo "os_version=$os_version" >> $config_dir/config
	echo "real_os_type=$real_os_type" >> $config_dir/config
	echo "real_os_version=$real_os_version" >> $config_dir/config
	if [ -r /etc/system.cnf ]; then
		# Found a caldera system config file .. get the language
		source /etc/system.cnf
		if [ "$CONF_LST_LANG" = "us" ]; then
			CONF_LST_LANG=en
		elif [ "$CONF_LST_LANG" = "uk" ]; then
			CONF_LST_LANG=en
		fi
		grep "lang=$CONF_LST_LANG," "$wadir/lang_list.txt" >/dev/null 2>&1
		if [ "$?" = 0 ]; then
			echo "lang=$CONF_LST_LANG" >> $config_dir/config
		fi
	fi

	# Set additional usermin-specific options
	echo "userconfig=.usermin" >> $config_dir/config
	echo "overlang=ulang" >> $config_dir/config
	echo "nofeedbackcc=2" >> $config_dir/config
	echo "nofeedbackconf=1" >> $config_dir/config
fi
echo $ver > $config_dir/version
echo "..done"
echo ""

# Set passwd_ fields in miniserv.conf from global config
for field in passwd_file passwd_uindex passwd_pindex passwd_cindex passwd_mindex; do
	grep $field= $config_dir/miniserv.conf >/dev/null
	if [ "$?" != "0" ]; then
		grep $field= $config_dir/config >> $config_dir/miniserv.conf
	fi
done
grep passwd_mode= $config_dir/miniserv.conf >/dev/null
if [ "$?" != "0" ]; then
	echo passwd_mode=2 >> $config_dir/miniserv.conf
fi

# Set usermin-specific SID cookie name
grep sidname= $config_dir/miniserv.conf >/dev/null
if [ "$?" != "0" ]; then
	echo sidname=usid >> $config_dir/miniserv.conf
fi

# Set a special theme if none was set before
if [ "$theme" = "" ]; then
	theme=`cat "$wadir/defaulttheme" 2>/dev/null`
fi
oldthemeline=`grep "^theme=" $config_dir/config`
oldtheme=`echo $oldthemeline | sed -e 's/theme=//g'`
if [ "$theme" != "" ] && [ "$oldthemeline" = "" ] && [ -d "$wadir/$theme" ]; then
	echo "theme=$theme" >> $config_dir/config
	echo "preroot=$theme" >> $config_dir/miniserv.conf
fi

# Set the product field in the global config
grep product= $config_dir/config >/dev/null
if [ "$?" != "0" ]; then
	echo product=usermin >> $config_dir/config
fi

# If password delays are not specifically disabled, enable them
grep passdelay= $config_dir/miniserv.conf >/dev/null
if [ "$?" != "0" ]; then
	echo passdelay=1 >> $config_dir/miniserv.conf
fi

if [ "$nouninstall" = "" ]; then
	echo "Creating uninstall script $config_dir/uninstall.sh .."
	cat >$config_dir/uninstall.sh <<EOF
#!/bin/sh
printf "Are you sure you want to uninstall Usermin? (y/n) : "
read answer
printf "\n"
if [ "\$answer" = "y" ]; then
	$config_dir/stop
	echo "Deleting $wadir .."
	rm -rf "$wadir"
	echo "Deleting $config_dir .."
	rm -rf $config_dir
	echo "Done!"
fi
EOF
	chmod +x $config_dir/uninstall.sh
	echo "..done"
	echo ""
fi

echo "Changing ownership and permissions .."
chown -R root:bin $config_dir
chmod -R 755 $config_dir
if [ "$nochown" = "" ]; then
	chown -R root:bin "$wadir"
	chmod -R og-w "$wadir"
	if [ $var_dir != "/var" ]; then
		chown -R root:bin $var_dir
		chmod -R og-w $var_dir
		chmod -R a+rx "$wadir"
	fi
fi
chmod 600 $config_dir/miniserv.pem 2>/dev/null
echo "..done"
echo ""

# Save target directory if one was specified
if [ "$wadir" != "$srcdir" ]; then
	echo $wadir >$config_dir/install-dir
else
	rm -f $config_dir/install-dir
fi

if [ "$nostart" = "" ]; then
	if [ "$inetd" != "1" ]; then
		echo "Attempting to start Usermin mini web server.."
		$config_dir/start
		if [ $? != "0" ]; then
			echo "ERROR: Failed to start web server!"
			echo ""
			exit 14
		fi
		echo "..done"
		echo ""
	fi

	echo "***********************************************************************"
	echo "Usermin has been installed and started successfully. Use your web"
	echo "browser to go to"
	echo ""
	host=`hostname`
	if [ "$ssl" = "1" ]; then
		echo "  https://$host:$port/"
	else
		echo "  http://$host:$port/"
	fi
	echo ""
	echo "and login as any Unix user on your system."
	echo ""
	if [ "$ssl" = "1" ]; then
		echo "Because Usermin uses SSL for encryption only, the certificate"
		echo "it uses is not signed by one of the recognized CAs such as"
		echo "Verisign. When you first connect to the Usermin server, your"
		echo "browser will ask you if you want to accept the certificate"
		echo "presented, as it does not recognize the CA. Say yes."
		echo ""
	fi
fi

if [ "$oldwadir" != "$wadir" -a "$upgrading" = 1 -a "$deletedold" != 1 ]; then
	echo "The directory from the previous version of Usermin"
	echo "   $oldwadir"
	echo "Can now be safely deleted to free up disk space, assuming"
	echo "that all third-party modules have been copied to the new"
	echo "version."
	echo ""
fi

