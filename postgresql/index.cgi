#!/usr/local/bin/perl
# index.cgi
# Display all existing databases

require './postgresql-lib.pl';

# Check for PostgreSQL program
if (!-x $config{'psql'}) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_esql', "<tt>$config{'psql'}</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}

$r = &is_postgresql_running();
if ($r == 0) {
	# Not running .. need to start it
	&main_header();
	print "<p> <b>$text{'index_notrun'}</b> <p>\n";
	}
elsif ($r == -1) {
	# Running, but user hasn't logged in yet
	&main_header();
	print "<center><p> <b>$text{'index_nopass'}</b> <p>\n";
	print "<form action=login.cgi method=post>\n";
	print "<table border>\n";
	print "<tr $tb> <td><b>$text{'index_ltitle'}</b></td> </tr>\n";
	print "<tr $cb> <td><table cellpadding=2>\n";

	print "<tr> <td><b>$text{'index_login'}</b></td>\n";
	printf "<td><input name=login size=20 value='%s'></td> </tr>\n",
		$userconfig{'login'};

	print "<tr> <td><b>$text{'index_pass'}</b></td>\n";
	print "<td><input name=pass size=20 type=password></td> </tr>\n";

	print "</table></td></tr></table>\n";
	print "<input type=submit value='$text{'save'}'>\n";
	print "<input type=reset value='$text{'index_clear'}'>\n";
	print "</center></form>\n";
	}
elsif ($r == -2) {
	# Looks like a shared library problem
	&main_header();
	print &text('index_elibrary', "<tt>$config{'psql'}</tt>"),"<p>\n";
	print "<p>",&text('index_ldpath', "<tt>$ENV{$gconfig{'ld_env'}}</tt>",
			  "<tt>$config{'psql'}</tt>"),"<br>\n";
	print "<pre>$out</pre>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}
else {
	# Check if we can re-direct to a single DB's page
	@titles = grep { &can_edit_db($_) } &list_databases();
	if (@titles == 1) {
		# Only one DB, so go direct to it!
		&redirect("edit_dbase.cgi?db=$titles[0]");
		exit;
		}

	# Running .. check version
	$postgresql_version = &get_postgresql_version();
	&main_header();
	if (!$postgresql_version) {
	        print &text('index_superuser'),"<p>\n";
		&ui_print_footer("/", $text{'index'});
		exit;
		}
	if ($postgresql_version < 6.5) {
		print &text('index_eversion', $postgresql_version, 6.5),
		      "<p>\n";
		&ui_print_footer("/", $text{'index'});
		exit;
		}

	# List the databases
	print &ui_subheading($text{'index_dbs'});
	@icons = map { "images/db.gif" } @titles;
	@links = map { "edit_dbase.cgi?db=$_" } @titles;
	if (!@titles) {
		print "<b>$text{'index_nodbs'}</b> <p>\n";
		}
	elsif ($displayconfig{'style'}) {
		@tables = map { if (&accepting_connections($_)) {
					my @t = &list_tables($_);
					scalar(@t);
					}
				else {
					"-";
					}
				} @titles;
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

&ui_print_footer("/", "index");

sub main_header
{
&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
	undef, undef, undef, $postgresql_version ?
		&text('index_version', $postgresql_version) : undef);
}

