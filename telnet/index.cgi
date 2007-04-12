#!/usr/local/bin/perl
# index.cgi
# Display the telnet applet

require '../web-lib.pl';
use Socket;
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();
$theme_no_table = 1 if ($userconfig{'sizemode'} == 1);
&ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

# Are we running SSH or telnet
$telnet_port = $config{'telnet_port'} || 23;
$ssh_port = $config{'ssh_port'} || 22;
$port = $ssh_port;
$mode = 1;
socket(STEST, PF_INET, SOCK_STREAM, getprotobyname("tcp"));
$rv = connect(STEST, pack_sockaddr_in($ssh_port, inet_aton("127.0.0.1")));
close(STEST);
if (!$rv) {
	$port = $telnet_port;
	$mode = 0;
	$rv = connect(STEST, pack_sockaddr_in($telnet_port, inet_aton("127.0.0.1")));
	close(STEST);
	}
if (!$rv) {
	print "<p>$text{'index_econnect'}<p>\n";
	}
else {
	print "<center>\n";
	if ($userconfig{'detach'}) {
		$w = 100; $h = 50;
		}
	elsif ($userconfig{'sizemode'} == 2 &&
	       $userconfig{'size'} =~ /^(\d+)\s*x\s*(\d+)$/) {
		$w = $1; $h = $2;
		}
	elsif ($userconfig{'sizemode'} == 1) {
		$w = "100%"; $h = "80%";
		}
	else {
		$w = 590; $h = 360;
		}
	$jar = $userconfig{'applet'} ? "jta25.jar" : "jta20.jar";
	print "<applet archive=\"$jar\" code=de.mud.jta.Applet ",
	      "width=$w height=$h>\n";
	printf "<param name=config value=%s>\n",
		$mode ? "ssh.conf" : "telnet.conf";
	print "$text{'index_nojava'} <p>\n";
	if ($userconfig{'sizemode'}) {
		print "<param name=Terminal.resize value='screen'>\n";
		}
	if ($userconfig{'fontsize'}) {
		print "<param name=Terminal.fontSize value='$userconfig{'fontsize'}'>\n";
		}
	if ($userconfig{'detach'}) {
		print "<param name=Applet.detach value='true'>\n";
		print "<param name=Applet.detach.stopText value='Disconnect'>\n";
		}
	if ($config{'port'}) {
		print "<param name=Socket.port value=$port>\n";
		}
        if ($config{'applet'}) {
                print "<param name=Socket.host value=$ENV{'SERVER_NAME'}>\n";
                }
	print "</applet><br>\n";

	print &text('index_credits',
		    "http://www.mud.de/se/jta/"),"<br>\n";
	if ($mode) {
		print &text('index_sshcredits',
			    "http://www.systemics.com/docs/cryptix/"),"<br>\n";
		}
	print "</center>\n";
	}
&ui_print_footer("/", $text{'index'});

