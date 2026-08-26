#!/usr/local/bin/perl
# save_sig.cgi
# Update the user's signature file
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %userconfig);

require './mailbox-lib.pl';
require '../html-editor-lib.pl';
if ($userconfig{'sig_file'} eq '*') {
	# Switch to ~/.signature
	$userconfig{'sig_file'} = '.signature';
	&save_user_module_config();
	}
my $sf = &get_signature_file();
$sf || &error($text{'sig_enone'});
&ReadParseMime();

$in{'sig'} =~ s/\r//g;
if ($in{'html_edit'}) {
	# Convert editor CSS classes to inline styles, and drop the
	# editor's own stylesheet block from the stored signature
	$in{'sig'} = &html_editor_substitute_classes_with_styles($in{'sig'});
	$in{'sig'} =~ s/<style\s+data-iframe-mode[^>]*>.*?<\/style>//gis;

	# Drop the single trailing line break appended by the editor
	$in{'sig'} =~ s/<br\s*\/?>\s*$//i;

	# Treat a signature with no actual text or images as empty
	my $check = $in{'sig'};
	$check =~ s/<[^>]+>//g;
	$check =~ s/&nbsp;|\s+//g;
	$in{'sig'} = '' if ($check eq '' && $in{'sig'} !~ /<img[^>]*>/i);
	}
$in{'sig'} =~ s/\n*$/\n/;
no strict "subs";
&open_tempfile(SIG, ">$sf") || &error(&text('sig_eopen', $!));
&print_tempfile(SIG, $in{'sig'});
&close_tempfile(SIG);
use strict "subs";
&redirect("");
