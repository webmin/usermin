#!/usr/local/bin/perl
# Show a form for enabling two-factor authentication

use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
require './twofactor-lib.pl';
our (%in, %text, $remote_user);
&ui_print_header(undef, $text{'index_title'}, "");

# Is it even enabled?
my %miniserv;
&get_miniserv_config(\%miniserv);
if (!$miniserv{'twofactor_provider'}) {
	print $text{'twofactor_setup'},"<p>\n";
	&ui_print_footer("/", $text{'index'});
	return;
	}

# Get the user's current state
my ($provid, $id, $api) = &get_user_twofactor($remote_user, \%miniserv);

print &ui_form_start("enable.cgi", "post");
my @buts;
if ($id) {
	@buts = ( [ "disable", $text{'twofactor_disable'} ] );
	my ($prov) = grep { $_->[0] eq $provid }
		       &list_twofactor_providers();
	print &text('twofactor_already2',
		    "<i>$prov->[1]</i>",
		    "<tt>$id</tt>",
		    "<tt>$remote_user</tt>"),"<p>\n";
	}
else {
	my ($prov) = grep { $_->[0] eq $miniserv{'twofactor_provider'} }
		       &list_twofactor_providers();
	print &text('twofactor_desc2',
		    "<i>$prov->[1]</i>",
		    $prov->[2],
		    "<tt>$remote_user</tt>"),"<p>\n";
	my $ffunc = "show_twofactor_form_".
		    $miniserv{'twofactor_provider'};
	if (defined(&$ffunc)) {
		print &ui_table_start($text{'twofactor_header'}, undef, 2);
		print &{\&{$ffunc}}($remote_user);
		print &ui_table_end();
		}
	@buts = ( [ "enable", $text{'twofactor_enable'} ] );
	}
print &ui_form_end(\@buts);

&ui_print_footer("/", $text{'index'});

