# changepass-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
require 'md5-lib.pl';

# check_password(password, username)
# Returns an error message if a password is invalid
sub check_password
{
local ($pass, $username) = @_;
return &text('change_epasswd_min', $config{'passwd_min'})
	if (length($pass) < $config{'passwd_min'});
local $re = $config{'passwd_re'};
return &text('change_epasswd_re', $re)
	if ($re && !eval { $pass =~ /$re/ });
if ($config{'passwd_same'}) {
	return &text('change_epasswd_same')
		if ($pass =~ /\Q$username\E/i);
	}
if ($config{'passwd_new'}) {
	return &text('change_epasswd_new')
		if (lc($pass) eq lc($in{'old'}));
	}
if ($config{'passwd_dict'} && $pass =~ /^[A-Za-z\'\-]+$/) {
	return &text('change_epasswd_dict') if (&is_dictionary_word($pass));
	}
if ($config{'passwd_prog'}) {
        # Run external program with username and password as args
        local $qu = quotemeta($username);
        local $qp = quotemeta($pass);
        local $out = &backquote_command("$config{'passwd_prog'} $qu $qp 2>&1 </dev/null");
        if ($?) {
                return $out;
                }
        }
return undef;
}

# change_mailbox_passwords(user, old, new)
# Change a user's password in Usermin IMAP folders. Returns a message about
# the password change, if done
sub change_mailbox_passwords
{
local ($user, $oldpass, $newpass) = @_;
local $rv;
if ($config{'mailbox'} && &foreign_check("mailbox")) {
	&foreign_require("mailbox", "mailbox-lib.pl");
	foreach my $f (&mailbox::list_folders()) {
		if (($f->{'type'} == 2 || $f->{'type'} == 4) &&
		    ($f->{'user'} eq $user || $f->{'user'} eq '*') &&
		    $f->{'pass'} eq $oldpass &&
		    !$f->{'imapauto'} &&
		    !$f->{'autouser'}) {
			# Found one to change
			local $type = $f->{'type'} == 2 ? "pop3" : "imap";
			local $file;
			if ($f->{'inbox'}) {
				# Need to change special inbox password file
				$file = "$mailbox::user_module_config_directory/inbox";
				$rv = &text('change_inbox', uc($type));
				}
			else {
				# Need to change folder's file
				$file = "$mailbox::user_module_config_directory/$f->{'id'}";
				$rv = &text('change_folder',
					    uc($type), $f->{'server'});
				}
			$file .= ".".$type;
			local %data;
			&read_file($file, \%data);
			$data{'pass'} = $newpass;
			&write_file($file, \%data);
			}
		}
	}
return $rv;
}

# change_samba_password(user, old, new)
# Change a user's Samba password
sub change_samba_password
{
local ($user, $oldpass, $newpass) = @_;
local ($smbpasswd_binary) = split(/\s+/, $config{'smbpasswd'});
local $smbout;
if (&has_command($smbpasswd_binary)) {
	$user = quotemeta($user);
	local $hout = &backquote_command("$config{'smbpasswd'} -h 2>&1");
	if ($hout =~ /\s-s\s/) {
		# New version of smbpasswd which accepts the -s option
		local $temp = &transname();
		open(TEMP, ">$temp");
		if ($config{'smbpasswd'} =~ /\s-r\s/) {
			print TEMP $oldpass,"\n";
			}
		print TEMP $newpass,"\n",$newpass,"\n";
		close(TEMP);
		$smbout = &backquote_command(
			"$config{'smbpasswd'} -s $user 2>&1 <$temp");
		unlink($temp);
		}
	else {
		# Old version of smbpasswd which takes password on command line
		local $pass = quotemeta($newpass);
		$smbout = &backquote_command(
			"$config{'smbpasswd'} $user $pass 2>&1 </dev/null");
		}
	}
return $smbout;
}

1;

