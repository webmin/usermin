#!/usr/local/bin/perl
# Display all Webmin modules visible to the current user

require './web-lib.pl';
&init_config();
$hostname = &get_display_hostname();
$ver = &get_webmin_version();
&get_miniserv_config(\%miniserv);
if ($gconfig{'real_os_type'}) {
	if ($gconfig{'os_version'} eq "*") {
		$ostr = $gconfig{'real_os_type'};
		}
	else {
		$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
		}
	}
else {
	$ostr = "$gconfig{'os_type'} $gconfig{'os_version'}";
	}
%access = &get_module_acl();

# Build a list of all modules
@modules = &get_visible_module_infos();

if (!defined($in{'cat'})) {
	# Maybe redirect to some module after login
	local $goto = &get_goto_module(\@modules);
	if ($goto) {
		&redirect($goto->{'dir'}.'/');
		exit;
		}
	}

# First login?
if ($gconfig{'firstlogin'}) {
  &redirect($gconfig{'firstlogdir'}.'/');
  $gconfig{'firstlogin'} = 0;
  &lock_file("$config_directory/config");
  &write_file("$config_directory/config", \%gconfig);
  &unlock_file("$config_directory/config");  
  exit;
  }

$gconfig{'sysinfo'} = 0 if ($gconfig{'sysinfo'} == 1);
if ($gconfig{'alt_startpage'}) {
	# Tim's webmin header
	&header(&text('main_title', $ver, $hostname, $ostr));
	print "<TABLE BORDER=0 WIDTH=100%>\n";
	print "<TR><TD WIDTH=20% ALIGN=left>\n";
	print "Version $ver<BR>$hostname<BR>$ostr</TD>";
	print "<TD WIDTH=60% ALIGN=center>\n";
	print "<IMG SRC=\"images/newlogo.gif\" BORDER=0>";
	print "</TD><TD WIDTH=20% ALIGN=right>";
	print "<a href=http://www.webmin.com/>$text{'main_homepage'}</a><br>";
	print "<a href=feedback_form.cgi>$text{'main_feedback'}</a>"
		if ($gconfig{'nofeedbackcc'} != 2 && $access{'feedback'});
	if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
	    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
		print "<br><br>\n";
		if ($main::session_id) {
			print "<a href='session_login.cgi?logout=1'>",
			      "$text{'main_logout'}</a>";
			}
		else {
			print "<a href=switch_user.cgi>$text{'main_switch'}</a>";
			}
		}
	print "</TD></TR></TABLE><P>\n\n";
	}
else {
	# Standard webmin header
	if ($gconfig{'texttitles'}) {
		@args = ( $text{'main_title2'}, undef );
		}
	else {
		@args = ( $gconfig{'nohostname'} ? $text{'main_title2'} :
			    &text('main_title', $ver, $hostname, $ostr),
			  "images/newlogo.gif" );
		}
	&header(@args, undef, undef, 1, 1,
		$tconfig{'brand'} ? 
		"<a href=$tconfig{'brand_url'}>$tconfig{'brand'}</a><br>" .
                ($gconfig{'nofeedbackcc'} == 2 || !$access{'feedback'} ? "" :
                  "<br><a href=feedback_form.cgi>$text{'main_feedback'}</a>") :
		$gconfig{'brand'} ? 
		"<a href=$gconfig{'brand_url'}>$gconfig{'brand'}</a>".
                ($gconfig{'nofeedbackcc'} == 2 || !$access{'feedback'} ? "" :
                  "<br><a href=feedback_form.cgi>$text{'main_feedback'}</a>") :
		"<a href=http://www.webmin.com/>$text{'main_homepage'}</a>".
		($gconfig{'nofeedbackcc'} == 2 || !$access{'feedback'} ? "" :
		  "<br><a href=feedback_form.cgi>$text{'main_feedback'}</a>")
		);
	print "<center>",
	    &text('main_version', $ver, $hostname, $ostr),"</font></center>\n"
		if (!$gconfig{'nohostname'});
	print "<p>\n";
	}
print $text{'main_header'};

if (!@modules) {
	# user has no modules!
	print "<p><b>$text{'main_none'}</b><p>\n";
	}
