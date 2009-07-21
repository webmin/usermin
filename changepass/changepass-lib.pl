# changepass-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
require 'md5-lib.pl';

# check_password(password, username)
sub check_password
{
return &text('change_epasswd_min', $config{'passwd_min'})
	if (length($_[0]) < $config{'passwd_min'});
local $re = $config{'passwd_re'};
return &text('change_epasswd_re', $re)
	if ($re && !eval { $_[0] =~ /$re/ });
if ($config{'passwd_same'}) {
	return &text('change_epasswd_same')
		if ($_[0] =~ /\Q$_[1]\E/i);
	}
if ($config{'passwd_new'}) {
	return &text('change_epasswd_new')
		if (lc($_[0]) eq lc($in{'old'}));
	}
if ($config{'passwd_dict'} && $_[0] =~ /^[A-Za-z\'\-]+$/ &&
    (&has_command("ispell") || &has_command("spell"))) {
	local $temp = &transname();
	open(TEMP, ">$temp");
	print TEMP $_[0],"\n";
	close(TEMP);
	if (&has_command("ispell")) {
		open(SPELL, "ispell -a <$temp |");
		while(<SPELL>) {
			if (/^(\#|\&|\?)/) {
				$unknown++;
				}
			}
		close(SPELL);
		}
	else {
		open(SPELL, "spell <$temp |");
		local $line = <SPELL>;
		$unknown++ if ($line);
		close(SPELL);
		}
	unlink($temp);
	return &text('change_epasswd_dict') if (!$unknown);
	}
if ($config{'passwd_prog'}) {
        # Run external program with username and password as args
        local $qu = quotemeta($_[1]);
        local $qp = quotemeta($_[0]);
        local $out = `$config{'passwd_prog'} $qu $qp 2>&1 </dev/null`;
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
		    $f->{'user'} eq $user &&
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

1;

