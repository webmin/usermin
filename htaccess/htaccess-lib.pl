# htaccess-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
do 'apache-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();

$www_root = $userconfig{'www_root'};
$www_root = "$remote_user_info[7]/$www_root" if ($www_root !~ /^\//);

sub get_htaccess_files
{
local @rv;
open(HTACCESS, "$user_module_config_directory/htlist");
while(<HTACCESS>) {
	s/\r|\n//g;
	push(@rv, $_) if (-r $_);
	}
close(HTACCESS);
return @rv;
}

sub set_htaccess_files
{
local $f;
&open_tempfile(HTACCESS, ">$user_module_config_directory/htlist");
foreach $f (@_) {
	&print_tempfile(HTACCESS, $f,"\n");
	}
&close_tempfile(HTACCESS);
}

1;