elsif ($gconfig{"notabs_${base_remote_user}"} == 2 ||
    $gconfig{"notabs_${base_remote_user}"} == 0 && $gconfig{'notabs'}) {
	# Generate main menu with all modules on one page
	print "<center><table cellpadding=5>\n";
	$pos = 0;
	$cols = $gconfig{'nocols'} ? $gconfig{'nocols'} : 4;
	$per = 100.0 / $cols;
	foreach $m (@modules) {
		if ($pos % $cols == 0) { print "<tr>\n"; }
		print "<td valign=top align=center width=$per\%>\n";
		local $idx = $m->{'index_link'};
		print "<table border><tr><td><a href=$gconfig{'webprefix'}/$m->{'dir'}/$idx>",
		      "<img src=$m->{'dir'}/images/icon.gif border=0 ",
          "title=\"$m->{'longdesc'}\" ",
		      "width=48 height=48></a></td></tr></table>\n";
		print "<a href=$gconfig{'webprefix'}/$m->{'dir'}/$idx>$m->{'desc'}</a></td>\n";
		if ($pos % $cols == $cols - 1) { print "</tr>\n"; }
		$pos++;
		}
	print "</table></center><p>\n";
	}
else {
	# Display under categorised tabs
	&ReadParse();
	&read_file("$config_directory/webmin.catnames", \%catnames);
	foreach $m (@modules) {
		$c = $m->{'category'};
		next if ($cats{$c});
		if (defined($catnames{$c})) {
			$cats{$c} = $catnames{$c};
			}
		elsif ($text{"category_$c"}) {
			$cats{$c} = $text{"category_$c"};
			}
		else {
			# try to get category name from module ..
			local %mtext = &load_language($m->{'dir'});
			if ($mtext{"category_$c"}) {
				$cats{$c} = $mtext{"category_$c"};
				}
			else {
				$c = $m->{'category'} = "";
				$cats{$c} = $text{"category_$c"};
				}
			}
		}
	@cats = sort { $b cmp $a } keys %cats;
	$cats = @cats;
	$per = $cats ? 100.0 / $cats : 100;
	if (!defined($in{'cat'})) {
		# Use default category
		if (defined($gconfig{'deftab'}) &&
		    &indexof($gconfig{'deftab'}, @cats) >= 0) {
			$in{'cat'} = $gconfig{'deftab'};
			}
		else {
			$in{'cat'} = $cats[0];
			}
		}
	elsif (!$cats{$in{'cat'}}) {
		$in{'cat'} = "";
		}
	print "<table border=0 cellpadding=0 cellspacing=0 height=20><tr>\n";
	$usercol = defined($gconfig{'cs_header'}) ||
		   defined($gconfig{'cs_table'}) ||
		   defined($gconfig{'cs_page'});
	foreach $c (@cats) {
		$t = $cats{$c};
		if ($in{'cat'} eq $c) {
			print "<td valign=top>", $usercol, "</td>\n";
			print "<td id='menubar'>&nbsp;<b>$t</b>&nbsp;</td>\n";
			print "<td valign=top>", $usercol, "</td>\n";
			}
		else {
			print "<td valign=top>", $usercol, "</td>\n";
			print "<td id='menubarun'>&nbsp;",
			      "<a href=$gconfig{'webprefix'}/?cat=$c title=\"$text{'longcategory_' . $c}\"><b>$t</b></a>&nbsp;</td>\n";
			print "<td valign=top>", $usercol, "</td>\n";
			}
		print "<td width=10></td>\n";
		}
	print "</tr></table> <table cellpadding=0 cellspacing=0 ",
              "width=100% $cb>\n";
	print "<tr><td><table id='main' width=100% cellpadding=5>\n";

	# Display the modules in this category
	$pos = 0;
	$cols = $gconfig{'nocols'} ? $gconfig{'nocols'} : 4;
	$per = 100.0 / $cols;
	foreach $m (@modules) {
		next if ($m->{'category'} ne $in{'cat'});

		if ($pos % $cols == 0) { print "<tr>\n"; }
		local $idx = $m->{'index_link'};
		print "<td valign=top align=center width=$per\%>\n";
		print "<table><tr><td><a href=$gconfig{'webprefix'}/$m->{'dir'}/$idx>",
		      "<img src=$m->{'dir'}/images/icon.gif title=\"$m->{'longdesc'}\" border=0></a>",
		      "</td></tr></table>\n";
		print "<a href=$gconfig{'webprefix'}/$m->{'dir'}/$idx>$m->{'desc'}</a></td>\n";
		if ($pos++ % $cols == $cols - 1) { print "</tr>\n"; }
		}
	while($pos++ % $cols) {
		print "<td width=$per\%></td>\n";
		}
	print "</table></td></tr></table><p>\n";
	}

if ($miniserv{'logout'} && !$gconfig{'alt_startpage'} &&
    !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} && !$ENV{'ANONYMOUS_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	print "<table width=100% cellpadding=0 cellspacing=0><tr>\n";
	if ($main::session_id) {
		print "<td align=right><a href='session_login.cgi?logout=1'>",
		      "$text{'main_logout'}</a></td>\n";
		}
	else {
		print "<td align=right><a href=switch_user.cgi>",
		      "$text{'main_switch'}</a></td>\n";
		}
	print "</tr></table>\n";
	}

print $text{'main_footer'};
&footer();

