#!/usr/local/bin/perl
# setup.cgi
# Calls ssh-keygen for the user

require './ssh-lib.pl';
&ReadParse();
&error_setup($text{'setup_err'});

$type = $in{'type'} ? "-t $in{'type'}" : "";

$out = &backquote_command(
	"echo '' | ssh-keygen $type -P ".
	($in{'pass'} ? quotemeta($in{'pass'}) : "''")." 2>&1");
if ($?) {
	&error("<pre>$out</pre>");
	}

# Add the new public key to the authorized keys file
$ak = "$ssh_directory/authorized_keys";
if  (-r "$ssh_directory/id_rsa.pub") {
	system("cat $ssh_directory/id_rsa.pub >>$ak");
	}
elsif (-r "$ssh_directory/identity.pub") {
	system("cat $ssh_directory/identity.pub >>$ak");
	}
else {
	system("cat $ssh_directory/id_dsa.pub >>$ak");
	}

&redirect("");

