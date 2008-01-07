#!/usr/local/bin/perl
# index.cgi
# Display all existing databases

require './mysql-lib.pl';

# Check for MySQL programs
if (!-x $config{'mysqladmin'}) {
	&main_header();
	print &text('index_eadmin',
			  "<tt>$config{'mysqladmin'}</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}
if (!-x $config{'mysql'}) {
	&main_header();
	print &text('index_esql',
			  "<tt>$config{'mysql'}</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}
$out = `$config{'mysql'} -V 2>&1`;
if ($out =~ /lib\S+\.so/) {
	&main_header();
	print &text('index_elibrary',
			  "<tt>$config{'mysql'}</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}
elsif ($out !~ /distrib\s+((3|4|5)\.[0-9\.]*)/i) {
	&main_header();
	print &text('index_ever', "<tt>$config{'mysql'}</tt>"),"<p>\n";
	print &text('index_mysqlver', "$config{'mysql'} -V"),"\n";
	print "<pre>$out</pre>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}
$mysql_version = $1;
open(VERSION, ">$user_module_config_directory/version");
print VERSION $mysql_version,"\n";
close(VERSION);

if (!$userconfig{'login'} && $config{'useident'} != "yes") {
	# User has not set his password yet
	$needpass = 1;
	}
else {
	$r = &is_mysql_running();
	if ($r == 0) {
		# Not running
		&main_header();
		print "<p> <b>$text{'index_notrun'}</b> <p>\n";
		}
	elsif ($r == -1) {
		# Running, but wrong password
		$needpass = 1;
		}
	else {
		# Check if we can re-direct to a single DB's page
		@titles = grep { &can_edit_db($_) } &list_databases();
		if (@titles == 1) {
			# Only one DB, so go direct to it!
			&redirect("edit_dbase.cgi?db=$titles[0]");
			exit;
			}
		
		# Running .. list databases
		&main_header();
		print &ui_subheading($text{'index_dbs'});
		@icons = map { "images/db.gif" } @titles;
		@links = map { "edit_dbase.cgi?db=$_" } @titles;
		if (!@titles) {
			print "<b>$text{'index_nodbs'}</b> <p>\n";
			}
		elsif ($displayconfig{'style'}) {
			@tables = map { @t = &list_tables($_); scalar(@t) }
				      @titles;
			@titles = map { &html_escape($_) } @titles;
			&split_table([ $text{'index_db'},
				       $text{'index_tables'} ],
				     undef, \@links, \@titles, \@tables)
				if (@titles);
			}
		else {
			@titles = map { &html_escape($_) } @titles;
			&icons_table(\@links, \@titles, \@icons);
			}

		# Check if the user can create databases
		#print "<a href=newdb_form.cgi>$text{'index_add'}</a> <p>\n";
		}
	}

if ($needpass) {
	# Need to ask for the password
	&main_header();
	print "<center>\n";
	print "<p> <b>$text{'index_nopass'}</b> <p>\n";
	print "<form action=login.cgi>\n";
	print "<table border>\n";
	print "<tr $tb> <td><b>$text{'index_ltitle'}</b></td> </tr>\n";
	print "<tr $cb> <td><table cellpadding=2>\n";
	print "<tr> <td><b>$text{'index_login'}</b></td>\n";
	printf "<td><input name=login size=20 value='%s'></td> </tr>\n",
		$userconfig{'login'} ? $userconfig{'login'} : $remote_user;
	print "<tr> <td><b>$text{'index_pass'}</b></td>\n";
	printf "<td><input name=pass size=20 type=password value='%s'></td>\n",
		$userconfig{'pass'};
	print "</tr> </table></td></tr></table>\n";
	print "<input type=submit value='$text{'save'}'>\n";
	print "<input type=reset value='$text{'index_clear'}'>\n";
	print "</center></form>\n";

	}

&ui_print_footer("/", "index");

sub main_header
{
&ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);
}

