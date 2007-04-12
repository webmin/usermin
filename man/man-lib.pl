# man-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();

$google_host = "www.google.com";
$google_port = 80;
$google_page = "/search";

# Get the paths to perl and perldoc
open(PERL, "$config_directory/perl-path");
chop($perl_path = <PERL>);
close(PERL);
if (&has_command("perldoc")) {
	$perl_doc = "perldoc";
	}
else {
	$perl_path =~ /^(.*)\/[^\/]+$/;
	if (-x "$1/perldoc") {
		$perl_doc = "$1/perldoc";
		}
	}
if ($perl_doc && $] >= 5.006) {
	$perl_doc = "$perl_doc -U";
	}

# set_manpath(extra)
sub set_manpath
{
$ENV{'MANPATH'} = join(":", split(/:/, $config{'man_dir'}),
			    split(/:/, $_[0]));
}

1;

