#!/usr/local/bin/perl
# export.cgi
# Output a key as binary or ascii

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
$key = $keys[$in{'idx'}];

# Work out command-line args
$args = "--armor" if (!$in{'format'});
$cmd = "$gpgpath $args $args --export \"$key->{'name'}->[0]\"";
if ($in{'smode'}) {
	$cmd .= "; $gpgpath $args --export-secret-keys \"$key->{'name'}->[0]\"";
	}

if ($in{'mode'}) {
	# Saving to file
	&error_setup($text{'export_err'});
	if ($in{'to'} !~ /^\//) {
		$in{'to'} = $remote_user_info[7]."/".$in{'to'};
		}
	$in{'to'} || &error($text{'export_efile'});
	if (-d $in{'to'}) {
		$in{'to'} .= "/".($in{'format'} ? "key.gpg" : "key.asc");
		}
	open(OUT, ">$in{'to'}") || &error(&text('efilewrite', $in{'to'}, $!));
	$fh = "OUT";
	}
else {
	# Showing in browser
	if ($in{'format'}) {
		print "Content-type: application/octet-stream\n\n";
		}
	else {
		print "Content-type: text/plain\n\n";
		}
	$fh = "STDOUT";
	}

# Do it
open(GPG, "($cmd) |");
while(<GPG>) {
	print $fh $_;
	}
close(GPG);

if ($in{'mode'}) {
	# Tell the user
	close($fh);
	&ui_print_header(undef, $text{'export_title'}, "");
	print &text('export_done', "<tt>$in{'to'}</tt>"),"<p>\n";
	&ui_print_footer("list_keys.cgi", $text{'keys_return'});
	}

