#!/usr/local/bin/perl
# change_lang.cgi
# Change the language for this user

require './language-lib.pl';
&ReadParse();

if ($in{'lang'}) {
	$gconfig{"langauto_$remote_user"} = int($in{'langauto'});
	$gconfig{"lang_$remote_user"} = $in{'lang'};
	}
else {
	delete($gconfig{'lang_'.$remote_user});
	}
&write_file("$config_directory/config", \%gconfig);
&redirect("");

