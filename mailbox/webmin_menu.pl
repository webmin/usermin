# Function to get the desired menu of folders, for use by themes

require "mailbox-lib.pl";

sub list_webmin_menu
{
my ($fromaddr) = &mailbox::split_addresses(
		&mailbox::get_preferred_from_address());
my @rv;
my @folders = &list_folders_sorted();
my $df = $userconfig{'default_folder'};
my $dfolder = $df ? &find_named_folder($df, \@folders) :
                    $folders[0];

# All the user's folders
foreach my $f (@folders) {
	my $fid = &folder_name($f);
	my $item = { 'type' => 'item',
		     'id' => $fid,
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
	push(@rv, $item);
	}
push(@rv, { 'type' => 'hr' });

# Search box
push(@rv, { 'type' => 'input',
	    'id' => 'search',
	    'name' => 'search',
	    'size' => 15,
	    'desc' => $text{'mail_search2'},
	    'cgi' => '/'.$module_name.'/mail_search.cgi',
	    'hidden' => [ [ 'simple', 1 ],
			  [ 'folder', $dfolder->{'index'} ],
			  [ 'id', undef ] ],
	  });

# Folder list link
my $fprog = $mconfig{'mail_system'} == 4 ? "list_ifolders.cgi"
					 : "list_folders.cgi";
push(@rv, { 'type' => 'item',
	    'id' => 'folders',
	    'desc' => $text{'mail_folders'},
	    'link' => '/'.$module_name.'/'.$fprog });

# Address book link
# XXX

# Module config link
# XXX

# Mail filter links
# XXX

# Edit signature link
# XXX

return @rv;
}

1;
