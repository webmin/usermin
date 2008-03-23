#!/usr/local/bin/perl
# address_chooser.cgi
# Display a list of entries from the address book

$trust_unknown_referers = 1;
require './mailbox-lib.pl';
&ReadParse();

&popup_header($text{'address_choose'}, undef,
	"onLoad='document.forms[0].search.focus()'");
print <<EOF;
<script>
function makeaddress(a, n)
{
if (n == "") {
	// An address without a name
	return "<"+a+">";
	}
else if (n.indexOf(",") != -1) {
	// A name with a comma in it
	return "\\""+n+"\\" <"+a+">";
	}
else {
	// A name without a comma
	return n+" <"+a+">";
	}
}

// Add an address to the list
function newaddress(a, n)
{
av = makeaddress(a, n);
if (top.opener.ifield.value == "") {
	top.opener.ifield.value = av;
	}
else {
	top.opener.ifield.value += ","+av;
	}
}

// Remove an address from the list
function oldaddress(a, n)
{
av = makeaddress(a, n);
curr = top.opener.ifield.value;
idx1 = curr.indexOf(av+",");
idx2 = curr.indexOf(","+av);
if (curr == av) {
	// Address only!
	curr = "";
	}
else if (idx1 != -1) {
	// Found the address, in string
	curr = curr.substring(0, idx1)+curr.substring(idx1+av.length+1);
	}
else if (idx2 != -1) {
	// Found the ,address in string
	curr = curr.substring(0, idx2)+curr.substring(idx2+av.length+1);
	}
else {
	// Look for address only
	sp = curr.split(",");
	curr = "";
	for(j=0; j<sp.length; j++) {
		if (sp[j].indexOf(a) == -1) {
			if (curr == "") {
				curr = sp[j];
				}
			else {
				curr += ","+sp[j];
				}
			}
		}
	}
top.opener.ifield.value = curr;
}

// Called when an address has been clicked on
function clickaddress(a, n, f)
{
if (f.checked) {
	newaddress(a, n);
	}
else {
	oldaddress(a, n);
	}
}

function select(a, n)
{
if ($in{'mode'} == 2) {
	// Strip off domain
	at = a.indexOf("@");
	if (at > 0)
		a = a.substr(0, at);
	}
if (top.opener.rfield != null) {
	// Put real name in separate field
	top.opener.ifield.value = a;
	top.opener.rfield.value = n;
	}
else {
	// Combine to single field
	if (n == "") {
		av = "<"+a+">";
		}
	else {
		av = n+" <"+a+">";
		}
	top.opener.ifield.value = av;
	}
window.close();
}
</script>
EOF

# Find addresses and groups
@addrs = &list_addresses();
if ($in{'search'}) {
	$s = $in{'search'};
	@addrs = grep { $_->[0] =~ /\Q$s\E/i || $_->[1] =~ /\Q$s\E/i } @addrs;
	}
if ($in{'mode'}) {
	@addrs = grep { $_->[3] } @addrs;
	$addrs_count = scalar(@addrs);
	}
else {
	if (!$uconfig{'from_in_to'}) {
		@addrs = grep { !$_->[3] } @addrs;
		}
	$addrs_count = scalar(@addrs);
	@agroups = &list_address_groups();
	if ($in{'search'}) {
		$s = $in{'search'};
		@agroups = grep { $_->[0] =~ /\Q$s\E/i ||
				  $_->[1] =~ /\Q$s\E/i } @agroups;
		}
	foreach $a (@agroups) {
		push(@addrs, [ $a->[0] ]);
		$mems{$a->[0]} = [ &split_addresses($a->[1]) ];
		}
	}

# Show search form
if (@addrs || $in{'search'}) {
	print &ui_form_start("address_chooser.cgi", "post");
	print "<b>$text{'address_search'}</b>\n";
	print &ui_textbox("search", $in{'search'}, 20);
	print &ui_hidden("mode", $in{'mode'});
	print &ui_hidden("addr", $in{'addr'});
	print &ui_submit($text{'address_ok'});
	print &ui_form_end();
	}

# Show list of addresses
if (@addrs) {
	local @sp = &split_addresses(&decode_mimewords($in{'addr'}));
	for($i=0; $i<@sp; $i++) {
		$infield{$sp[$i]->[0]} = $i;
		}
	print "<form><table width=100%>\n";
	print "<tr>\n";
	print "<td><br></td>\n" if (!$in{'mode'});
	print "<td><b>$text{'address_addr'}</b></td>\n";
	print "<td><b>$text{'address_name'}</b></td> </tr>\n";
	$i = 0;
	foreach $a (@addrs) {
		if ($i == $addrs_count && $i) {
			print "<tr> <td><br></td>\n";
			print "<td><b>$text{'address_group'}</b></td>\n";
			print "<td><b>$text{'address_members'}</b></td></tr>\n";
			}
		print "<tr>\n";
		if ($in{'mode'} == 0) {
			printf "<td><input type=checkbox name=addr_$i value='%s' onClick='clickaddress(\"%s\", \"%s\", this)' %s>", &html_escape($a->[1]), &html_escape($a->[0]), &html_escape($a->[1]), defined($infield{$a->[0]}) ? "checked" : "";
			$href = "<a href='' onClick='cb = document.forms[1].addr_$i; cb.checked = !cb.checked; clickaddress(\"".&html_escape($a->[0])."\", \"".&html_escape($a->[1])."\", cb); return false'>";
			}
		else {
			$href = "<a href='' onClick='select(\"".&html_escape($a->[0])."\", \"".&html_escape($a->[1])."\"); return false'>";
			}
		if ($i >= $addrs_count) {
			print "<td>$href",$a->[0],"</a></td>\n";
			local $m = @{$mems{$a->[0]}};
			print "<td>$href",&text('address_m', $m),"</a></td>\n";
			}
		else {
			print "<td>$href$a->[0]</a></td>\n";
			print "<td>$href",($a->[1] ? $a->[1] : "<br>"),"</a></td>\n";
			}
		print "</tr>\n";
		$i++;
		}
	print "</table></form>\n";
	}
elsif ($in{'search'}) {
	print "<b>$text{'address_none2'}</b> <p>\n";
	}
else {
	print "<b>$text{'address_none'}</b> <p>\n";
	}
&popup_footer();

