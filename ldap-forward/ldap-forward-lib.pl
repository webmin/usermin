# Functions for editing the current user's LDAP mail forwarding address

do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");

1;

