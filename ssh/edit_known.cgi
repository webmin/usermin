#!/usr/local/bin/perl
# edit_known.cgi
# Edit or create a known host

require './ssh-lib.pl';
&ReadParse();
if ($in{'new'}) {
	&ui_print_header(undef, $text{'known_create'}, "");
	$msg = $text{'known_desc1'};
	}
else {
	&ui_print_header(undef, $text{'known_edit'}, "");
	@knowns = &list_knowns();
	$known = $knowns[$in{'idx'}];
	}

# Show main key details
print "$msg<p>\n" if ($msg);
print "<form action=save_known.cgi>\n";
print "<input type=hidden name=idx value='$in{'idx'}'>\n";
print "<input type=hidden name=new value='$in{'new'}'>\n";
print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'known_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table width=100%>\n";

if (!$known->{'hash'}) {
	print "<tr> <td valign=top><b>$text{'known_hosts'}</b></td>\n";
	print "<td colspan=3>";
	print "<textarea name=hosts rows=3 cols=50>",
		join("\n", @{$known->{'hosts'}}),
		"</textarea></td> </tr>\n";
	}
else {
	print "<tr> <td valign=top><b>$text{'known_salt'}</b></td>\n";
	print "<td colspan=3>";
	printf "<input name=salt readonly size=30 value='%s'>",
		$known->{'salt'},
		"</input></td> </tr>\n";
	print "<tr> <td valign=top><b>$text{'known_hash'}</b></td>\n";
	print "<td colspan=3>";
	printf "<input name=hash readonly size=30 value='%s'>",
		$known->{'hash'},
		"</textarea></td> </tr>\n";
}

if (($known->{'type'} eq 'ssh-rsa1') or $in{'new'}) {
	print "<tr> <td><b>$text{'known_bits'}</b></td>\n";
	printf "<td><input name=bits size=5 value='%s'></td>\n",
		$known->{'bits'};

	print "<tr> <td><b>$text{'known_exp'}</b></td>\n";
	printf "<td><input name=exp size=5 value='%s'></td> </tr>\n",
		$known->{'exp'};
	}
	
if ($known->{'type'} eq 'ssh-rsa1') {
	printf "<input type=hidden name=type value='%s'>\n", 
		$known->{'type'};
	}

if ($in{'new'}) {
	
	print "<tr> <td><b>$text{'known_type'}</b></td>\n<td>";
	print &ui_select("type", "",
		[ [ "ssh-rsa1", $text{'index_rsa1'} ],
		  [ "ssh-rsa", $text{'index_rsa'} ],
		  [ "ssh-dsa", $text{'index_dsa'} ] ]),"</td>\n";
	}
else {
	print "<tr> <td><b>$text{'known_type'}</b></td>\n";
	printf "<td><input readonly name=type size=7 value='%s'>\n",
		$known->{'type'};
	}

print "<tr> <td valign=top><b>$text{'known_key'}</b></td>\n";
print "<td colspan=3><textarea name=key rows=10 cols=50 wrap=on>$known->{'key'}",
      "</textarea></td> </tr>\n";

print "<tr> <td valign=top><b>$text{'known_comment'}</b></td>\n";
printf "<td colspan=3><input name=comment size=40 value='%s'></td> </tr>\n",
	$known->{'comment'};

print "</table></td></tr></table>\n";
print "<table width=100%><tr>\n";

#~ if  ($known->{'hash'}){
	#~ print "<td>$text{'hash_support'}</td></tr>\n";
	#~ print "<tr><td align=left><input type=submit name=delete ",
		#~ "value='$text{'delete'}'></td>\n";
	#~ }
if ($in{'new'}) {
	print "<td><input type=submit value='$text{'create'}'></td>\n";
	}
elsif (($known->{'type'} eq 'ssh-rsa') or ($known->{'type'} eq 'ssh-dss')) {
	print "<td><input type=submit value='$text{'save'}'></td>\n";
	print "<td align=right><input type=submit name=delete ",
		"value='$text{'delete'}'></td>\n";
	}
else {
	print "<td><input type=submit value='$text{'save'}'></td>\n";
	print "<td align=right><input type=submit name=delete ",
		"value='$text{'delete'}'></td>\n";
	}

print "</tr></table></form>\n";

&ui_print_footer("list_knowns.cgi", $text{'knowns_return'},
	"", $text{'index_return'});

