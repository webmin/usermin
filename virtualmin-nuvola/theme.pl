#!/usr/local/bin/perl -w

# Swell-Nuvola theme
# Icons copyright David Vignoni, all other theme elements copyright Joe Cooper.

sub theme_icons_table
{
local ($i, $need_tr);
local $cols = $_[3] ? $_[3] : 4;
local $per = int(100.0 / $cols);
print "<table id='main' width=100% cellpadding=5>\n";
for($i=0; $i<@{$_[0]}; $i++) {
	if ($i%$cols == 0) { print "<tr>\n"; }
	print "<td width=$per% align=center valign=top>\n";
	&generate_icon($_[2]->[$i], $_[1]->[$i], $_[0]->[$i],
		       $_[4], $_[5], $_[6]);
	print "</td>\n";
        if ($i%$cols == $cols-1) { print "</tr>\n"; }
        }
while($i++%$cols) { print "<td width=$per%></td>\n"; $need_tr++; }
print "</tr>\n" if ($need_tr);
print "</table>\n";
}

sub theme_generate_icon
{
local $w = !defined($_[4]) ? "width=48" : $_[4] ? "width=$_[4]" : "";
local $h = !defined($_[5]) ? "height=48" : $_[5] ? "height=$_[5]" : "";
if ($tconfig{'noicons'}) {
	if ($_[2]) {
		print "<a href=\"$_[2]\" $_[3]>$_[1]</a>\n";
		}
	else {
		print "$_[1]\n";
		}
	}
elsif ($_[2]) {
	print "<table><tr><td width=48 height=48>\n",
	      "<a href=\"$_[2]\" $_[3]><img src=\"$_[0]\" alt=\"\" border=0 ",
	      "$w $h></a></td></tr></table>\n";
	print "<a href=\"$_[2]\" $_[3]>$_[1]</a>\n";
	}
else {
	print "<table><tr><td width=48 height=48>\n",
	      "<img src=\"$_[0]\" alt=\"\" border=0 $w $h>",
	      "</td></tr></table>\n$_[1]\n";
	}
}

