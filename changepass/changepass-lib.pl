# changepass-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
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

1;

