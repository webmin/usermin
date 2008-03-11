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
if (!@conf) {
	print "<b>$text{'index_none'}</b><p>\n";
	}
&show_polls(\@conf, $fetchmail_config, $remote_user_info[0]);

if (@conf) {
	# Show the fetchmail daemon form
	print "<hr>\n";
	print &ui_buttons_start();

	if (&foreign_check("cron") && $can_cron) {
		# Show button to manage cron job
		print &ui_buttons_row("edit_cron.cgi",
				      $text{'index_cron'},
				      $text{'index_crondesc'});
		}

	if ($can_daemon) {
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
			print &ui_buttons_row("stop.cgi",
				$text{'index_stop'},
				&text('index_stopmsg',$interval));
			}
		else {
			# daemon isn't running - offer to start it
			print &ui_buttons_row("start.cgi",
				$text{'index_start'},
				&text('index_startmsg',
				      &ui_textbox("interval", 60, 5)));
			}
		}
	print &ui_buttons_end();
	}

&ui_print_footer("/", $text{'index'});

