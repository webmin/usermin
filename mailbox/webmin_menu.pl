# Function to get the desired menu of folders, for use by themes

require "mailbox-lib.pl";

sub list_webmin_menu
{
my @rv;

# Desired title
push(@rv, { 'type' => 'title',
	    'id' => 'title',
	    'icon' => '/'.$module_name.'/images/mail.gif',
	    'desc' => $text{'left_mail'} });

# Show real name and address
my ($fromaddr) = &mailbox::split_addresses(
		&mailbox::get_preferred_from_address());
if ($fromaddr->[1]) {
	push(@rv, { 'type' => 'text',
		    'id' => 'realname',
		    'desc' => $fromaddr->[1] });
	}
push(@rv, { 'type' => 'text',
	    'id' => 'emailaddr',
	    'desc' => $fromaddr->[0] });
push(@rv, { 'type' => 'hr' });

# Get all the folders
my @folders = &list_folders_sorted();
my $df = $userconfig{'default_folder'};
my $dfolder = $df ? &find_named_folder($df, \@folders) :
                    $folders[0];

# All the user's folders
foreach my $f (@folders) {
	# Create the folder object
	my $fid = &folder_name($f);
	my $item = { 'type' => 'item',
		     'id' => 'folder_'.$fid,
		     'desc' => $f->{'name'},
		     'link' => '/'.$module_name.
			       '/index.cgi?id='.&urlize($fid) };
	if ($f->{'type'} == 6 &&
	    $special_folder_id &&
	    $f->{'id'} == $special_folder_id) {
		$item->{'icon'} = '/'.$module_name.'/images/special.gif';
		$item->{'special'} = 1;
		}
	if (&should_show_unread($f)) {
		my ($c, $u) = &mailbox_folder_unread($f);
		$item->{'desc'} .= " ($u)" if ($u);
		}

	# Check if this is under a new heirarchy
	my $sep = $f->{'name'} =~ /\// ? "/" : "\\.";
	my $sepchar = $f->{'name'} =~ /\// ? "/" : ".";
	my @w = split($sep, $f->{'name'});
	if (@w > 1) {
		my $hname = join($sepchar, @w[0..$#w-1]);
		$item->{'desc'} =~ s/^\Q$hname$sepchar\E//;
		if ($parent && $parent->{'id'} eq $hname) {
			# Add to current parent
			push(@{$parent->{'members'}}, $item);
			}
		else {
			# Create new parent
			my $newp = { 'type' => 'cat',
				     'id' => $hname,
				     'desc' => $hname,
				     'members' => [ $item ] };
			$parent = $newp;
			push(@rv, $newp);
			}
		}
	else {
		# Add to top level
		push(@rv, $item);
		}
	}
push(@rv, { 'type' => 'hr' });

# Search box
push(@rv, { 'type' => 'input',
	    'id' => 'search',
	    'name' => 'search',
	    'size' => 10,
	    'desc' => $text{'left_search'},
	    'cgi' => '/'.$module_name.'/mail_search.cgi',
	    'hidden' => [ [ 'simple', 1 ],
			  [ 'lastfolder', 1 ],
			  [ 'folder', $dfolder->{'index'} ],
			  [ 'id', undef ] ],
	  });

# Folder list link
my $fprog = $config{'mail_system'} == 4 ? "list_ifolders.cgi"
					: "list_folders.cgi";
push(@rv, { 'type' => 'item',
	    'icon' => '/'.$module_name.'/images/mail.gif',
	    'id' => 'folders',
	    'desc' => $text{'left_folders'},
	    'link' => '/'.$module_name.'/'.$fprog });

# Address book link
push(@rv, { 'type' => 'item',
	    'icon' => '/'.$module_name.'/images/address.gif',
            'id' => 'address',
	    'desc' => $text{'left_addresses'},
	    'link' => '/'.$module_name.'/list_addresses.cgi' });

# Module config link
if ($config{'noprefs'}) {
	push(@rv, { 'type' => 'item',
		    'icon' => '/'.$module_name.'/images/usermin.gif',
		    'id' => 'config',
		    'desc' => $text{'left_prefs'},
		    'link' => '/uconfig.cgi?'.$module_name });
	}

# Mail filter links
if (&foreign_available("filter")) {
	&foreign_require("filter");
	if (!&filter::no_user_procmailrc()) {
		# Forwarding link
		if (&filter::can_simple_forward()) {
			push(@rv, { 'type' => 'item',
				    'icon' => '/'.$module_name.'/images/forward.gif',
				    'id' => 'forward',
				    'desc' => $text{'left_forward'},
			            'link' => '/filter/edit_forward.cgi' });
			}

		# Autoreply link
		if (&filter::can_simple_autoreply()) {
			push(@rv, { 'type' => 'item',
				    'icon' => '/'.$module_name.'/images/autoreply.gif',
				    'id' => 'autoreply',
				    'desc' => $text{'left_autoreply'},
			            'link' => '/filter/edit_auto.cgi' });
			}

		# Filter management
		push(@rv, { 'type' => 'item',
			    'icon' => '/'.$module_name.'/images/filters.gif',
			    'id' => 'filter',
			    'desc' => $text{'left_filter'},
			    'link' => '/filter/' });
		}
	}

# Edit signature link
push(@rv, { 'type' => 'item',
	    'icon' => '/'.$module_name.'/images/sig.gif',
            'id' => 'sig',
	    'desc' => $text{'left_sig'},
	    'link' => '/'.$module_name.'/edit_sig.cgi' });

return @rv;
}

1;
