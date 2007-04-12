# theme-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';

# list_themes()
# Returns an array of all installed themes
sub list_themes
{
local (@rv, $o);
opendir(DIR, "..");
foreach $m (readdir(DIR)) {
	local %tinfo;
	next if ($m =~ /^\./);
	next if (!&read_file("../$m/theme.info", \%tinfo));
	next if (!&check_os_support(\%tinfo));
	foreach $o (@lang_order_list) {
		$tinfo{'desc'} = $tinfo{'desc_'.$o} if ($tinfo{'desc_'.$o});
		}
	$tinfo{'dir'} = $m;
	push(@rv, \%tinfo);
	}
closedir(DIR);
return @rv;
}



1;

