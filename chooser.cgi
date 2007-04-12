#!/usr/local/bin/perl
# chooser.cgi
# Outputs HTML for a frame-based file chooser 

@icon_map = (	"c", "text.gif",
		"txt", "text.gif",
		"pl", "text.gif",
		"cgi", "text.gif",
		"html", "text.gif",
		"htm", "text.gif",
		"gif", "image.gif",
		"jpg", "image.gif",
		"tar", "binary.gif"
		);

require './web-lib.pl';
&init_config();
&switch_to_remote_user();
%access = &get_module_acl();
$rootdir = $access{'root'} ? $access{'root'} :
	   $remote_user_info[7] ? $remote_user_info[7] : "/";
&ReadParse();
if ($in{'file'} =~ /^(.*\/)([^\/]*)$/) {
	# File entered is invalid
	$dir = $1;
	$file = $2;
	}
else {
	$dir = $rootdir;
	$dir .= '/' if ($dir !~ /\/$/);
	$file = "";
	}

if (!(-d $in{'chroot'}.$dir)) {
	# Entered directory does not exist
	$dir = $rootdir.'/';
	$file = "";
	}
if ($rootdir ne '/' && $dir ne $rootdir &&
    $dir !~ /^$rootdir\//) {
	# Directory is outside allowed root
	$dir = $rootdir.'/';
	$file = "";
	}

if ($in{'frame'} == 0) {
	# base frame
	&PrintHeader();
	if ($in{'type'} == 0)
		{ print "<title>$text{'chooser_title1'}</title>\n"; }
	elsif ($in{'type'} == 1)
		{ print "<title>$text{'chooser_title2'}</title>\n";}
	print "<frameset rows='*,50'>\n";
	print "<frame marginwidth=5 marginheight=5 name=topframe ",
	     "src=\"chooser.cgi?frame=1&file=$in{'file'}&chroot=$in{'chroot'}&",
	     "type=$in{'type'}\">\n";
	print "<frame marginwidth=0 marginheight=0 name=bottomframe ",
	      "src=\"chooser.cgi?frame=2&file=$in{'file'}&",
	      "chroot=$in{'chroot'}&type=$in{'type'}\" scrolling=no>\n";
	print "</frameset>\n";
	}
elsif ($in{'frame'} == 1) {
	# List of files in this directory
	&header();
	
	print <<EOF;
<script>
function fileclick(f, d)
{
curr = top.frames[1].document.forms[0].elements[1].value;
if (curr == f) {
	// Double-click! Enter directory or select file
	if (d) {
		// Enter this directory
		location = "chooser.cgi?frame=1&chroot=$in{'chroot'}&type=$in{'type'}&file="+f+"/";
		}
	else {
		// Select this file and close the window
		top.ifield.value = f;
		top.close();
		}
	}
else {
	top.frames[1].document.forms[0].elements[1].value = f;
	}
}

function parentdir(p)
{
top.frames[1].document.forms[0].elements[1].value = p;
location = "chooser.cgi?frame=1&chroot=$in{'chroot'}&type=$in{'type'}&file="+p;
}
</script>
EOF

	print "<b>",&text('chooser_dir', $dir),"</b>\n";
	print "<table width=100%>\n";
	opendir(DIR, $in{'chroot'}.$dir);
	foreach $f (sort { $a cmp $b } readdir(DIR)) {
		$path = "$in{'chroot'}$dir$f";
		if ($f eq ".") { next; }
		if ($f eq ".." && ($dir eq "/" || $dir eq $rootdir.'/')) { next; }
		if (!(-d $path) && $in{'type'} == 1) { next; }

		@st = stat($path);
		print "<tr>\n";
		$isdir = 0; undef($icon);
		if (-d $path) { $icon = "dir.gif"; $isdir = 1; }
		elsif ($path =~ /\.([^\.\/]+)$/) { $icon = $icon_map{$1}; }
		if (!$icon) { $icon = "unknown.gif"; }

		if ($f eq "..") {
			$dir =~ /^(.*\/)[^\/]+\/$/;
			$link = "<a href=\"\" onClick='parentdir(\"$1\"); return false'>";
			}
		else {
			$link = "<a href=\"\" onClick='fileclick(\"$dir$f\", $isdir); return false'>";
			}
		print "<td>$link<img border=0 src=/images/$icon></a></td>\n";
		print "<td nowrap>$link$f</a></td>\n";
		printf "<td nowrap>%s</td>\n",
			$st[7] > 1000000 ? int($st[7]/1000000)." MB" :
			$st[7] > 1000 ? int($st[7]/1000)." kB" :
			$st[7];
		@tm = localtime($st[9]);
		printf "<td nowrap><tt>%.2d/%s/%.4d</tt></td>\n",
			$tm[3], $text{'smonth_'.($tm[4]+1)}, $tm[5]+1900;
		printf "<td nowrap><tt>%.2d:%.2d</tt></td>\n", $tm[2], $tm[1];
		print "</tr>\n";
		}
	closedir(DIR);
	print "</table>\n";
	}
elsif ($in{'frame'} == 2) {
	# Current file and OK/cancel buttons
	&header();
	print <<EOF;
<script>
function filechosen()
{
top.ifield.value = document.forms[0].path.value;
top.close();
}
</script>
EOF

	print "<table width=100%>\n";
	print "<form onSubmit='filechosen(); return false'>\n";
	print "<tr><td><input type=submit value=\"$text{'chooser_ok'}\"></td>\n";
	print "<td align=right><input name=path size=45 value=\"$dir$file\"></td></tr>\n";
	print "</form>\n";
	print "</table>\n";
	}

