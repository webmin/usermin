#!/usr/local/bin/perl
# changepass.cgi
# Change the user's password now, using PAM and the passwd service

require './changepass-lib.pl';
&error_setup($text{'change_err'});
&ReadParse();

# Validate inputs
$in{'new1'} ne '' || &error($text{'change_enew1'});
$in{'new1'} eq $in{'new2'} || &error($text{'change_enew2'});

# Make sure minimum length and other restrictions are met
$err = &check_password($in{'new1'}, $remote_user);
&error($err) if ($err);

eval "use Authen::PAM";
$has_pam++ if (!$@);
$@ = undef;

if ($config{'passwd_cmd'} eq 'file') {
	# Directly update shadow file to do the change

	# Read shadow file and find user
	&get_miniserv_config(\%miniserv);
	&lock_file($miniserv{'passwd_file'});
	$lref = &read_file_lines($miniserv{'passwd_file'});
	for($i=0; $i<@$lref; $i++) {
		@line = split(/:/, $lref->[$i], -1);
		local $u = $line[$miniserv{'passwd_uindex'}];
		if ($u eq $remote_user) {
			$idx = $i;
			last;
			}
		}
	defined($idx) || &error($text{'change_euser'});

	# Work out password encryption type
	if ($config{'md5'} && !&check_md5()) {
		$type = 1;
		}
	else {
		$type = 0;
		}

	# Validate old password
	$oldpass = $line[$miniserv{'passwd_pindex'}];
	&validate_password($in{'old'}, $oldpass) ||
		&error($text{'change_eold'});

	# Set new password and save file
	if ($type == 0) {
		# Do Unix encryption
		$salt = chr(int(rand(26))+65) . chr(int(rand(26))+65);
		$line[$miniserv{'passwd_pindex'}] = &unix_crypt($in{'new1'},
								$salt);
		}
	else {
		# Do MD5 encryption
		$line[$miniserv{'passwd_pindex'}] = &encrypt_md5($in{'new1'});
		}
	if ($miniserv{'passwd_cindex'} ne '') {
		$days = int(time()/(24*60*60));
		$line[$miniserv{'passwd_cindex'}] = $days;
		}
	$lref->[$idx] = join(":", @line);
	&flush_file_lines();
	&unlock_file($miniserv{'passwd_file'});
	}
elsif ($config{'passwd_cmd'} || !$has_pam) {
	# Call passwd program to do the change
	if ($config{'passwd_cmd'}) {
		$passwd_cmd = $config{'passwd_cmd'};
		}
	else {
		$passwd_cmd = &has_command("passwd");
		$passwd_cmd ||
			&error(&text('change_epasswd', "<tt>passwd</tt>"));
		}
	&foreign_require("proc", "proc-lib.pl");
	&clean_environment();
	$ENV{'REMOTE_USER'} = $remote_user;	# some programs need this
	if ($config{'cmd_mode'} == 0) {
		# Command is run as the user
		$ENV{'USER'} = $ENV{'LOGNAME'} = $remote_user;
		@uinfo = getpwnam($remote_user);
		$ENV{'HOME'} = $uinfo[7];
		chdir($uinfo[7]);
		($fh, $fpid) = &proc::pty_process_exec(
					$passwd_cmd, $uinfo[2], $uinfo[3]);
		chdir($module_root_directory);
		}
	else {
		# Command is being run as root
		$passwd_cmd .= " ".quotemeta($remote_user);
		($fh, $fpid) = &proc::pty_process_exec($passwd_cmd, 0, 0);
		}
	&reset_environment();
	while(1) {
		local $rv = &wait_for($fh,
			   '(new|re-enter).*:',
			   '(old|current|login).*:',
			   'pick a password',
			   'too\s+many\s+failures',
			   'attributes\s+changed\s+on|successfully\s+changed',
			   'pick your passwords');
		$out .= $wait_for_input;
		sleep(1);
		if ($rv == 0) {
			# Prompt for the new password
			syswrite($fh, $in{'new1'}."\n", length($in{'new1'})+1);
			}
		elsif ($rv == 1) {
			# Prompt for the old password
			syswrite($fh, $in{'old'}."\n", length($in{'old'})+1);
			}
		elsif ($rv == 2) {
			# Request for a menu option (SCO?)
			syswrite($fh, "1\n", 2);
			}
		elsif ($rv == 3) {
			# Failed too many times
			last;
			}
		elsif ($rv == 4) {
			# All done
			last;
			}
		elsif ($rv == 5) {
			# Request for a menu option (HP/UX)
			syswrite($fh, "p\n", 2);
			}
		else {
			last;
			}
		last if (++$count > 10);
		}
	$crv = close($fh);
	sleep(1);
	waitpid($fpid, 1);
	$oldstars = ("*" x length($in{'old'}));
	$newstars = ("*" x length($in{'new1'}));
	$out =~ s/\Q$in{'old'}\E/$oldstars/g;
	$out =~ s/\Q$in{'new1'}\E/$newstars/g;
	&error(&text('change_ecmd', "<tt>$passwd_cmd</tt>", "<pre>$out</pre>"))
		if ($? || $count > 10 ||
		    $out =~ /error|failed/i ||
		    $out =~ /bad\s+password/i && !$config{'cmd_mode'});
	}
