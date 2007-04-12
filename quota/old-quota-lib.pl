# quota-lib.pl
# Functions for getting user quotas

do '../web-lib.pl';
&init_config();
&switch_to_remote_user();
require '../ui-lib.pl';
if ($gconfig{'os_type'} =~ /^\S+\-linux$/) {
	do "linux-lib.pl";
	}
else {
	do "$gconfig{'os_type'}-lib.pl";
	}

# print_limit(amount, no-blocks)
sub print_limit
{
if ($_[0] == 0) { print "<td>$text{'quota_unlimited'}</td>\n"; }
elsif ($bsize && !$_[1]) { print "<td>",&nice_size($_[0]*$bsize),"</td>"; }
else { print "<td>$_[0]</td>\n"; }
}

sub print_grace
{
print "<td>",($_[0] || "<br>"),"</td>\n";
}



1;

