
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
require 'mailbox-lib.pl';
our (%text, %gconfig);

# list_system_info()
# Return some basic info about the system
sub list_system_info
{
my @table;
my $table = { 'type' => 'table',
              'desc' => $text{'right_header'},
	      'priority' => 10,
              'table' => \@table };

# Hostname
push(@table, { 'desc' => $text{'right_host'},
	       'value' => &get_display_hostname() });

# Operating system
push(@table, { 'desc' => $text{'right_os'},
               'value' => $gconfig{'os_version'} eq '*' ?
                        $gconfig{'real_os_type'} :
                        $gconfig{'real_os_type'}.' '.$gconfig{'real_os_version'}
             });

# Usermin version
push(@table, { 'desc' => $text{'right_usermin'},
	       'value' => &get_webmin_version() });

# System time
my $tm = localtime(time());
eval "use DateTime; use DateTime::Locale; use DateTime::TimeZone;";
if (!$@) {
   $tm = make_date(time(), {get => 'complete'});
   }
push(@table, { 'desc' => $text{'right_time'},
	       'value' => $tm });

return ($table);
}

1;
