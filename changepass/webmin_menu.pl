# Returns just the change password link

require "changepass-lib.pl";

sub list_webmin_menu
{
my @rv;
push(@rv, { 'type' => 'item',
	    'icon' => '/'.$module_name.'/images/changepass.gif',
	    'id' => 'changepass',
	    'desc' => $text{'left_changepass'},
	    'priority' => -1,
	    'link' => '/'.$module_name.'/', });
return @rv;
}
