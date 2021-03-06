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

# Get and check the version
$mysql_version = &get_mysql_version(\$out);
if ($mysql_version < 0) {
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

if (!$userconfig{'login'} && $config{'useident'} ne "yes") {
	# User has not set his password yet
	$needpass = 1;
	}
else {
	($r, $rout) = &is_mysql_running();
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
		}
	}

if ($needpass) {
	# Need to ask for the password
	&main_header();

        print "<b>$text{'index_nopass'}</b> <p>\n";

        print &ui_form_start("login.cgi", "post");
        print &ui_table_start($text{'index_ltitle'}, undef, 2);

        print &ui_table_row($text{'index_login'},
                &ui_textbox("login", $userconfig{'login'} || $remote_user, 40));

        print &ui_table_row($text{'index_pass'},
                &ui_password("pass", $userconfig{'pass'}, 40));

        print &ui_table_end();
        print &ui_form_end([ [ undef, $text{'save'} ] ]);

	if ($rout) {
		print &text('index_emsg', "<tt>$rout</tt>"),"<p>\n";
		}
	}

&ui_print_footer("/", "index");

sub main_header
{
&ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);
}

