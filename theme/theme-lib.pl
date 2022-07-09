# theme-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();

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

sub list_visible_themes
{
my ($curr) = @_;
my @rv;
my %done;
foreach my $theme (&list_themes()) {
	my $iscurr = $curr && $theme->{'dir'} eq $curr;
	my $lnk = readlink($root_directory."/".$theme->{'dir'});
	next if ($lnk && $lnk !~ /^\// && $lnk !~ /^\.\.\// && !$iscurr);
	next if ($done{$theme->{'desc'}}++ && !$iscurr);
	push(@rv, $theme);
	}
return @rv;
}

1;

