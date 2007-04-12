#!/usr/local/bin/perl
# edit_afile.cgi
# Display the contents of an address file

require './forward-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'afile_title'}, "");
$in{'vfile'} = &make_absolute($in{'vfile'});
open(FILE, $in{'file'});
@lines = <FILE>;
close(FILE);

print "<b>",&text('afile_desc', "<tt>$in{'vfile'}</tt>"),"</b><p>\n";

print "<form action=save_afile.cgi method=post enctype=multipart/form-data>\n";
print &ui_hidden("file", $in{'file'}),"\n";
print &ui_hidden("num", $in{'num'}),"\n";
print &ui_hidden("vfile", $in{'vfile'}),"\n";
print "<textarea name=text rows=20 cols=80>",
	join("", @lines),"</textarea><p>\n";
print "<input type=submit value=\"$text{'save'}\"> ",
      "<input type=reset value=\"$text{'afile_undo'}\">\n";
print "</form>\n";

&ui_print_footer("edit_alias.cgi?num=$in{'num'}&file=$in{'file'}",
		 $text{'aform_return'});

