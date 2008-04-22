#!/usr/local/bin/perl
# mail_search.cgi
# Find mail messages matching some pattern

require './mailbox-lib.pl';
&ReadParse();
$limit = { };
if (!$in{'status_def'} && defined($in{'status'})) {
	$statusmsg = &text('search_withstatus',
			   $text{'view_mark'.$in{'status'}});
	}
if ($in{'simple'}) {
	# Make sure a search was entered
	$in{'search'} || &error($text{'search_ematch'});
	if ($userconfig{'search_latest'}) {
		$limit->{'latest'} = $userconfig{'search_latest'};
		}
	}
elsif ($in{'spam'}) {
	# Make sure a spam score was entered
	$in{'score'} =~ /^\d+$/ || &error($text{'search_escore'});
	}
else {
	# Validate search fields
	for($i=0; defined($in{"field_$i"}); $i++) {
		if ($in{"field_$i"}) {
			$in{"what_$i"} || &error(&text('search_ewhat', $i+1));
			$neg = $in{"neg_$i"} ? "!" : "";
			push(@fields, [ $neg.$in{"field_$i"}, $in{"what_$i"} ]);
			}
		}
	@fields || $statusmsg || &error($text{'search_enone'});
	if (!defined($in{'limit'})) {
		if ($userconfig{'search_latest'}) {
			$limit = { 'latest' => $userconfig{'search_latest'} };
			}
		}
	elsif (!$in{'limit_def'}) {
		$in{'limit'} =~ /^\d+$/ || &error($text{'search_elatest'});
		$limit->{'latest'} = $in{'limit'};
		}
	}
if ($limit && $limit->{'latest'}) {
	$limitmsg = &text('search_limit', $limit->{'latest'});
	}

@folders = &list_folders();
if ($in{'id'}) {
	$folder = &find_named_folder($in{'id'}, \@folders);
	$folder || &error("Failed to find folder $in{'id'}");
	$in{'folder'} = $folder->{'index'};
	}
elsif ($in{'folder'} >= 0) {
	$folder = $folders[$in{'folder'}];
	}
if ($folder && $folder->{'id'} eq $search_folder_id) {
	# Cannot search searchs!
	&error($text{'search_eself'});
	}

if ($in{'simple'}) {
	# Just search by Subject and From (or To) in one folder
	($mode, $words) = &parse_boolean($in{'search'});
	local $who = $folder->{'sent'} ? 'to' : 'from';
	if ($mode == 0) {
		# Search was like 'foo' or 'foo bar'
		# Can just do a single 'or' search
		@searchlist = map { ( [ 'subject', $_ ],
				      [ $who, $_ ] ) } @$words;
		@rv = &mailbox_search_mail(\@searchlist, 0, $folder, $limit, 1);
		}
	elsif ($mode == 1) {
		# Search was like 'foo and bar'
		# Need to do two 'and' searches and combine
		@searchlist1 = map { ( [ 'subject', $_ ] ) } @$words;
		@rv1 = &mailbox_search_mail(\@searchlist1, 1, $folder,
					    $limit, 1);
		@searchlist2 = map { ( [ $who, $_ ] ) } @$words;
		@rv2 = &mailbox_search_mail(\@searchlist2, 1, $folder,
					    $limit, 1);
		@rv = @rv1;
		%gotid = map { $_->{'id'}, 1 } @rv;
		foreach $mail (@rv2) {
			push(@rv, $mail) if (!$gotid{$mail->{'id'}});
			}
		}
	else {
		&error($text{'search_eboolean'});
		}
	foreach $mail (@rv) {
		$mail->{'folder'} = $folder;
		}
	if ($statusmsg) {
		@rv = &filter_by_status(\@rv, $in{'status'});
		}
	$msg = &text('search_msg2', $in{'search'});
	}
elsif ($in{'spam'}) {
	# Search by spam score, using X-Spam-Level header
	$stars = "*" x $in{'score'};
	@rv = &mailbox_search_mail([ [ "x-spam-level", $stars ] ], 0, $folder,
				   $limit, 1);
	foreach $mail (@rv) {
		$mail->{'folder'} = $folder;
		}
	$msg = &text('search_msg5', $in{'score'});
	}
else {
	# Complex search, perhaps over multiple folders!
	if ($in{'folder'} == -2) {
		# All local folders, except composite and virtual
		@sfolders = grep { !$_->{'remote'} &&
				   $_->{'type'} != 5 &&
				   $_->{'type'} != 6 } @folders;
		$multi_folder = 1;
		}
	elsif ($in{'folder'} == -1) {
		# All folders, except composite and virtual
		@sfolders = grep { $_->{'type'} != 5 &&
				   $_->{'type'} != 6 } @folders;
		$multi_folder = 1;
		}
	else {
		@sfolders = ( $folder );
		}
	foreach $sf (@sfolders) {
		local @frv = &mailbox_search_mail(\@fields, $in{'and'}, $sf,
						  $limit, 1);
		foreach $mail (@frv) {
			$mail->{'folder'} = $sf;
			}
		push(@rv, @frv);
		}
	if ($statusmsg) {
		@rv = &filter_by_status(\@rv, $in{'status'});
		}
	$msg = $text{'search_msg4'};
	}
$msg .= " $limitmsg" if ($limitmsg);
$msg .= " $statusmsg" if ($statusmsg);

# Create a virtual folder for the search results
if ($in{'dest_def'} || !defined($in{'dest'})) {
	# Use the default search results folder
	($virt) = grep { $_->{'type'} == 6 && $_->{'id'} == 1 } @folders;
	if (!$virt) {
		$virt = { 'id' => $search_folder_id,
			  'type' => 6,
			};
		}
	$virt->{'name'} = $text{'search_title'};
	}
else {
	# Create a new virtual folder
	$in{'dest'} || &error($text{'search_edest'});
	$virt = { 'type' => 6,
		  'name' => $in{'dest'} };
	}
$virt->{'delete'} = 1;
$virt->{'members'} = [ map { [ $_->{'folder'}, $_->{'id'} ] } @rv ];
$virt->{'msg'} = $msg;
if ($folder) {
	# Use same From/To display mode as original folder
	$virt->{'show_to'} = $folder->{'show_to'};
	$virt->{'show_from'} = $folder->{'show_from'};
	$virt->{'spam'} = $folder->{'spam'};
	$virt->{'sent'} = $folder->{'sent'};
	$virt->{'drafts'} = $folder->{'drafts'};
	}
else {
	# Use default From/To mode
	delete($virt->{'show_to'});
	delete($virt->{'show_from'});
	delete($virt->{'spam'});
	delete($virt->{'sent'});
	delete($virt->{'drafts'});
	}
&delete_new_sort_index($virt);
&save_folder($virt, $virt);

# Redirect to it
&redirect("index.cgi?id=$virt->{'id'}&refresh=2");
&pop3_logout_all();

