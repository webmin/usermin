#!/usr/local/bin/perl
# Create, update or delete an IMAP folder

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();

# Get or create the folder object
if ($in{'new'}) {
	$folder = { 'type' => 4,
		    'imapauto' => 1,
		    'server' => $folders[0]->{'server'},
		    'user' => $folders[0]->{'user'},
		    'pass' => $folders[0]->{'pass'},
		  };
	}
else {
	$folder = $folders[$in{'idx'}];
	}

if ($in{'delete'}) {
	# Delete the folder (on the server), after asking for confirmation
	if ($in{'confirm'}) {
		# Do the delete
		&delete_folder($folder);
		}
	else {
		# Ask first
		&ui_print_header(undef, $text{'save_title'}, "");

		print "<center>\n";
		print &ui_form_start("save_ifolder.cgi");
		print &ui_hidden("idx", $in{'idx'}),"\n";
		print &ui_hidden("delete", 1),"\n";
		$sz = &nice_size(&folder_size($folder));
		print &text('save_rusure2', $folder->{'name'}, $sz),"<p>\n";
		print &ui_form_end([ [ "confirm", $text{'save_delete'} ] ]);
		print "</center>\n";

		&ui_print_footer("list_ifolders.cgi", $text{'folders_return'});
		exit;
		}
	}
else {
	# Validate and store inputs
	if ($in{'new'} || $in{'name'} ne $folder->{'name'}) {
		$in{'name'} =~ /^[a-z0-9\.\-\/]+$/ ||
			&error($text{'save_ename'});
		$in{'name'} =~ /\.\./ && 
			&error($text{'save_ename2'});
		lc($in{'name'}) eq 'inbox' && 
			&error($text{'save_ename3'});
		($clash) = grep { lc($_->{'name'}) eq lc($in{'name'}) }
				@folders;
		$clash && &error($text{'save_eclash'});
		$folder->{'name'} = $in{'name'};
		}
	&parse_folder_options($folder, 4, \%in);
	&save_folder($folder);
	}

&redirect("list_ifolders.cgi");

