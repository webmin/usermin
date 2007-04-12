#!/usr/local/bin/perl
# show.cgi
# Show directives from a virtualhost, directory or .htaccess

require './htaccess-lib.pl';
&ReadParse();
if (defined($in{'idx'})) {
	# files within .htaccess file
	$hconf = &get_htaccess_config($in{'file'});
	$d = $hconf->[$in{'idx'}];
	$conf = $d->{'members'};
	$title = &text('htfile_header', &dir_name($d),
		       "<tt>$in{'file'}</tt>");
	$edit = "edit_files.cgi"; $return = "htaccess_index.cgi";
	$editable = "directory"; $rmsg = $text{'htindex_return'};
	}
else {
	# .htaccess file
	$conf = &get_htaccess_config($in{'file'});
	$title = &text('htindex_header', "<tt>$in{'file'}</tt>");
	$edit = "edit_htaccess.cgi"; $return = "htaccess_index.cgi";
	$editable = 'htaccess'; $rmsg = $text{'htindex_return'};
	$dir = "files_index.cgi";
	}
&ui_print_header($title, $text{'show_title'}, "");

foreach $h ('virt', 'idx', 'file') {
	if (defined($in{$h})) {
		$s .= "<input type=hidden name=$h value='$in{$h}'>\n";
		push(@args, "$h=$in{$h}");
		}
	}
$args = join('&', @args);

for($i=0; $i<$directive_type_count; $i++) {
	foreach $e (&editable_directives($i, $editable)) {
		foreach $n (split(/\s+/, $e->{'name'})) {
			$edit{lc($n)} = $e;
			push(@elist, { 'name' => $n, 'edit' => $e });
			}
		}
	}
@elist = sort { $a->{'name'} cmp $b->{'name'} } @elist;

print "<table><tr><td colspan=2>\n";
print "<table border><tr><td $cb><pre>";
&show_directives($conf, 0);
print "</pre></td></tr></table>\n";
print "</td></tr>\n";

if ($in{'virt'} || $in{'file'} || defined($in{'idx'})) {
	print "<tr><form action=manual_form.cgi>\n";
	print $s;
	print "<td><input type=submit name=these ",
	      "value='$text{'show_these'}'></td>\n";
	print "</form>\n";
	}
else {
	print "<tr> <td></td>\n";
	}

print "<form action=$edit>\n";
print $s;
print "<td align=right><input type=submit value='$text{'show_edit'}'>\n";
print "<select name=type>\n";
foreach $e (@elist) {
	print "<option value=",$e->{'edit'}->{'type'},">",
	      $e->{'name'},"\n";
	}
print "</select></td>\n";
print "</form></tr></table>\n";

&ui_print_footer("$return?$args", $rmsg);

# show_directives(list, indent)
sub show_directives
{
local ($list, $ind) = @_;
local $idx;
for($idx=0; $idx<@$list; $idx++) {
	local $d = $list->[$idx];
	next if ($d->{'name'} eq "dummy");
	$t = $edit{lc($d->{'name'})};
	if ($d->{'type'}) {
		# Recurse into section
		local ($ed1, $ed2);
		print " " x $ind;
		if ($d->{'name'} eq "VirtualHost") { next; }
		elsif ($d->{'name'} =~ /Location|Files|Directory/) {
			$ed1 = "<a href=\"$dir?$args&".
			       "idx=$idx\">";
			$ed2 = "</a>";
			}
		print $ed1,"&lt;",$d->{'name'}," ",$d->{'value'},
		      "&gt;",$ed2,"\n";
		&show_directives($d->{'members'}, $ind+1);
		print " " x $ind;
		print "&lt;/",$d->{'name'},"&gt;\n";
		}
	elsif ($_[1] || !$access_types{$t->{'type'}}) {
		# Directives in section are not editable
		&print_line($d, [ $d->{'name'}," ",$d->{'value'} ], $ind);
		}
	else {
		next if (!$t);
		&print_line($d, [ $d->{'name'}," ",$d->{'value'} ], $ind,
			    "$edit?$args&type=$t->{'type'}");
		}
	}
}

