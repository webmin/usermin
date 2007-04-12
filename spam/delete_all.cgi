#!/usr/local/bin/perl
# delete_all.cgi
# Delete all spam messages

require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
$folder = &spam_file_folder();
&disable_indexing($folder);
&mailbox::mailbox_empty_folder($folder);
&redirect("mail.cgi");

