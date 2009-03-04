#!/usr/local/bin/perl
# Display a message for printing

$trust_unknown_referers = 1;
require './mailbox-lib.pl';
&ReadParse();

# Get the folder
&set_module_index($in{'folder'});
@folders = &list_folders();
$folder = $folders[$in{'folder'}];

# Get the mail
$mail = &mailbox_get_mail($folder, $in{'id'}, 0);
$mail || &error($text{'view_egone'});
&parse_mail($mail);
foreach $s (split(/\0/, $in{'sub'})) {
	&decrypt_attachments($mail);
	local $amail = &extract_mail(
			$mail->{'attach'}->[$s]->{'data'});
	&parse_mail($amail);
	$mail = $amail;
	}
&decrypt_attachments($mail);
($textbody, $htmlbody, $body) = &find_body($mail, $userconfig{'view_html'});

# Show it
&ui_print_header(undef, &decode_mimewords($mail->{'header'}->{'subject'}));
&show_mail_printable($mail, $body, $textbody, $htmlbody);
print "<script>window.print();</script>\n";
&ui_print_footer();
