#!/usr/local/bin/perl
# detach.cgi
# View one attachment from a message

use Socket;
require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
$folder = &spam_file_folder();
&disable_indexing($folder);

&ReadParse();
@mail = &mailbox::mailbox_list_mails_sorted($in{'idx'}, $in{'idx'}, $folder);
$mail = $mail[$in{'idx'}];
&mailbox::parse_mail($mail);
@sub = split(/\0/, $in{'sub'});
foreach $s (@sub) {
        # We are looking at a mail within a mail ..
	&mailbox::decrypt_attachments($mail);
        local $amail = &mailbox::extract_mail($mail->{'attach'}->[$s]->{'data'});
        &mailbox::parse_mail($amail);
        $mail = $amail;
        }
&mailbox::decrypt_attachments($mail);
$attach = $mail->{'attach'}->[$in{'attach'}];

print "X-no-links: 1\n";
print "Content-type: $attach->{'type'}\n\n";
if ($attach->{'type'} =~ /^text\/html/i) {
	print &filter_javascript($attach->{'data'});
	}
else {
	print $attach->{'data'};
	}

