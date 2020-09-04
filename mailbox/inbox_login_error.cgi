#!/usr/local/bin/perl
# inbox_login_error.cgi
# Let user update IMAP/POP3 login credentials
use strict;
use warnings;
our (%text, %in);
our ($remote_user, $remote_pass);

require './mailbox-lib.pl';
&ReadParse();

my @folders = &list_folders_sorted();
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;

# Check if this is a POP3 or IMAP inbox with no login set
if ($folder->{'type'} == 2 || $folder->{'type'} == 4) {
	&ui_print_header(undef, &text('error'), undef,
			 undef, undef, 1);
	print &ui_form_start("inbox_login.cgi", "post");
	print &ui_hidden("folder", $folder->{'index'}),"\n";
	print &ui_table_start(
	      $folder->{'type'} == 2 ? $text{'mail_loginheader'}
				     : $text{'mail_loginheader2'}, undef, 2);
	print &ui_table_row(undef, &text('mail_logindesc',
					 "<tt>$folder->{'server'}</tt>"), 2);

	print &ui_table_row($text{'mail_loginuser'},
			    &ui_textbox("user", $remote_user, 30));
	print &ui_table_row($text{'mail_loginpass'},
			    &ui_password("pass", $remote_pass, 30));

	print &ui_table_end();
	print &ui_form_end([ [ "login", $text{'mail_login'} ] ]);
	}
else {
	error(text('mail_unknown'));
}

