# freebsd-lib.pl
# Functions for changing user details on FreeBSD

# change_details(realname, office, ophone, hphone, shell)
sub change_details
{
#&switch_to_remote_user();
$ENV{'EDITOR'} = "$module_root_directory/editor.pl";
$ENV{'EDITOR_REAL'} = $_[0];
$ENV{'EDITOR_OFFICE'} = $_[1];
$ENV{'EDITOR_OPHONE'} = $_[2];
$ENV{'EDITOR_HPHONE'} = $_[3];
$ENV{'EDITOR_SHELL'} = $_[4];
local $out = `chfn $remote_user 2>&1`;
return $? ? $out : undef;
}

