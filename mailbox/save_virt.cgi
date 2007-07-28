#!/usr/local/bin/perl
# Create, modify or delete a virtual folder

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
if (!$in{'new'}) {
	$folder = $folders[$in{'idx'}];
	$old = { %$folder };
	}
&error_setup($text{'save_err'});

if ($in{'delete'}) {
	# Just delete this folder file
	&delete_folder($old);
	}
else {
	# Validate inputs
	$in{'name'} =~ /\S/ || &error($text{'save_ename'});
	&parse_folder_options($folder, 0, \%in);

	# Save the folder
	$folder->{'type'} = 6;
	$folder->{'name'} = $in{'name'};
	$folder->{'delete'} = $in{'deletesub'};
	$folder->{'perpage'} = $in{'perpage_def'} ? undef : $in{'perpage'};
	$folder->{'fromaddr'} = $in{'fromaddr_def'} ? undef : $in{'fromaddr'};
	$folder->{'sent'} = $in{'sent'};
	&save_folder($folder, $old);
	}
&redirect($config{'mail_system'} == 4 ? "list_ifolders.cgi"
				      : "list_folders.cgi");
