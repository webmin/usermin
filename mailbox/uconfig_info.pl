
do 'mailbox-lib.pl';

# If addressbook whitelisting is enabled, update the whitelist
sub config_post_save
{
&addressbook_to_whitelist();
}