else {
	# Use PAM to make the change..
	# Check if the old password is correct
	&get_miniserv_config(\%miniserv);
	@uinfo = getpwnam($remote_user);
	$service = $miniserv{'pam'} ? $miniserv{'pam'} : "webmin";
	$pamh = new Authen::PAM($service, $remote_user, \&pam_check_func);
	$rv = $pamh->pam_authenticate();
	$rv == PAM_SUCCESS || &error($text{'change_eold'});
	$pamh = undef;

	# Change the password with PAM, in a sub-process. This is needed because
	# the UID must be changed to properly signal to the PAM libraries that
	# the password change is not being done by the root user.
	$temp = &transname();
	$pid = fork();
	if (!$pid) {
		($>, $<) = (0, $uinfo[2]);
		$pamh = new Authen::PAM("passwd", $remote_user, \&pam_change_func);
		$rv = $pamh->pam_chauthtok();
		open(TEMP, ">$temp");
		print TEMP "$rv\n";
		print TEMP ($messages || $pamh->pam_strerror($rv)),"\n";
		close(TEMP);
		exit(0);
		}
	waitpid($pid, 0);
	open(TEMP, $temp);
	chop($rv = <TEMP>);
	chop($messages = <TEMP>);
	close(TEMP);
	unlink($temp);
	$rv == PAM_SUCCESS || &error(&text('change_epam2', $messages));
	}

# Run any post-change command. This must be done before the calls to the
# MySQL and mailboxes module, while we are still root.
if ($config{'post_command'}) {
	$ENV{'CHANGEPASS_USER'} = $remote_user;
	$ENV{'CHANGEPASS_PASS'} = $in{'new1'};
	system("($config{'post_command'}) >/dev/null 2>&1 </dev/null");
	}

# Change samba password as well
($smbpasswd_binary) = split(/\s+/, $config{'smbpasswd'});
if (&has_command($smbpasswd_binary)) {
	local $user = quotemeta($remote_user);
	local $hout = `$config{'smbpasswd'} -h 2>&1`;
	if ($hout =~ /\s-s\s/) {
		# New version of smbpasswd which accepts the -s option
		local $temp = &transname();
		open(TEMP, ">$temp");
		print TEMP $in{'new1'},"\n",$in{'new1'},"\n";
		close(TEMP);
		$smbout = `$config{'smbpasswd'} -s $user 2>&1 <$temp`;
		unlink($temp);
		}
	else {
		# Old version of smbpasswd which takes password on command line
		local $pass = quotemeta($in{'new1'});
		$smbout = `$config{'smbpasswd'} $user $pass 2>&1 </dev/null`;
		}
	}

# Change MySQL password too, if possible
if ($config{'mysql'} && &foreign_check("mysql")) {
	&foreign_require("mysql", "mysql-lib.pl");
	$myr = &mysql::is_mysql_running();
	if ($myr == 1) {
		# Running and can login .. change it
		($db) = grep { &mysql::can_edit_db($_) }
			     &mysql::list_databases();
		$db ||= "mysql";
		local $main::error_must_die = 1;
		eval {
			$mypass = $in{'new1'};
			$mypass =~ s/'/''/g;
			&mysql::execute_sql($db,
				"set password = password('$mypass')");
			};
		if ($@) {
			$mysql_error = $@;
			}
		else {
			# Worked! Save in MySQL config too
			$mysql_ok = 1;
			$mysql::userconfig{'pass'} = $in{'new1'};
			&mysql::save_user_module_config(
				\&mysql::userconfig, "mysql");
			}
		}
	elsif ($myr == -1) {
		# Running but cannot login
		$mysql_error = $text{'change_emysql'};
		}
	}

# Change matching stored POP3 passwords in read mail module
$msg = &change_mailbox_passwords($remote_user, $in{'old'}, $in{'new1'});
push(@pc, $msg) if ($msg);

&ui_print_header(undef, $text{'change_title'}, "");

print "<p>",&text('change_ok', "<tt>$remote_user</tt>"),"<p>\n";
if ($smbout =~ /changed/) {
	print "<p>",&text('change_samba'),"<p>\n";
	}
elsif ($smbout) {
	print "<p>",&text('change_samba2', "<pre>$smbout</pre>"),"<p>\n";
	}
if ($mysql_ok) {
	print "<p>",&text('change_mysql'),"<p>\n";
	}
elsif ($mysql_error) {
	print "<p>",&text('change_mysql2', $mysql_error),"<p>\n";
	}
foreach $pc (@pc) {
	print "$pc<br>\n";
	}
print "<p>\n" if (@pc);

&ui_print_footer("", $text{'index_return'});

sub pam_check_func
{
my @res;
while ( @_ ) {
	my $code = shift;
	my $msg = shift;
	my $ans = "";

	$ans = $remote_user if ($code == PAM_PROMPT_ECHO_ON());
	$ans = $in{'old'} if ($code == PAM_PROMPT_ECHO_OFF());

	push @res, PAM_SUCCESS();
	push @res, $ans;
	}
push @res, PAM_SUCCESS();
return @res;
}

sub pam_change_func
{
my @res;
while ( @_ ) {
	my $code = shift;
	my $msg = shift;
	my $ans = "";
	$messages = $msg;

	if ($code == PAM_PROMPT_ECHO_ON()) {
		# Assume asking for username
		push @res, PAM_SUCCESS();
		push @res, $remote_user;
		}
	elsif ($code == PAM_PROMPT_ECHO_OFF()) {
		# Assume asking for a password (old first, then new)
		push @res, PAM_SUCCESS();
		if ($msg =~ /old|current|login/i) {
			push @res, $in{'old'};
			}
		else {
			push @res, $in{'new1'};
			}
		}
	else {
		# Some message .. ignore it
		push @res, PAM_SUCCESS();
		push @res, undef;
		}
	}
push @res, PAM_SUCCESS();
return @res;
}

