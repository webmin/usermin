#!/usr/bin/env perl
# Update Usermin config links to Webmin (for given modules)

use strict;
use warnings;

# Load libs
BEGIN { push( @INC, "." ); }
use WebminCore;

# Run the update
my @modules = ( 'at', 'cron', 'man', 'mysql', 'postgresql', 'proc', 'quota' );
foreach my $module (@modules) {
    print "Creating symlinks configs for \`$module\` module..", "\n";
    my $rs = 0;
    foreach my $config ( glob("../webadmin/$module/config-*") ) {
        ($config) = $config =~ /([^\/]*$)/;
        if ( !-e "$module/$config" ) {
            print "  $module/$config", "\n";
            symlink_file( "../../webadmin/$module/$config",
                          "$module/$config" );
            $rs++;
            }
        }
    print $rs ? "..done" : "..already updated", "\n\n";
    }
