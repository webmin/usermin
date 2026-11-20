#!/usr/local/bin/perl
# Edit a Usermin module's preferences for the logged-in Unix user.

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

my $m = $in{'module'} || $ARGV[0];
my ($info, $dir, $fields, $canconfig, $custom) = &user_config_editor($m);
my $help = -r &help_file($m, "config_intro") ? [ "config_intro", $m ] : undef;
&ui_print_header(&text('config_dir', $info->{'desc'}), $text{'config_title'},
		 "", $help, 0, 1);
my ($section, $title, $next) =
	&config_section_navigation("uconfig.cgi", $m, $fields);
$title = &text('config_header', $info->{'desc'}) if (!defined($section));

# Personal settings override the module and administrator defaults.
my %prefs;
&read_file("$dir/defaultuconfig", \%prefs);
&read_file("$config_directory/$m/uconfig", \%prefs);
&read_file("$user_config_directory/$m/config", \%prefs);

print &ui_form_start("uconfig_save.cgi", "post"), &ui_hidden("module", $m);
if (defined($section)) {
	print &ui_hidden("section", $section), &ui_hidden("section_next", $next);
	}
print &ui_table_start($title, "width=100%", 2);
if ($custom) {
	# Legacy callbacks read the selected section from their own %in.
	(my $pkg = $m) =~ tr/-/_/;
	%{$pkg."::in"} = %in;
	&foreign_call($m, "config_form", \%prefs, $canconfig);
	}
else {
	&generate_config(\%prefs, $fields, $m, %$canconfig ? $canconfig : undef,
			 undef, $section);
	}
print &ui_table_end();
my @buttons = ( [ "save", $text{'save'} ] );
push(@buttons, [ "save_next", $text{'config_next'} ]) if (defined($section));
print &ui_form_end(\@buttons);
my %mtext = &load_language($m);
&ui_print_footer("/$m/", $mtext{'index_return'} || $text{'index'});
