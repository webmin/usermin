# Checks if Terminal link should be printed in Webmin menu

require "xterm-lib.pl";

sub allow_menu_link
{
my @uinfo = @remote_user_info;
@uinfo = getpwnam($remote_user) if (!@uinfo);
return 0 if (!$uinfo[8]);
return 0 if ($uinfo[8] =~ /(nologin|false|null|sync)$/);
return 1;
}

1;