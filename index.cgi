#!/usr/local/bin/perl

require './web-lib.pl';
&init_config();
&ReadParse();
$hostname = &get_display_hostname();
$ver = &get_webmin_version();
&get_miniserv_config(\%miniserv);
if ($gconfig{'real_os_type'}) {
	$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
	}
else {
	$ostr = "$gconfig{'os_type'} $gconfig{'os_version'}";
	}

# Build a list of all modules
@modules = &get_available_module_infos(1);
if (!defined($in{'cat'})) {
        # Maybe redirect to some module after login
        local $goto = &get_goto_module(\@modules);
        if ($goto) {
                &redirect($goto->{'dir'}.'/');
                exit;
                }
        }

$gconfig{'sysinfo'} = 0 if ($gconfig{'sysinfo'} == 1);
if ($gconfig{'texttitles'}) {
	@args = ( $text{'main_title2'}, undef );
	}
else {
	@args = ( $gconfig{'nohostname'} ? $text{'main_title2'} :
		    &text('main_title', $ver, $hostname, $ostr),
		  "images/usermin.gif" );
	}
&header(@args, undef, undef, 1, 1,
	$tconfig{'brand'} ? 
	"<a href=$tconfig{'brand_url'}>$tconfig{'brand'}</a>" :
	$gconfig{'brand'} ? 
	"<a href=$gconfig{'brand_url'}>$gconfig{'brand'}</a>" :
	"<a href=http://www.usermin.com/>$text{'main_homepage'}</a>".
	($gconfig{'feedback'} ? "<br><a href=feedback_form.cgi>$text{'main_feedback'}</a>" : "")
	);
print "<center><font size=+1>",
	    &text('main_version', $ver, $hostname, $ostr),"</font></center>\n"
		if (!$gconfig{'nohostname'});
print "<hr><p>\n";
print $text{'main_header'};

if (!@modules) {
	# use has no modules!
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
		      "width=48 height=48></a></td></tr></table>\n";
		print "<a href=$gconfig{'webprefix'}/$m->{'dir'}/$idx>$m->{'desc'}</a></td>\n";
		if ($pos % $cols == $cols - 1) { print "</tr>\n"; }
		$pos++;
		}
	print "</table></center><p><hr>\n";
	}
else {
	# Display under categorised tabs
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
			print "<td valign=top $cb>", $usercol ? "<br>" :
			  "<img src=images/lc2.gif alt=\"\">","</td>\n";
			print "<td $cb>&nbsp;<b>$t</b>&nbsp;</td>\n";
			print "<td valign=top $cb>", $usercol ? "<br>" :
			  "<img src=images/rc2.gif alt=\"\">","</td>\n";
			}
		else {
			print "<td valign=top $tb>", $usercol ? "<br>" :
			  "<img src=images/lc1.gif alt=\"\">","</td>\n";
			print "<td $tb>&nbsp;",
			      "<a href=$gconfig{'webprefix'}/?cat=$c><b>$t</b></a>&nbsp;</td>\n";
			print "<td valign=top $tb>", $usercol ? "<br>" :
			  "<img src=images/rc1.gif alt=\"\">","</td>\n";
			}
		print "<td width=10></td>\n";
		}
	print "</tr></table> <table border=0 cellpadding=0 cellspacing=0 ",
              "width=100% $cb>\n";
	print "<tr><td><table width=100% cellpadding=5>\n";

	# Display the modules in this category
	$pos = 0;
	$cols = $gconfig{'nocols'} ? $gconfig{'nocols'} : 4;
	$per = 100.0 / $cols;
	foreach $m (@modules) {
		next if ($m->{'category'} ne $in{'cat'});

		if ($pos % $cols == 0) { print "<tr>\n"; }
		print "<td valign=top align=center width=$per\%>\n";
		print "<table border bgcolor=#ffffff><tr><td><a href=$gconfig{'webprefix'}/$m->{'dir'}/>",
		      "<img src=$m->{'dir'}/images/icon.gif alt=\"\" border=0></a>",
		      "</td></tr></table>\n";
		print "<a href=$gconfig{'webprefix'}/$m->{'dir'}/>$m->{'desc'}</a></td>\n";
		if ($pos++ % $cols == $cols - 1) { print "</tr>\n"; }
		}
	while($pos++ % $cols) {
		print "<td width=$per\%></td>\n";
		}
	print "</table></td></tr></table><p><hr>\n";
	}

if ($miniserv{'logout'} && !$gconfig{'alt_startpage'} &&
    !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
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

