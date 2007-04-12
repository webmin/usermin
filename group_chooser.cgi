#!/usr/local/bin/perl
# group_chooser.cgi
# This CGI generated the HTML for choosing a group or list of groups.

require './web-lib.pl';
&init_config();
&switch_to_remote_user();
&ReadParse();
%access = &get_module_acl();

# Build list of primary groups
setpwent();
while(@uinfo = getpwent()) {
	push(@{$members{$uinfo[3]}}, $uinfo[0]);
	}
endpwent() if ($gconfig{'os_type'} ne 'hpux');

if ($in{'multi'}) {
	# selecting multiple groups.
	if ($in{'frame'} == 0) {
		# base frame
		&PrintHeader();
		print "<script>\n";
		@ul = split(/\s+/, $in{'group'});
		$len = @ul;
		print "sel = new Array($len);\n";
		print "selr = new Array($len);\n";
		for($i=0; $i<$len; $i++) {
			print "sel[$i] = \"$ul[$i]\";\n";
			@ginfo = getgrnam($ul[$i]);
			if (@ginfo) {
				@mems = &unique( split(/ /, $ginfo[3]),
						 @{$members{$ginfo[2]}} );
				if (@mems > 3) { @mems = (@mems[0..1], "..."); }
				print "selr[$i] = \"",join(' ', @mems),"\";\n";
				}
			else { print "selr[$i] = \"???\";\n"; }
			}
		print "</script>\n";
		print "<title>$text{'groups_title1'}</title>\n";
		print "<frameset cols='50%,50%'>\n";
		print "<frame src=\"/group_chooser.cgi?frame=1&multi=1\">\n";
		print "<frameset rows='*,50' frameborder=no>\n";
		print " <frame src=\"/group_chooser.cgi?frame=2&multi=1\">\n";
		print " <frame src=\"/group_chooser.cgi?frame=3&multi=1\" scrolling=no>\n";
		print "</frameset>\n";
		print "</frameset>\n";
		}
	elsif ($in{'frame'} == 1) {
		# list of all groups to choose from
		&header();
		print "<script>\n";
		print "function addgroup(u, r)\n";
		print "{\n";
		print "top.sel[top.sel.length] = u\n";
		print "top.selr[top.selr.length] = r\n";
		print "top.frames[1].location = top.frames[1].location\n";
		print "return false;\n";
		print "}\n";
		print "</script>\n";
		print "<font size=+1>$text{'groups_all'}</font>\n";
		print "<table width=100%>\n";
		foreach $u (&get_groups_list()) {
			if ($in{'group'} eq $u->[0]) { print "<tr $cb>\n"; }
			else { print "<tr>\n"; }
			print "<td width=20%><a href=\"\" onClick='return addgroup(\"$u->[0]\", \"$u->[3]\")'>$u->[0]</a></td>\n";
			print "<td>$u->[3]</td> </tr>\n";
			}
		print "</table>\n";
		}
	elsif ($in{'frame'} == 2) {
		# show chosen groups
		&header();
		print "<font size=+1>$text{'groups_sel'}</font>\n";
		print <<'EOF';
<table width=100%>
<script>
function sub(j)
{
sel2 = new Array(); selr2 = new Array();
for(k=0,l=0; k<top.sel.length; k++) {
	if (k != j) {
		sel2[l] = top.sel[k];
		selr2[l] = top.selr[k];
		l++;
		}
	}
top.sel = sel2; top.selr = selr2;
location = location;
return false;
}
for(i=0; i<top.sel.length; i++) {
	document.write("<tr>\n");
	document.write("<td><a href=\"\" onClick='return sub("+i+")'>"+top.sel[i]+"</a></td>\n");
	document.write("<td>"+top.selr[i]+"</td>\n");
	}
</script>
</table>
EOF
		}
	elsif ($in{'frame'} == 3) {
		# output OK and Cancel buttons
		&header();
		print "<form>\n";
		print "<input type=button value=\"$text{'groups_ok'}\" ",
		      " onClick='top.ifield.value = top.sel.join(\" \"); ",
		      "top.close()'>\n";
		print "<input type=button value=\"$text{'groups_cancel'}\" ",
		      "onClick='top.close()'>\n";
		print "&nbsp;&nbsp;<input type=button value=\"$text{'groups_clear'}\" onClick='top.sel = new Array(); top.selr = new Array(); top.frames[1].location = top.frames[1].location'>\n";
		print "</form>\n";
		}
	}
else {
	# selecting just one group .. display a list of all groups to choose from
	&header();
	print "<script>\n";
	print "function select(f)\n";
	print "{\n";
	print "ifield.value = f;\n";
	print "top.close();\n";
	print "return false;\n";
	print "}\n";
	print "</script>\n";
	print "<title>$text{'groups_title2'}</title>\n";
	print "<table width=100%>\n";
	foreach $u (&get_groups_list()) {
		if ($in{'group'} eq $u->[0]) { print "<tr $cb>\n"; }
		else { print "<tr>\n"; }
		print "<td width=20%><a href=\"\" onClick='return select(\"$u->[0]\")'>$u->[0]</a></td>\n";
		print "<td>$u->[3]</td> </tr>\n";
		}
	print "</table>\n";
	}

sub get_groups_list
{
local(@ginfo, @groups, %gcan, %found);
if ($access{'gedit_mode'} == 2 || $access{'gedit_mode'} == 3) {
	map { $gcan{$_}++ } split(/\s+/, $access{'gedit'});
	}
setgrent();
while(@ginfo = getgrent()) {
	@mems = &unique( split(/ /, $ginfo[3]), @{$members{$ginfo[2]}} );
	if (@mems > 3) { @mems = (@mems[0..1], "..."); }
	$ginfo[3] = join(' ', @mems);
	if ($access{'gedit_mode'} == 0 ||
	    $access{'gedit_mode'} == 2 && $gcan{$ginfo[0]} ||
	    $access{'gedit_mode'} == 3 && !$gcan{$ginfo[0]} ||
	    $access{'gedit_mode'} == 4 &&
		(!$access{'gedit'} || $ginfo[2] >= $access{'gedit'}) &&
		(!$access{'gedit2'} || $ginfo[2] <= $access{'gedit2'})) {
		push(@groups, [ @ginfo ]) if (!$found{$ginfo[0]}++);
		}
	}
endgrent() if ($gconfig{'os_type'} ne 'hpux');
return sort { $a->[0] cmp $b->[0] } @groups;
}

