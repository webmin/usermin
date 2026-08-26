#!/usr/local/bin/perl
# edit_sig.cgi
# Display the user's .signature file for editing
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %userconfig);

require './mailbox-lib.pl';
require '../html-editor-lib.pl';
my $sf = &get_signature_file();
$sf ||= ".signature";
my $sig = &get_signature();
my $sig_html = &signature_is_html($sig);

# Use the HTML editor if composing email in HTML format is enabled
my $html_edit = $userconfig{'html_edit'} ? 1 : 0;
&ui_print_header(undef, $text{'sig_title'}, "");

print &text('sig_desc', "<tt>$sf</tt>"),"<p>\n";
print &ui_form_start("save_sig.cgi", "form-data");
if ($html_edit) {
	# Show WYSIWYG HTML editor with hidden textarea holding the content
	if ($sig && !$sig_html) {
		$sig = &html_escape($sig);
		$sig =~ s/\n/<br>\n/g;
		}
	my $editor_mode = $userconfig{'html_edit_mode'} || 'simple';
	my $html_editor = &html_editor(
	      { textarea =>
	          { target => { name => 'sig', attr => 'name' } },
	        type => $editor_mode,
	        storage => 'quill=last-signature',
	      });
	print &ui_textarea("sig", $sig, 5, 80, undef, 0,
		"style='display: none' id=sig data-html-mode='$editor_mode'").
	      $html_editor;
	}
else {
	# Show plain text editing area
	$sig = &html_to_text($sig) if ($sig_html);
	print &ui_textarea("sig", $sig, 5, 80);
	}
print &ui_hidden("html_edit", $html_edit);
print &ui_form_end([ [ undef, $text{'save'} ] ]);

&ui_print_footer("", $text{'mail_return'});
