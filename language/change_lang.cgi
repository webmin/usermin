#!/usr/local/bin/perl
# change_lang.cgi
# Change the language for this user

require './language-lib.pl';
&ReadParse();

# Language
if ($in{'lang'}) {
	$gconfig{"langauto_$remote_user"} = int($in{'langauto'});
	$gconfig{"lang_$remote_user"} = $in{'lang'};
	}
else {
	delete($gconfig{'lang_'.$remote_user});
	}
# Locale
if ($in{'locale'}) {
	$gconfig{"locale_$remote_user"} = $in{'locale'};
	}
else {
	delete($gconfig{'locale_'.$remote_user});
	}
&write_file("$config_directory/config", \%gconfig);
&redirect("");

