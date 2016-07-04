#!/usr/local/bin/perl
# Show a page containing all image attachments
use strict;
use warnings;
our (%text, %in);

require './mailbox-lib.pl';

# Get the mail
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];
my $mail = &mailbox_get_mail($folder, $in{'id'}, 0);
$mail || &error($text{'view_egone'});
&parse_mail($mail);
my @sub = split(/\0/, $in{'sub'});
my $subs = join("", map { "&sub=".&urlize($_) } @sub);
foreach my $s (@sub) {
        # We are looking at a mail within a mail ..
	&decrypt_attachments($mail);
        my $amail = &extract_mail($mail->{'attach'}->[$s]->{'data'});
        &parse_mail($amail);
        $mail = $amail;
        }
&decrypt_attachments($mail);

# Find image attachments
my @attach = @{$mail->{'attach'}};
@attach = &remove_body_attachments($mail, \@attach);
@attach = &remove_cid_attachments($mail, \@attach);
my @iattach = grep { $_->{'type'} =~ /^image\// } @attach;

&popup_header($text{'slide_title'});

my $n = 0;
foreach my $a (@iattach) {
	# Navigation links
	print "<hr>" if ($n > 0);
	print "<a name=image$n></a>\n";
	my @links;
	if ($a eq $iattach[0]) {
		push(@links, $text{'slide_prev'});
		}
	else {
		push(@links, "<a href='#image".($n-1)."'>".
			     "$text{'slide_prev'}</a>");
		}
	if ($a eq $iattach[$#iattach]) {
		push(@links, $text{'slide_next'});
		}
	else {
		push(@links, "<a href='#image".($n+1)."'>".
			     "$text{'slide_next'}</a>");
		}
	push(@links, "<b>$a->{'filename'}</b>") if ($a->{'filename'});
	print &ui_links_row(\@links),"<br>\n";

	# Actual image
	print "<img src='detach.cgi?id=".&urlize($in{'id'}).
	      "&folder=$in{'folder'}&attach=$a->{'idx'}$subs'><br>\n";
	$n++;
	}

&popup_footer();
