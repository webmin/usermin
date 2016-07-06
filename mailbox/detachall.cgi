#!/usr/local/bin/perl
# Download all attachments in a ZIP file
use strict;
use warnings;
our (%text, %in);

require './mailbox-lib.pl';
&error_setup($text{'detachall_err'});

&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];
my $mail = &mailbox_get_mail($folder, $in{'id'}, 0);
$mail || &error($text{'view_egone'});
&parse_mail($mail);
my @sub = split(/\0/, $in{'sub'});
foreach my $s (@sub) {
        # We are looking at a mail within a mail ..
	&decrypt_attachments($mail);
        my $amail = &extract_mail($mail->{'attach'}->[$s]->{'data'});
        &parse_mail($amail);
        $mail = $amail;
        }
&decrypt_attachments($mail);

# Save each attachment to a temporary directory
my @attach = @{$mail->{'attach'}};
@attach = &remove_body_attachments($mail, \@attach);
@attach = &remove_cid_attachments($mail, \@attach);
my $temp = &transname();
&make_dir($temp, 0755) || &error(&text('detachall_emkdir', $!));
my $n = 0;
my $fn;
foreach my $a (@attach) {
	# Work out a filename
	if (!$a->{'type'} || $a->{'type'} eq 'message/rfc822') {
		$fn = "mail".(++$n).".txt";
		}
	elsif ($a->{'filename'}) {
		$fn = &decode_mimewords($a->{'filename'});
		}
	else {
		$fn = "file".(++$n).".".&type_to_extension($a->{'type'});
		}

	# Write the file
	no strict "subs";
	&open_tempfile(FILE, ">$temp/$fn", 0, 1);
	&print_tempfile(FILE, $a->{'data'});
	&close_tempfile(FILE);
	use strict "subs";
	}

# Make and output the zip
my $zip = &transname("$$.zip");
my $out = &backquote_command(
	"cd ".quotemeta($temp)." && zip ".quotemeta($zip)." * 2>&1");
if ($?) {
	&error(&text('detachall_ezip', "<tt>".&html_escape($out)."</tt>"));
	}

# Output the ZIP
print "Content-type: application/zip\n\n";
open(my $ZIP, "<", $zip);
my $buf;
while(read($ZIP, $buf, 1024) > 0) {
	print $buf;
	}
close($ZIP);
&unlink_file($zip);
&unlink_file($temp);

&pop3_logout_all();
