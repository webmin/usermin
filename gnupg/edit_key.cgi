#!/usr/local/bin/perl
# edit_key.cgi
# Display the details of a key, including the exported format

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
if ($in{'key'}) {
	($key) = grep { $_->{'key'} eq $in{'key'} } @keys;
	$in{'idx'} = &indexof($key, @keys);
	}
else {
	$key = $keys[$in{'idx'}];
	}

&ui_print_header(undef, $text{'key_title'}, "");

print "$text{'key_desc'}<p>\n";

print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'key_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table width=100%>\n";

print "<tr> <td><b>$text{'key_id'}</b></td>\n";
print "<td><tt>$key->{'key'}</tt></td>\n";

print "<td><b>$text{'key_date'}</b></td>\n";
print "<td>$key->{'date'}</tt></td> </tr>\n";

if ($key->{'secret'}) {
	print "<form action=owner.cgi>\n";
	print "<input type=hidden name=idx value='$in{'idx'}'>\n";
	}
print "<tr> <td valign=top><b>$text{'key_owner'}</b></td>\n";
print "<td valign=top colspan=3><table border=0>\n";
print "<tr> <td><b>$text{'key_oname'}</b></td> ",
      "<td><b>$text{'key_oemail'}</b></td> </tr>\n";
for($i=0; $i<@{$key->{'name'}}; $i++) {
	print "<tr>\n";
	print "<td>",$key->{'name'}->[$i],"</td>\n";
	print "<td>",$key->{'email'}->[$i] || "<br>","</td>\n";
	if ($key->{'secret'}) {
		print "<td><input type=submit name=$i value='$text{'delete'}'></td>\n";
		}
	print "</tr>\n";
	}
if ($key->{'secret'}) {
	print "</form>\n";
	print "<form action=owner.cgi>\n";
	print "<input type=hidden name=idx value='$in{'idx'}'>\n";
	print "<tr>\n";
	print "<td><input name=name size=30></td>\n";
	print "<td><input name=email size=30></td>\n";
	print "<td><input name=add type=submit value='$text{'key_addowner'}'></td>\n";
	print "</tr>\n";
	}
print "</table>\n";
print "</form>\n" if ($key->{'secret'});
print "</td> </tr>\n";

print "<tr> <td><b>$text{'key_finger'}</b></td>\n";
print "<td colspan=3><tt>",&key_fingerprint($key),"</tt></td> </tr>\n";

#print "<tr> <td valign=top><b>$text{'key_ascii'}</b>",
#      "<br>$text{'key_asciidesc'}</td>\n";
#print "<td colspan=3><pre>";
#open(GPG, "$gpgpath --armor --export \"$key->{'name'}->[0]\" |");
#while(<GPG>) {
#	print &html_escape($_);
#	}
#close(GPG);
#print "</pre></td> </tr>\n";

if ($key->{'secret'}) {
	# Offer to change usermin's passphrase
	$pass = &get_passphrase($key);
	print "<form action=save_pass.cgi>\n";
	print "<input type=hidden name=idx value='$in{'idx'}'>\n";
	print "<tr> <td valign=top><b>",defined($pass) ? $text{'key_changepass'}
					    : $text{'key_setpass'},"</b></td>\n";
	print "<td colspan=3><input type=password name=pass size=20> ",
	      "<input type=submit value='$text{'save'}'><br>\n";
	print defined($pass) ? $text{'key_passdesc2'} : $text{'key_passdesc'},"\n";
	print "</td></tr></form>\n";
	}
else {
	# Offer to set trust level
	$tr = &get_trust_level($key);
	print "<form action=change_trust.cgi>\n";
	print "<input type=hidden name=idx value='$in{'idx'}'>\n";
	print "<tr> <td><b>$text{'key_trust'}</b></td>\n";
	print "<td><select name=trust>\n";
	foreach $t (0 .. 4) {
		printf "<option value=%d %s>%s\n",
			$t, $t eq $tr ? "selected" : "", $text{"key_trust_$t"};
		}
	print "</select>\n";
	print "<input type=submit value='$text{'key_changetrust'}'>\n";
	print "</td></tr></form>\n";
	}

print "</table></td></tr></table>\n";

print "<table width=100%><tr>\n";
print "<form action=edit_export.cgi>\n";
print "<input type=hidden name=idx value='$key->{'index'}'>\n";
print "<td width=25%><input type=submit value='$text{'key_exportform'}'></td></form>\n";

print "<form action=send.cgi>\n";
print "<input type=hidden name=idx value='$key->{'index'}'>\n";
print "<td align=middle width=25%><input type=submit value='$text{'key_send'}'></td></form>\n";

print "<form action=signkey.cgi>\n";
print "<input type=hidden name=idx value='$key->{'index'}'>\n";
print "<td align=middle width=25%><input type=submit value='$text{'key_sign'}'></td></form>\n";

print "<form action=delkey.cgi>\n";
print "<input type=hidden name=idx value='$key->{'index'}'>\n";
print "<td align=right width=25%><input type=submit value='$text{'key_del'}'></td></form>\n";
print "</tr></table>\n";

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

