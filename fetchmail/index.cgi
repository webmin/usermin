#!/usr/local/bin/perl
# index.cgi
# Show fetchmail configurations

require './fetchmail-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

# Check if fetchmail is installed
if (!&has_command($config{'fetchmail_path'})) {
	print &text('index_efetchmail',
			  "<tt>$config{'fetchmail_path'}</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}

@conf = &parse_config_file($fetchmail_config);
@conf = grep { $_->{'poll'} } @conf;
&show_polls(\@conf, $fetchmail_config, $remote_user_info[0]);

if (@conf) {
	# Show the fetchmail daemon form
	print "<hr>\n";
	print "<table width=100%>\n";

	if (&foreign_check("cron")) {
		# Show button to manage cron job
		print "<form action=edit_cron.cgi>\n";
		print "<tr> <td><input type=submit ",
		      "value='$text{'index_cron'}'></td>\n";
		print "<td>$text{'index_crondesc'}</td> </tr></form>\n";
		}

	print "<tr><td>\n";
	foreach $pf ("$remote_user_info[7]/.fetchmail.pid",
		     "$remote_user_info[7]/.fetchmail") {
		if (open(PID, $pf) && ($line=<PID>) &&
		    (($pid,$interval) = split(/\s+/, $line)) && $pid &&
		    kill(0, $pid)) {
			$running = $pf;
			last;
			}
		}
	if ($running) {
		# daemon is running - offer to stop it
		print "<form action=stop.cgi>\n";
		print "<input type=submit value='$text{'index_stop'}'></td>\n";
		print "<td>",&text('index_stopmsg', $interval),"</td>\n";
		}
	else {
		# daemon isn't running - offer to start it
		print "<form action=start.cgi>\n";
		print "<input type=submit value='$text{'index_start'}'></td>\n";
		print "<td>",&text('index_startmsg',
			   "<input name=interval size=5 value='60'>"),"</td>\n";
		}
	print "</td></tr></table></form>\n";
	}

&ui_print_footer("/", $text{'index'});

