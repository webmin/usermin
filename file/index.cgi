#!/usr/local/bin/perl
# index.cgi
# Output HTML for the file manager applet

require './file-lib.pl';
&ReadParse();
$theme_no_table = 1;
@modules = &get_available_module_infos(1);
if (@modules == 1 && $gconfig{'gotoone'}) {
	&header($text{'index_title'}, "", undef, 0, 1);
	$w = 100;
	$h = 80;
	}
else {
	&header($text{'index_title'});
	$w = 100;
	$h = 100;
	if (!$tconfig{'inframe'}) {
		$return = "<param name=return value=\"$gconfig{'webprefix'}/?cat=$module_info{'category'}\">";
		$returnhtml = &text('index_index',
				    "$gconfig{'webprefix'}/")."<p>";
		}
	}
$root = join(" ", @allowed_roots);
$noroot = join(" ", @denied_roots);
if ($in{'open'}) {
	$open = "<param name=open value=\"$in{'open'}\">\n";
	}
if ($session_id) {
	$session = "<param name=session value=\"usid=$session_id\">\n";
	}
if (!$config{'noprefs'}) {
	$config = "<param name=config value=\"$gconfig{'webprefix'}/uconfig.cgi?$module_name\">\n";
	}
$iconsize = int($userconfig{'iconsize'});

foreach $d (@disallowed_buttons) {
	$disallowed .= "<param name=no_$d value=1>\n";
	}

# Create parameters for custom colours
foreach $k (keys %tconfig) {
	if ($k =~ /^applet_(.*)/) {
		$colours .= "<param name=$k value=\"$tconfig{$k}\">\n";
		}
	}

$mounting = &foreign_check("usermount");

print <<EOF;
<script>
function upload(dir)
{
open("upform.cgi?dir="+escape(dir)+"&trust=$trust", "upload", "toolbar=no,menubar=no,scrollbar=no,width=450,height=200");
}
function htmledit(file, dir)
{
open("edit_html.cgi?file="+escape(file)+"&dir="+escape(dir)+"&trust=$trust", "html", "toolbar=no,menubar=no,scrollbar=no,width=800,height=600");
}
</script>

<applet code=FileManager name=FileManager archive=file.jar width=$w% height=$h% MAYSCRIPT>
<param name=root value="$root">
<param name=noroot value="$noroot">
<param name=follow value="$follow">
<param name=ro value="0">
<param name=sharing value="0">
<param name=mounting value="$mounting">
<param name=home value="$real_home_dir">
<param name=goto value="$config{'goto'}">
<param name=iconsize value=$iconsize>
<param name=doarchive value=$archive>
<param name=fixed value="$userconfig{'fixed'}">
<param name=small_fixed value="$userconfig{'small_fixed'}">
<param name=canperms value="$canperms">
<param name=canusers value="$canusers">
<param name=contents value="$contents">
<param name=force_text value="$userconfig{'force_text'}">
$config
$session
$open
$return
$disallowed
$colours
$text{'index_nojava'} <p>
</applet>
EOF
&footer();

