#!/usr/local/bin/perl
# Send a forgotten password reset email via Webmin

BEGIN { push(@INC, "."); };
use WebminCore;
$no_acl_check++;
&init_config();
&ReadParse();
&load_theme_library();

# Bail out if the request is not a valid XMLHttpRequest
if ($ENV{'HTTP_X_REQUESTED_WITH'} ne 'XMLHttpRequest') {
	&redirect(get_referer_relative());
	return;
	}

# Check if we have Webmin installed
my $wdir = $config_directory;
$wdir =~ s/\/usermin$/\/webmin/;
my $wconfig = "$wdir/config";
my $wminiserv = "$wdir/miniserv.conf";
my (%wconfig, %wminiserv);
if (&read_env_file($wconfig, \%wconfig) &&
    &read_env_file($wminiserv, \%wminiserv) && $wconfig{'forgot_pass'}) {
	# Make a request to the Webmin server
	my ($host) = split(/:/, $ENV{'HTTP_HOST'});
	my $port = $wminiserv{'port'};
	my $url = $wminiserv{'ssl'} ? "https" : "http";
	$url .= "://$host";
	if ($port != 80 && $port != 443) {
		$url .= ":$port";
		}
	$url .= $wminiserv{'webprefix'} if ($wminiserv{'webprefix'});
	my ($out, $err);
	my $custom_headers = {
		'Content-Type' => 'application/x-www-form-urlencoded',
		'X-Requested-With' => 'XMLHttpRequest',
	};
	&http_post($host, $port, "$wminiserv{'webprefix'}/forgot_send.cgi",
		   ("forgot=".
		   	&urlize($in{'forgot'}).
		    "&return=".
		   	&urlize($url).
		    "&product=".
		   	&get_product_name()), \$out, \$err, undef,
		   $wminiserv{'ssl'}, undef, undef, 15, 0, 1, $custom_headers);
	print "Content-type: text/plain\n\n";
	if ($err) {
		&error_stderr($err);
		print "Remote Error: $text{'forgot_eremote'}\n";
		}
	else {
		print $out;
		}
	}
else {
	print "Content-type: text/plain\n\n";
	print "Remote Error: $text{'forgot_eremote'}\n";
	}
