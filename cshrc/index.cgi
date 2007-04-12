#!/usr/local/bin/perl
# index.cgi
# Display user's .cshrc or .profile file

require './cshrc-lib.pl';
&ui_print_header(undef, $text{'index_title'}, undef, undef, 0, 1);

$i = 0;
foreach $cshrc_file (@cshrc_files) {
	print "<hr>\n" if ($i);
	print &text('index_desc_'.$cshrc_types[$i],
		    "<tt>$cshrc_file</tt>"),"<br>\n";
	print "<form action=save_cshrc.cgi method=post ",
	      "enctype=multipart/form-data>\n";
	print "<input type=hidden name=idx value='$i'>\n";
	print "<textarea name=cshrc rows=20 cols=70>";
	open(CSHRC, $cshrc_file);
	while(<CSHRC>) { print; }
	close(CSHRC);
	print "</textarea><br>\n";
	print "<input type=submit value='$text{'save'}'></form>\n";
	$i++;
	}
 
&ui_print_footer("/", $text{'index'});

