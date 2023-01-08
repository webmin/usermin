#!/usr/local/bin/perl
# edit_sig.cgi
# Display the user's .signature file for editing
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text);

require './mailbox-lib.pl';
my $sf = &get_signature_file();
$sf ||= ".signature";
&ui_print_header(undef, $text{'sig_title'}, "");

print &text('sig_desc', "<tt>$sf</tt>"),"<p>\n";
print &ui_form_start("save_sig.cgi", "form-data");
print &ui_textarea("sig", &get_signature(), 5, 80);
print &ui_form_end([ [ undef, $text{'save'} ] ]);

&ui_print_footer("", $text{'mail_return'});
