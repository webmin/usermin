#!/usr/local/bin/perl
# edit_alias.cgi
# Edit an existing .forward entry

require './forward-lib.pl';
&ReadParse();
if (!$in{'new'}) {
	if ($in{'file'}) {
		$a = &get_dotqmail($in{'file'});
		}
	else {
		@aliases = &list_aliases();
		$a = $aliases[$in{'num'}];
		}
 	&alias_form($text{'aform_edit'}, $a);
	}
else {
	&alias_form($text{'aform_create'}, $a);
	}
