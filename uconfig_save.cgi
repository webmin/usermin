#!/usr/local/bin/perl
# Save the logged-in Unix user's preferences for one module.

BEGIN { push(@INC, "."); };
use WebminCore;
require './config-lib.pl';
&init_config();
if ($ENV{'CONTENT_TYPE'} =~ m!^multipart/form-data\b!i) {
	&ReadParseMime();
	}
else {
	&ReadParse();
	}
&error_setup($text{'config_err'});

my $m = $in{'module'};
my (undef, undef, $fields, $canconfig, $custom) = &user_config_editor($m);
my @sections = @{$fields->{'sections'}};
my $section = $in{'section'};
my $next;
if (@sections > 1 || length($section)) {
	# A missing or stale section must not turn a partial save into a full save.
	my $idx = &indexof($section, map { $_->[0] } @sections);
	$idx >= 0 || &error($text{'config_esection'});
	$next = $sections[($idx + 1) % @sections]->[0];
	}

# Merge the submitted page into the user's current file under lock.
my $file = "$user_config_directory/$m/config";
mkdir("$user_config_directory/$m", 0700);
&lock_file($file);
my %prefs;
&read_file($file, \%prefs);
my %oldprefs = %prefs;
if ($custom) {
	# Older editors read the submitted inputs from their module's own hash.
	(my $pkg = $m) =~ tr/-/_/;
	%{$pkg."::in"} = %in;
	&foreign_call($m, "config_save", \%prefs, $canconfig);
	}
else {
	&parse_config(\%prefs, $fields, $m, %$canconfig ? $canconfig : undef,
		      $section);
	}
&write_file($file, \%prefs);
&unlock_file($file);

if (&foreign_defined($m, 'config_post_save')) {
	&foreign_call($m, "config_post_save", \%prefs, \%oldprefs, $canconfig);
	}
if ($in{'save_next'} && defined($next)) {
	&redirect("uconfig.cgi?module=".&urlize($m)."&section=".&urlize($next));
	}
else {
	&redirect("/$m/");
	}
