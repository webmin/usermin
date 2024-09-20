
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

my $can_type = sub {
      my ($type) = @_;
      return 1 if (!defined($gconfig{'ui_show'}));
      return 1 if ($gconfig{'ui_show'} =~ /\b$type\b/);
      return 0;
      };

# Hostname
if ($can_type->('host')) {
   push(@table, { 'desc' => $text{'right_host'},
                  'value' => &get_display_hostname(),
                  'type' => 'hostname' });
   }

# Operating system
if ($can_type->('os')) {
   push(@table, { 'desc' => $text{'right_os'},
                  'value' => $gconfig{'os_version'} eq '*' ?
                           $gconfig{'real_os_type'} :
                           $gconfig{'real_os_type'}.' '.$gconfig{'real_os_version'},
                  'type' => 'os' });
   }

# Usermin version
if ($can_type->('ver')) {
   push(@table, { 'desc' => $text{'right_usermin'},
                  'value' => &get_webmin_version(),
                  'type' => 'version' });
   }

# System time
if ($can_type->('time')) {
   my $tm = localtime(time());
   eval "use DateTime; use DateTime::Locale; use DateTime::TimeZone;";
   if (!$@) {
      $tm = make_date(time(), { get => 'complete' });
      }
   push(@table, { 'desc' => $text{'right_time'},
                  'value' => $tm,
                  'type' => 'time' });
   }

return ($table);
}

1;
