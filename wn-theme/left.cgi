#!/usr/local/bin/perl
# Show modules available to this user, plus a logout button. For the Read Mail
# module, show folders too

do './web-lib.pl';
&init_config();

&PrintHeader();
local $bgcolor = defined($tconfig{'cs_page'}) ? $tconfig{'cs_page'} :
		 defined($gconfig{'cs_page'}) ? $gconfig{'cs_page'} : "ffffff";
local $link = defined($tconfig{'cs_link'}) ? $tconfig{'cs_link'} :
	      defined($gconfig{'cs_link'}) ? $gconfig{'cs_link'} : "0000ee";
local $text = defined($tconfig{'cs_text'}) ? $tconfig{'cs_text'} : 
	      defined($gconfig{'cs_text'}) ? $gconfig{'cs_text'} : "000000";
print "<html><body bgcolor=#$bgcolor link=#$link vlink=#$link text=#$text>\n";
print "<table cellpadding=0 cellspacing=1 width=140>\n";

# Show username
if ($remote_user =~ /^(\S+)\@(\S+)$/) {
	print "<tr> <td><tt>$1\@<br>$2</tt></td> </tr>\n";
	}
else {
	print "<tr> <td><tt>$remote_user</tt></td> </tr>\n";
	}

@mods = &get_available_module_infos();
($mailbox) = grep { $_->{'dir'} eq 'mailbox' } @mods;
if ($mailbox) {
	# Show mail folders first
	@mods = grep { $_ ne $mailbox } @mods;
	&foreign_require("mailbox", "mailbox-lib.pl");
	print "<tr> <td><table border width=100%><tr><td>\n";
	print "<b>Mail Folders</b><br>\n";
	foreach $f (&mailbox::list_folders()) {
		print "&nbsp;&nbsp;\n";
		print "<a href='/mailbox/index.cgi?folder=$f->{'index'}' target=body>$f->{'name'}</a><br>\n";
		}
	print "</td></tr></table></td> </tr>\n";
	}

# Show other modules
foreach $m (@mods) {
	print "<tr> <td><table border width=100%><tr><td>\n";
	print "<a href='/$m->{'dir'}/' target=body><b>$m->{'desc'}</b></a>";
	print "</td></tr></table></td> </tr>\n";
	}

# Show logout button
print "<tr> <td><table border width=100%><tr><td>\n";
if ($main::session_id) {
	print "<a href='session_login.cgi?logout=1' target=_top>",
	      "$text{'main_logout'}</a>";
	}
else {
	print "<a href=switch_user.cgi target=_top>",
	      "$text{'main_switch'}</a>";
	}
print "</td></tr></table></td> </tr>\n";

print "</table>\n";
print "</body></html>\n";

1;

