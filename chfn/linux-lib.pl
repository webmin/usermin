# linux-lib.pl
# Functions for changing user details on linux

# change_details(realname, office, ophone, hphone, shell)
sub change_details
{
foreach $a (@_) {
	$a =~ s/\\//g;
	$a =~ s/'//g;
	}

# What version of chfn are we running?
local @ruser = getpwnam($remote_user);
local @uinfo = split(/,/, $ruser[6]);
local $out = `chfn -v 2>&1`;
local $cmd;
if ($out =~ /pwdutils/i || ($out =~ /-r/ && $out =~ /-w/ && $out =~ /-h/)) {
	# Change details using chfn from pwdutils syntax
	$cmd = "chfn -f ".quotemeta($_[0]);
	$cmd .= " -r ".quotemeta($_[1]) if ($_[1] || $uinfo[1]);
	$cmd .= " -w ".quotemeta($_[2]) if ($_[2] || $uinfo[2]);
	$cmd .= " -h ".quotemeta($_[3]) if ($_[3] || $uinfo[3]);
	$cmd .= " ".quotemeta($remote_user);
	}
else {
	# Change details using chfn from util-linux syntax
	$cmd = "chfn -f ".quotemeta($_[0]);
	$cmd .= " -o ".quotemeta($_[1]) if ($_[1] || $uinfo[1]);
	$cmd .= " -p ".quotemeta($_[2]) if ($_[2] || $uinfo[2]);
	$cmd .= " -h ".quotemeta($_[3]) if ($_[3] || $uinfo[3]);
	$cmd .= " ".quotemeta($remote_user);
	}
local $out = `$cmd 2>&1`;
return $out if ($?);

# Change shell
if ($ruser[8] ne $_[4]) {
	$cmd = "chsh -s ".quotemeta($_[4])." ".quotemeta($remote_user);
	$out = `$cmd 2>&1`;
	return $? ? $out : undef;
	}
return undef;
}

1;