sub theme_header
{
return if ($main::done_webmin_header++);
local $ll;
local $charset = defined($force_charset) ? $force_charset : &get_charset();
&PrintHeader($charset);
print "<!doctype html public \"-//W3C//DTD HTML 3.2 Final//EN\">\n";
print "<html>\n";
local $os_type = $gconfig{'real_os_type'} ? $gconfig{'real_os_type'}
					  : $gconfig{'os_type'};
local $os_version = $gconfig{'real_os_version'} ? $gconfig{'real_os_version'}
					        : $gconfig{'os_version'};
print "<head>\n";
if ($charset) {
	print "<meta http-equiv=\"Content-Type\" ",
	      "content=\"text/html; Charset=$charset\">\n";
	}
if (@_ > 0) {
	if ($gconfig{'sysinfo'} == 1) {
		printf "<title>%s : %s on %s (%s %s)</title>\n",
			$_[0], $remote_user, &get_display_hostname(),
			$os_type, $os_version;
		}
	elsif ($gconfig{'sysinfo'} == 4) {
		printf "<title>%s on %s (%s %s)</title>\n",
			$remote_user, &get_display_hostname(),
			$os_type, $os_version;
		}
	else {
		print "<title>$_[0]</title>\n";
		}
	print $_[7] if ($_[7]);
	if ($gconfig{'sysinfo'} == 0 && $remote_user) {
		print "<script language=JavaScript type=text/javascript>\n";
		printf
		"defaultStatus=\"%s%s logged into %s %s on %s (%s%s)\";\n",
			$ENV{'ANONYMOUS_USER'} ? "Anonymous user" :$remote_user,
			$ENV{'SSL_USER'} ? " (SSL certified)" :
			$ENV{'LOCAL_USER'} ? " (Local user)" : "",
			$text{'programname'},
			&get_webmin_version(), &get_display_hostname(),
			$os_type, $os_version eq "*" ? "" : " $os_version";
		print "</SCRIPT>\n";
		}
	}
print "$tconfig{'headhtml'}\n" if ($tconfig{'headhtml'});
if ($tconfig{'headinclude'}) {
	local $_;
	open(INC, "$root_directory/$current_theme/$tconfig{'headinclude'}");
	while(<INC>) {
		print;
		}
	close(INC);
	}
print "</head>\n";
local $bgcolor = defined($tconfig{'cs_page'}) ? $tconfig{'cs_page'} :
		 defined($gconfig{'cs_page'}) ? $gconfig{'cs_page'} : "ffffff";
local $link = defined($tconfig{'cs_link'}) ? $tconfig{'cs_link'} :
	      defined($gconfig{'cs_link'}) ? $gconfig{'cs_link'} : "0000ee";
local $text = defined($tconfig{'cs_text'}) ? $tconfig{'cs_text'} : 
	      defined($gconfig{'cs_text'}) ? $gconfig{'cs_text'} : "000000";
local $bgimage = defined($tconfig{'bgimage'}) ? "background=$tconfig{'bgimage'}"
					      : "";
print "<body bgcolor=#$bgcolor link=#$link vlink=#$link text=#$text ",
      "$bgimage $tconfig{'inbody'} $_[8]>\n";
local $hostname = &get_display_hostname();
local $version = &get_webmin_version();
local $prebody = $tconfig{'prebody'};
if ($prebody) {
	$prebody =~ s/%HOSTNAME%/$hostname/g;
	$prebody =~ s/%VERSION%/$version/g;
	$prebody =~ s/%USER%/$remote_user/g;
	$prebody =~ s/%OS%/$os_type $os_version/g;
	print "$prebody\n";
	}
if ($tconfig{'prebodyinclude'}) {
	local $_;
	open(INC, "$root_directory/$current_theme/$tconfig{'prebodyinclude'}");
	while(<INC>) {
		print;
		}
	close(INC);
	}
if (defined(&theme_prebody)) {
	&theme_prebody(@_);
	}
if (@_ > 1) {
	print "<table class=header width=100%><tr>\n";
	if ($gconfig{'sysinfo'} == 2 && $remote_user) {
		print "<td colspan=3 align=center>\n";
		printf "%s%s logged into %s %s on %s (%s%s)</td>\n",
			$ENV{'ANONYMOUS_USER'} ? "Anonymous user" : "<tt>$remote_user</tt>",
			$ENV{'SSL_USER'} ? " (SSL certified)" :
			$ENV{'LOCAL_USER'} ? " (Local user)" : "",
			$text{'programname'},
			$version, "<tt>$hostname</tt>",
			$os_type, $os_version eq "*" ? "" : " $os_version";
		print "</tr> <tr>\n";
		}
	print "<td width=15% valign=top align=left>";
	if ($ENV{'HTTP_WEBMIN_SERVERS'}) {
		print "<a href='$ENV{'HTTP_WEBMIN_SERVERS'}'>",
		      "$text{'header_servers'}</a><br>\n";
		}
	if (!$_[5] && !$tconfig{'noindex'}) {
		local %acl;
		&read_acl(undef, \%acl);
		#local $mc = @{$acl{$base_remote_user}};
		local @avail = &get_available_module_infos(1);
		local $nolo = $ENV{'ANONYMOUS_USER'} ||
			      $ENV{'SSL_USER'} || $ENV{'LOCAL_USER'} ||
			      $ENV{'HTTP_USER_AGENT'} =~ /webmin/i;
		if ($gconfig{'gotoone'} && $main::session_id && @avail == 1 &&
		    !$nolo) {
			print "<a href='$gconfig{'webprefix'}/session_login.cgi?logout=1'>",
			      "$text{'main_logout'}</a><br>";
			}
		elsif ($gconfig{'gotoone'} && @avail == 1 && !$nolo) {
			print "<a href=$gconfig{'webprefix'}/switch_user.cgi>",
			      "$text{'main_switch'}</a><br>";
			}
		elsif (!$gconfig{'gotoone'} || @avail > 1) {
			print "<a href='$gconfig{'webprefix'}/?cat=$module_info{'category'}'>",
			      "$text{'header_webmin'}</a><br>\n";
			}
		}
	if (!$_[4] && !$tconfig{'nomoduleindex'}) {
		local $idx = $module_info{'index_link'};
		local $mi = $module_index_link || "/$module_name/$idx";
		print "<img src="/images/left.gif"></img>";
		print "<a href=\"$gconfig{'webprefix'}$mi\">",
		      "$text{'header_module'}</a><br>\n";
		}
	if (ref($_[2]) eq "ARRAY" && !$ENV{'ANONYMOUS_USER'}) {
		print "<img src="/images/help.gif"></img>";
		print &hlink($text{'header_help'}, $_[2]->[0], $_[2]->[1]),
		      "<br>\n";
		}
	elsif (defined($_[2]) && !$ENV{'ANONYMOUS_USER'}) {
		print "<img src="/images/help.gif"></img>";
		print &hlink($text{'header_help'}, $_[2]),"<br>\n";
		}
	if ($_[3]) {
		local %access = &get_module_acl();
		if (!$access{'noconfig'} && !$config{'noprefs'}) {
			local $cprog = $user_module_config_directory ?
					"uconfig.cgi" : "config.cgi";
			print "<a href=\"$gconfig{'webprefix'}/$cprog?$module_name\">",
			      $text{'header_config'},"</a><br>\n";
			}
		}
	print "</td>\n";
	if ($_[1]) {
		# Title is a single image
		print "<td align=center width=70%>",
		      "<img alt=\"$_[0]\" src=\"$_[1]\"></td>\n";
		}
	elsif ($current_lang_info->{'titles'} && !$gconfig{'texttitles'} &&
	       !$tconfig{'texttitles'}) {
		# Title is made out of letter images
		local $title = &entities_to_ascii($_[0]);
		print "<td align=center width=70%>";
		foreach $l (split(//, $title)) {
			$ll = ord($l);
			if ($ll > 127 && $current_lang_info->{'charset'}) {
				print "<img src=$gconfig{'webprefix'}/images/letters/$ll.$current_lang_info->{'charset'}.gif alt=\"$l\" align=bottom>";
				}
			elsif ($l eq " ") {
				print "<img src=$gconfig{'webprefix'}/images/letters/$ll.gif alt=\"\&nbsp;\" align=bottom>";
				}
			else {
				print "<img src=$gconfig{'webprefix'}/images/letters/$ll.gif alt=\"$l\" align=bottom>";
				}
			}
		print "<br>$_[9]\n" if ($_[9]);
		print "</td>\n";
		}
	else {
		# Title is just text
		print "<td align=center width=70%><h1>$_[0]</h1>\n";
		print "$_[9]\n" if ($_[9]);
		print "</td>\n";
		}
	print "<td width=15% valign=top align=right>";
	print $_[6];
	print "</td></tr></table>\n";
	}
}
