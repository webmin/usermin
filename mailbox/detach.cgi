#!/usr/local/bin/perl
# detach.cgi
# View one attachment from a message
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);

use Socket;
require './mailbox-lib.pl';

&ReadParse();
my @folders = &list_folders_sorted();
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
$folder || &error($text{'view_efolder'});
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
my $attach = $mail->{'attach'}->[$in{'attach'}];

if ($in{'scale'}) {
	# Scale the gif or jpeg image to 48 pixels high
	my $temp = &transname();
	open(my $TEMP, ">", "$temp");
	print $TEMP $attach->{'data'};
	close($TEMP);
	$SIG{'CHLD'} = sub { wait; };
	my ($pnmin, $pnmout);
	if ($attach->{'type'} eq 'image/gif') {
		($pnmin, $pnmout) = &pipeopen("giftopnm $temp");
		}
	elsif ($attach->{'type'} eq 'image/jpeg') {
		($pnmin, $pnmout) = &pipeopen("djpeg -fast $temp");
		}
	else {
		&dump_erroricon();
		}
	close($pnmin);
	my $type = <$pnmout>;
	my $size = <$pnmout>;
	unlink($temp);
	$type =~ /^P[0-9]/ || &dump_erroricon();
	$size =~ /(\d+)\s+(\d+)/ || &dump_erroricon();
	my ($w, $h) = ($1, $2);
	my $scale;
	if ($w > 48) {
		$scale = 48.0 / $w;
		}
	else {
		$scale = 48.0 / $h;
		}
	my ($jpegin, $jpegout) = &pipeopen("pnmscale $scale 2>/dev/null | cjpeg");
	print $jpegin $type;
	print $jpegin $size;
	my $buf;
	while(read($pnmout, $buf, 1024)) {
		print $jpegin $buf;
		}
	close($jpegin);
	close($pnmout);
	print "Content-type: image/jpeg\n\n";
	while(read($jpegout, $buf, 1024)) {
		print $buf;
		}
	close($jpegout);
	}
else {
	# Just output the attachment
	print "X-no-links: 1\n";
	if ($in{'type'}) {
		# Display as a specific MIME type
		print "Content-type: $in{'type'}\n\n";
		print $attach->{'data'};
		}
	else {
		# Auto-detect type
		if ($in{'save'}) {
			# Force download
			print "Content-Disposition: Attachment; filename=\"$attach->{'filename'}\"\n";
			}
		if ($attach->{'type'} eq 'message/delivery-status') {
			print "Content-type: text/plain\n\n";
			}
		else {
			print "Content-type: $attach->{'type'}\n\n";
			}
		if ($attach->{'type'} =~ /^text\/html/i && !$in{'save'}) {
			print &safe_urls(&filter_javascript($attach->{'data'}));
			}
		else {
			print $attach->{'data'};
			}
		}
	}
&pop3_logout_all();

sub dump_erroricon
{
print "Content-type: image/gif\n\n";
open(my $ICON, "<", "images/error.gif");
while(<$ICON>) { print; }
close($ICON);
exit;
}

# pipeopen(command)
my $pipe;
sub pipeopen
{
$pipe++;
my $inr = "INr$pipe";
my $inw = "INw$pipe";
my $outr = "OUTr$pipe";
my $outw = "OUTw$pipe";
pipe($inr, $inw);
pipe($outr, $outw);
if (!fork()) {
	untie(*STDIN);
	untie(*STDOUT);
	open(STDIN, "<", "&$inr");
	open(STDOUT, ">", "&$outw");
	close($inw);
	close($outr);
	exec($_[0]) || print STDERR "exec failed : $!\n";
	exit 1;
	}
close($inr);
close($outw);
return ($inw, $outr);
}
