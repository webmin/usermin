#!/usr/local/bin/perl
# Validate the OTP for some Usermin user

$main::no_acl_check = 1;
$main::no_referers_check = 1;
$ENV{'WEBMIN_CONFIG'} = "/etc/usermin";
$ENV{'WEBMIN_VAR'} = "/var/usermin";
if ($0 =~ /^(.*\/)[^\/]+$/) {
        chdir($1);
        }
require './twofactor-lib.pl';
$module_name eq 'twofactor' || die "Command must be run with full path";

# Check command-line args
@ARGV == 5 || die "Usage: $0 user provider id token api-key";
($user, $provider, $id, $token, $apikey) = @ARGV;

# Call the provider validation function
$func = "validate_twofactor_".$provider;
$err = &$func($id, $token, $apikey);
if ($err) {
	$err =~ s/\r|\n/ /g;
	print $err,"\n";
	exit(1);
	}
else {
	exit(0);
	}
