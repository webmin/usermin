#!/usr/local/bin/perl
# setup.cgi
# Calls ssh-keygen for the user

require './ssh-lib.pl';
&ReadParse();
&error_setup($text{'setup_err'});

# Check for openssh version 3.4 or above
$type = $in{'type'} ? "-t $in{'type'}" : "";

$out = `echo '' | ssh-keygen $type -P \"$in{'pass'}\" 2>&1`;
if ($?) {
	&error("<pre>$out</pre>");
	}
if  (-r "$ssh_directory/id_rsa.pub") {
	system("cp $ssh_directory/id_rsa.pub $ssh_directory/authorized_keys");
	}
else {
	if (-r "$ssh_directory/identity.pub") {
		system("cp $ssh_directory/identity.pub $ssh_directory/authorized_keys");
		}
	else {
		system("cp $ssh_directory/id_dsa.pub $ssh_directory/authorized_keys");
		}
	}
&redirect("");

