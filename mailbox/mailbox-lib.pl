# mailbox-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();
do 'boxes-lib.pl';
do 'folders-lib.pl';

#open(DEBUG, ">>/tmp/mailbox.debug");

if ($config{'mail_qmail'}) {
	$qmail_maildir = &mail_file_style($remote_user, $config{'mail_qmail'},
					  $config{'mail_style'});
	}
else {
	$qmail_maildir = "$remote_user_info[7]/$config{'mail_dir_qmail'}";
	}
$address_book = "$user_module_config_directory/address_book";
$address_group_book = "$user_module_config_directory/address_group_book";
$folders_dir = "$remote_user_info[7]/$userconfig{'mailbox_dir'}";
%folder_types = map { $_, 1 } (split(/,/, $config{'folder_types'}),
			       split(/,/, $config{'folder_virts'}));
$search_folder_id = 1;
$special_folder_id = 2;
$auto_cmd = "$user_module_config_directory/auto.pl";

# mailbox_file()
sub mailbox_file
{
if ($config{'mail_system'} == 0) {
	return &user_mail_file(@remote_user_info);
	}
else {
	return "$qmail_maildir/";
	}
}

# decrypt_attachments(&mail)
# If the attachments on a mail are encrypted, converts them into unencrypted
# form. Returns a code and message, valid codes being: 0 = not encrypted,
# 1 = encrypted but cannot decrypt, 2 = failed to decrypt, 3 = decrypted OK
sub decrypt_attachments
{
# Check requirements for decryption
local $first = $_[0]->{'attach'}->[0];
local ($body) = grep { $_->{'type'} eq 'text/plain' || $_->{'type'} eq 'text' }
		     @{$_[0]->{'attach'}};
local $hasgpg = &has_command("gpg") && &foreign_check("gnupg");
if ($_[0]->{'header'}->{'content-type'} =~ /^multipart\/encrypted/ &&
    $first->{'type'} =~ /^application\/pgp-encrypted/ &&
    $first->{'data'} =~ /Version:\s+1/i) {
	# RFC 2015 PGP encryption of entire message
	return (1) if (!$hasgpg);
	&foreign_require("gnupg", "gnupg-lib.pl");
	local $plain;
	local $enc = $_[0]->{'attach'}->[1];
	local $rv = &foreign_call("gnupg", "decrypt_data", $enc->{'data'}, \$plain);
	return (2, $rv) if ($rv);
	$plain =~ s/\r//g;
	local $amail = &extract_mail($plain);
	&parse_mail($amail);
	$_[0]->{'attach'} = $amail->{'attach'};
	return (3);
	}

# Check individual attachments for text-only encryption
local $a;
local $cc = 0;
local $ok = 3;
foreach $a (@{$_[0]->{'attach'}}) {
	if ($a->{'type'} =~ /^(text|application\/pgp-encrypted)/i &&
	    $a->{'data'} =~ /BEGIN PGP MESSAGE/ &&
	    $a->{'data'} =~ /([\000-\377]*)(-----BEGIN PGP MESSAGE-+\r?\n([\000-\377]+)-+END PGP MESSAGE-+\r?\n)([\000-\377]*)/i) {
		local ($before, $enc, $after) = ($1, $2, $4);
		return (1) if (!$hasgpg);
		&foreign_require("gnupg", "gnupg-lib.pl");
		$cc++;
		local $pass = &gnupg::get_passphrase();
		local $plain;
		local $rv = &gnupg::decrypt_data($enc, \$plain, $pass);
		return (2, $rv) if ($rv);
		$ok = 4 if ($before =~ /\S/ || $after =~ /\S/);
		if ($a->{'type'} !~ /^text/) {
			$a->{'type'} = "text/plain";
			}
		$a->{'data'} = $before.$plain.$after;
		}
	}
return $cc ? ( $ok ) : ( 0 );
}

# check_signature_attachments(&attach, &textbody-attach)
# Checks for a signature attachment, and verifies it. Returns the signature
# status code and message.
sub check_signature_attachments
{
my ($attach, $textbody) = @_;
my ($sigcode, $sigmessage);
if (&has_command("gpg") && &foreign_check("gnupg")) {
	# Check for GnuPG signatures
	my $sig;
	foreach my $a (@$attach) {
		$sig = $a if ($a->{'type'} =~ /^application\/pgp-signature/);
		}
	if ($sig) {
		# Verify the signature against the rest of the attachment
		&foreign_require("gnupg", "gnupg-lib.pl");
		my $rest = $sig->{'parent'}->{'attach'}->[0];
		$rest->{'raw'} =~ s/\r//g;
		$rest->{'raw'} =~ s/\n/\r\n/g;
		($sigcode, $sigmessage) =
			&gnupg::verify_data($rest->{'raw'}, $sig->{'data'});
		@$attach = grep { $_ ne $sig } @$attach;
		$sindex = $sig->{'idx'};
		}
	elsif ($textbody && $textbody->{'data'} =~ /(-+BEGIN PGP SIGNED MESSAGE-+\r?\n(Hash:\s+(\S+)\r?\n\r?\n)?([\000-\377]+\r?\n)-+BEGIN PGP SIGNATURE-+\r?\n([\000-\377]+)-+END PGP SIGNATURE-+\r?\n)/i) {
		# Signature is in body text!
		my $sig = $1;
		my $text = $4;
		&foreign_require("gnupg", "gnupg-lib.pl");
		($sigcode, $sigmessage) = &gnupg::verify_data($sig);
		$body = $textbody;
		if ($sigcode == 0 || $sigcode == 1) {
			$body->{'data'} = $text;
			}
		}
	}
return ($sigcode, $sigmessage);
}

# list_addresses()
# Returns a list of address book entries, each an array reference containing
# the email address, real name, index (if editable) and From: flag
sub list_addresses
{
local @rv;
local $i = 0;
open(ADDRESS, $address_book);
while(<ADDRESS>) {
	s/\r|\n//g;
	local @sp = split(/\t/, $_);
	if (@sp >= 1) {
		push(@rv, [ $sp[0], $sp[1], $i, $sp[2] ]);
		}
	$i++;
	}
close(ADDRESS);
if ($config{'global_address'}) {
	local $gab = &group_subs($config{'global_address'});
	open(ADDRESS, $gab);
	while(<ADDRESS>) {
		s/\r|\n//g;
		local @sp = split(/\t+/, $_);
		if (@sp >= 2) {
			push(@rv, [ $sp[0], $sp[1] ]);
			}
		}
	close(ADDRESS);
	}
if ($userconfig{'sort_addrs'} == 2) {
	return sort { lc($a->[0]) cmp lc($b->[0]) } @rv;
	}
elsif ($userconfig{'sort_addrs'} == 1) {
	return sort { lc($a->[1]) cmp lc($b->[1]) } @rv;
	}
else {
	return @rv;
	}
}

# create_address(email, real name, forfrom)
# Adds an entry to the address book
sub create_address
{
&open_tempfile(ADDRESS, ">>$address_book");
&print_tempfile(ADDRESS, "$_[0]\t$_[1]\t$_[2]\n");
&close_tempfile(ADDRESS);
}

# modify_address(index, email, real name, forfrom)
# Updates some entry in the address book
sub modify_address
{
&replace_file_line($address_book, $_[0], "$_[1]\t$_[2]\t$_[3]\n");
}

# delete_address(index)
# Deletes some entry from the address book
sub delete_address
{
&replace_file_line($address_book, $_[0]);
}

# address_button(field, [form], [frommode], [realfield], [nogroups])
# Returns HTML for an address-book popup button
sub address_button
{
if (defined(&theme_address_button)) {
	return &theme_address_button(@_);
	}
local $form = @_ > 1 ? $_[1] : 0;
local $mode = @_ > 2 ? $_[2] : 0;
local $nogroups = @_ > 4 ? $_[4] : 0;
local ($rfield1, $rfield2);
if ($_[3]) {
	return "<input type=button onClick='ifield = document.forms[$form].$_[0]; rfield = document.forms[$form].$_[3]; chooser = window.open(\"../$module_name/address_chooser.cgi?addr=\"+escape(ifield.value)+\"&mode=$mode&nogroups=$nogroups\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,width=500,height=500\"); chooser.ifield = ifield; window.ifield = ifield; chooser.rfield = rfield; window.rfield = rfield' value=\"...\">\n";
	}
else {
	return "<input type=button onClick='ifield = document.forms[$form].$_[0]; chooser = window.open(\"../$module_name/address_chooser.cgi?addr=\"+escape(ifield.value)+\"&mode=$mode\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,width=500,height=500\"); chooser.ifield = ifield; window.ifield = ifield' value=\"...\">\n";
	}
}

# list_folders()
# Returns a list of all folders for this user
# folder types: 0 = mbox, 1 = maildir, 2 = pop3, 3 = mh, 4 = imap, 5 = combined,
#		6 = virtual
# folder modes: 0 = ~/mail, 1 = external folder, 2 = sent mail,
#               3 = inbox/drafts/trash
sub list_folders
{
if (defined(@list_folders_cache)) {
	return @list_folders_cache;
	}
local (@rv, $f, $o, %done);

# Read the module's config directory, to find folders files
opendir(DIR, $user_module_config_directory);
local @folderfiles = readdir(DIR);
closedir(DIR);

if ($config{'mail_system'} == 2) {
	# POP3 inbox
	push(@rv, { 'name' => $text{'folder_inbox'},
		    'type' => 2,
		    'server' => $config{'pop3_server'} || "localhost",
		    'mode' => 3,
		    'remote' => 1,
		    'nowrite' => 1,
		    'inbox' => 1,
		    'index' => 0 });
	&read_file("$user_module_config_directory/inbox.pop3", $rv[$#rv]);
	}
elsif ($config{'mail_system'} == 4) {
	# IMAP inbox
	local $imapserver = $config{'pop3_server'} || "localhost";
	push(@rv, { 'name' => $text{'folder_inbox'},
		    'id' => 'INBOX',
		    'type' => 4,
		    'server' => $imapserver,
		    'mode' => 3,
		    'remote' => 1,
		    'flags' => 1,
		    'inbox' => 1,
		    'index' => 0 });
	&read_file("$user_module_config_directory/inbox.imap", $rv[$#rv]);

	# Use HTTP username and password, if available and if logging in to
	# a local IMAP server.
	if ($remote_user && $main::remote_pass &&
	    (&to_ipaddress($rv[0]->{'server'}) eq '127.0.0.1' ||
	     &to_ipaddress($rv[0]->{'server'}) eq
	      &to_ipaddress(&get_system_hostname()))) {
		$rv[0]->{'user'} = $remote_user;
		$rv[0]->{'pass'} = $main::remote_pass;
		$rv[0]->{'autouser'} = 1;
		}

	# Get other IMAP folders (if we can)
	local ($ok, $ih) = &imap_login($rv[0]);
	if ($ok == 1) {
		local @irv = &imap_command($ih, "list \"\" \"*\"");
		if ($irv[0]) {
			foreach my $l (@{$irv[1]}) {
				if ($l =~ /LIST\s+\(.*\)\s+("(.*)"|\S+)\s+("(.*)"|\S+)/) {
					# Found a folder line
					local $fn = $4 || $3;
					next if ($fn eq "INBOX");
					push(@rv,
					  { 'name' => $fn,
					    'id' => $fn,
					    'type' => 4,
					    'server' => $imapserver,
					    'user' => $rv[0]->{'user'},
					    'pass' => $rv[0]->{'pass'},
					    'mode' => 0,
					    'remote' => 1,
		    			    'flags' => 1,
					    'imapauto' => 1,
					    'mailbox' => $fn,
					    'index' => scalar(@rv) });
					&read_file("$user_module_config_directory/$fn.imap", $rv[$#rv]);
					}
				}
			}
		}

	# Find or create the IMAP sent mail folder
	local $sf = $userconfig{'sent_name'} || 'sent';
	local ($sent) = grep { lc($_->{'name'}) eq lc($sf) } @rv;
	if (!$sent) {
		local @irv = &imap_command($ih, "create \"$sf\"");
		if ($irv[0]) {
			$sent = { 'id' => $sf,
			          'type' => 4,
				  'server' => $imapserver,
				  'user' => $rv[0]->{'user'},
				  'pass' => $rv[0]->{'pass'},
				  'mode' => 2,
				  'remote' => 1,
				  'flags' => 1,
				  'imapauto' => 1,
				  'mailbox' => $sf,
			          'index' => scalar(@rv) };
			push(@rv, $sent);
			&read_file("$user_module_config_directory/$sf.imap",
				   $sent);
			}
		}
	if ($sent) {
		$sent->{'name'} = $text{'folder_sent'};
		$sent->{'perpage'} = $userconfig{'perpage_sent_mail'};
		$sent->{'fromaddr'} = $userconfig{'fromaddr_sent_mail'};
		$sent->{'sent'} = 1;
		$sent->{'mode'} = 2;
		}

	# Find or create the IMAP drafts folder
	local $df = $userconfig{'drafts_name'} || 'drafts';
	local ($drafts) = grep { lc($_->{'name'}) eq lc($df) } @rv;
	if (!$drafts) {
		local @irv = &imap_command($ih, "create \"$df\"");
		if ($irv[0]) {
			$drafts = { 'id' => $df,
			            'type' => 4,
				    'server' => $imapserver,
				    'user' => $rv[0]->{'user'},
				    'pass' => $rv[0]->{'pass'},
				    'mode' => 3,
				    'remote' => 1,
				    'flags' => 1,
				    'imapauto' => 1,
				    'mailbox' => $df,
			            'index' => scalar(@rv) };
			push(@rv, $drafts);
			&read_file("$user_module_config_directory/$df.imap",
				   $drafts);
			}
		}
	if ($drafts) {
		$drafts->{'name'} = $text{'folder_drafts'};
		$drafts->{'drafts'} = 1;
		$drafts->{'mode'} = 3;
		}

	# Find or create the IMAP trash folder
	if ($userconfig{'delete_mode'} == 1) {
		local $tf = $userconfig{'trash_name'} || 'trash';
		local ($trash) = grep { lc($_->{'name'}) eq lc($tf) } @rv;
		if (!$trash) {
			local @irv = &imap_command($ih, "create \"$tf\"");
			if ($irv[0]) {
				$trash = { 'id' => $tf,
					   'type' => 4,
					   'server' => $imapserver,
					   'user' => $rv[0]->{'user'},
					   'pass' => $rv[0]->{'pass'},
					   'mode' => 3,
					   'remote' => 1,
					   'flags' => 1,
					   'imapauto' => 1,
					   'mailbox' => $tf,
					   'index' => scalar(@rv) };
				push(@rv, $trash);
				&read_file(
				    "$user_module_config_directory/$tf.imap",
				    $trash);
				}
			}
		if ($trash) {
			$trash->{'name'} = $text{'folder_trash'};
			$trash->{'trash'} = 1;
			$trash->{'mode'} = 3;
			}
		}

	# For each IMAP folder, guess the underlying file
	foreach my $f (@rv) {
		if ($f->{'inbox'}) {
			# Use the configured inbox location
			local $path = $config{'mail_system'} == 0 ?
                                &user_mail_file(@remote_user_info) :
                                $qmail_maildir;
			$f->{'file'} = $path if (-e $path);
			}
		else {
			# Look in configured folders directory
			local $path = "$folders_dir/$f->{'id'}";
			if (-e $path) {
				$f->{'file'} = $path;
				}
			else {
				# Try . at start of folder names
				local $n = $f->{'id'};
				$n =~ s/^\.//;
				if ($n =~ /\//) {
					# Turn foo/bar to foo/.bar
					$n =~ s/\//\/\./;
					}
				else {
					# Turn foo to .foo
					$n = ".".$n;
					}
				$path = "$folders_dir/$n";
				$f->{'file'} = $path if (-e $path);
				}
			}
		}

	goto IMAPONLY;
	}
else {
	# Local mail file inbox
	push(@rv, { 'name' => $text{'folder_inbox'},
		    'type' => $config{'mail_system'},
		    'mode' => 3,
		    'inbox' => 1,
		    'file' => $config{'mail_system'} == 0 ?
				&user_mail_file(@remote_user_info) :
				$qmail_maildir,
		    'index' => 0 });
	$done{$rv[$#rv]->{'file'}}++;
	}
local $inbox = $rv[$#rv];

# Add sent mail file
local $sf;
if ($folder_types{'ext'} && $userconfig{'sent_mail'}) {
	$sf = $userconfig{'sent_mail'};
	$done{$userconfig{'sent_mail'}}++;
	}
else {
	local $sfn = $userconfig{'sent_name'} || 'sentmail';
	$sf = "$folders_dir/$sfn";
	if (!-e $sf && $userconfig{'mailbox_dir'} eq "Maildir") {
		# For Maildir++ , use .sentmail
		$sf = "$folders_dir/.$sfn";
		}
	}
$done{$sf}++;
local $sft = -e $sf ? &folder_type($sf) :
	     $userconfig{'mailbox_dir'} eq "Maildir" ? 1 : 0;
push(@rv, { 'name' => $text{'folder_sent'},
	    'type' => $sft,
	    'file' => $sf,
	    'perpage' => $userconfig{'perpage_sent_mail'},
	    'fromaddr' => $userconfig{'fromaddr_sent_mail'},
	    'hide' => $userconfig{'hide_sent_mail'},
	    'mode' => 2,
	    'sent' => 1,
	    'index' => scalar(@rv) });

# Add drafts file
local $dn = $userconfig{'drafts_name'};
if ($dn && $userconfig{'mailbox_dir'} eq "Maildir" && $dn !~ /^\./) {
	# Maildir++ folders always start with .
	$dn = ".".$dn;
	}
local $df = $dn ? "$folders_dir/$dn" :
	    -r "$folders_dir/Drafts" ? "$folders_dir/Drafts" :
	    -r "$folders_dir/.Drafts" ? "$folders_dir/.Drafts" :
	    -r "$folders_dir/.drafts" ? "$folders_dir/.drafts" :
	    $userconfig{'mailbox_dir'} eq "Maildir" ? "$folders_dir/.drafts" :
				        	      "$folders_dir/drafts";
$done{$df}++;
local $dft = -e $df ? &folder_type($df) :
	     $userconfig{'mailbox_dir'} eq "Maildir" ? 1 : 0;
push(@rv, { 'name' => $text{'folder_drafts'},
	    'type' => $dft,
	    'file' => $df,
	    'mode' => 3,
	    'drafts' => 1,
	    'index' => scalar(@rv) });

# If using a trash folder, add it
if ($userconfig{'delete_mode'} == 1) {
	local $tn = $userconfig{'trash_name'};
	if ($tn && $userconfig{'mailbox_dir'} eq "Maildir" && $tn !~ /^\./) {
		# Maildir++ folders always start with .
		$tn = ".".$tn;
		}
	local $tf = $tn ? "$folders_dir/$tn" :
		    -r "$folders_dir/Trash" ? "$folders_dir/Trash" :
		    -r "$folders_dir/.Trash" ? "$folders_dir/.Trash" :
		    -r "$folders_dir/.trash" ? "$folders_dir/.trash" :
		    $userconfig{'mailbox_dir'} eq "Maildir" ?
			"$folders_dir/.trash" : "$folders_dir/trash";
	$done{$tf}++;
	local $tft = -e $tf ? &folder_type($tf) :
		     $userconfig{'mailbox_dir'} eq "Maildir" ? 1 : 0;
	push(@rv, { 'name' => $text{'folder_trash'},
		    'type' => $tft,
		    'file' => $tf,
		    'mode' => 3,
		    'trash' => 1,
		    'index' => scalar(@rv) });
	}

# Add local folders, usually under ~/mail
if ($folder_types{'local'}) {
	foreach $p (&recursive_files($folders_dir,
				     $userconfig{'mailbox_recur'})) {
		local $f = $p;
		$f =~ s/^\Q$folders_dir\E\///;
		local $name = $f;
		if ($folders_dir eq "$remote_user_info[7]/Maildir") {
			# A sub-folder under Maildir .. remove the . at the
			# start of the sub-folder name
			$name =~ s/^\.// || $name =~ s/\/\./\// || next;

			# When in Maildir++ mode, any non-subdirectory
			# is ignored
			next if (!-d $p);
			}
		push(@rv, { 'name' => $name,
			    'file' => $p,
			    'type' => &folder_type($p),
			    'perpage' => $userconfig{"perpage_$f"},
			    'fromaddr' => $userconfig{"fromaddr_$f"},
			    'sent' => $userconfig{"sent_$f"},
			    'hide' => $userconfig{"hide_$f"},
			    'mode' => 0,
			    'index' => scalar(@rv) } ) if (!$done{$p});
		$done{$p}++;
		}
	}

# Add sub-folders in ~/Maildir/ , as used by Courier
if ($inbox->{'type'} == 1 && $userconfig{'mailbox_dir'} ne "Maildir") {
	foreach $p (&recursive_files($inbox->{'file'}, 0)) {
		local $f = $p;
		$f =~ s/^\Q$inbox->{'file'}\E\///;
		local $name = $f;
		$name =~ s/^\.// || $name =~ s/\/\./\//;
		push(@rv, { 'name' => "$name (Courier)",
			    'file' => $p,
			    'type' => &folder_type($p),
			    'perpage' => $userconfig{"perpage_$f"},
			    'fromaddr' => $userconfig{"fromaddr_$f"},
			    'sent' => $userconfig{"sent_$f"},
			    'hide' => $userconfig{"hide_$f"},
			    'mode' => 0,
			    'index' => scalar(@rv) } ) if (!$done{$p});
		$done{$p}++;
		}
	}

# Add user-defined external mail file folders
if ($folder_types{'ext'}) {
	foreach $o (split(/\t+/, $userconfig{'mailboxes'})) {
		$o =~ /\/([^\/]+)$/ || next;
		push(@rv, { 'name' => $userconfig{"folder_$o"} || $1,
			    'file' => $o,
			    'perpage' => $userconfig{"perpage_$o"},
			    'fromaddr' => $userconfig{"fromaddr_$o"},
			    'sent' => $userconfig{"sent_$o"},
			    'hide' => $userconfig{"hide_$o"},
			    'type' => &folder_type($o),
			    'mode' => 1,
			    'index' => scalar(@rv) } ) if (!$done{$o});
		$done{$o}++;
		}
	}

# Add user-defined POP3	and IMAP folders
foreach $f (@folderfiles) {
	if ($f =~ /^(\d+)\.pop3$/ && $folder_types{'pop3'}) {
		local %pop3 = ( 'id' => $1 );
		&read_file("$user_module_config_directory/$f", \%pop3);
		$pop3{'type'} = 2;
		$pop3{'mode'} = 0;
		$pop3{'remote'} = 1;
		$pop3{'nowrite'} = 1;
		$pop3{'index'} = scalar(@rv);
		push(@rv, \%pop3);
		}
	elsif ($f =~ /^(\d+)\.imap$/ && $folder_types{'imap'}) {
		local %imap = ( 'id' => $1 );
		&read_file("$user_module_config_directory/$f", \%imap);
		$imap{'type'} = 4;
		$imap{'mode'} = 0;
		$imap{'remote'} = 1;
		$imap{'flags'} = 1;
		$imap{'index'} = scalar(@rv);
		push(@rv, \%imap);
		}
	}

# When in IMAP inbox mode, we goto this label to skip all local folders
IMAPONLY:

# Add user-defined composite folders
local %fcache;
foreach $f (@folderfiles) {
	if ($f =~ /^(\d+)\.comp$/) {
		local %comp = ( 'id' => $1 );
		&read_file("$user_module_config_directory/$f", \%comp);
		$comp{'folderfile'} = "$user_module_config_directory/$f";
		$comp{'type'} = 5;
		$comp{'mode'} = 0;
		$comp{'index'} = scalar(@rv);
		local $sfn;
		foreach $sfn (split(/\t+/, $comp{'subfoldernames'})) {
			local $sf = &find_named_folder($sfn, \@rv, \%fcache);
			push(@{$comp{'subfolders'}}, $sf) if ($sf);
			}
		push(@rv, \%comp);
		}
	}

# Add spam folder as specified in spamassassin module, in case it is
# outside of the folders we scan
if (&foreign_check("spam")) {
	local %suserconfig = &foreign_config("spam", 1);
	local $file = $suserconfig{'spam_file'};
	$file =~ s/\.$//;
	$file =~ s/\/$//;
	$file = "$remote_user_info[7]/$file" if ($file && $file !~ /^\//);
	$file =~ s/\~/$remote_user_info[7]/;
	if ($file) {
		if ($config{'mail_system'} == 4) {
			# In IMAP mode, the first folder named spam is marked
			local ($sf) = grep { lc($_->{'name'}) eq 'spam' } @rv;
			if ($sf) {
				$sf->{'spam'} = 1;
				}
			}
		elsif (!$done{$file}) {
			# Need to add
			push(@rv, { 'name' => "Spam",
				    'file' => $file,
				    'type' => &folder_type($file),
				    'perpage' => $userconfig{"perpage_$file"},
				    'fromaddr' => $userconfig{"fromaddr_$file"},
				    'sent' => $userconfig{"sent_$file"},
				    'hide' => 0,
				    'mode' => 0,
				    'spam' => 1,
				    'index' => scalar(@rv) } );
			$done{$file}++;
			}
		else {
			# Mark as spam folder
			local ($sf) = grep { $_->{'file'} eq $file } @rv;
			if ($sf) {
				$sf->{'spam'} = 1;
				}
			}
		}
	}

# Add virtual folders. This has to be last, so that other folders can be found
# based on virtual/composite indexes.
foreach $f (@folderfiles) {
	if ($f =~ /^(\d+)\.virt$/) {
		local %virt = ( 'id' => $1 );
		&read_file("$user_module_config_directory/$f", \%virt);
		$virt{'folderfile'} = "$user_module_config_directory/$f";
		$virt{'type'} = 6;
		$virt{'mode'} = 0;
		$virt{'index'} = scalar(@rv);
		$virt{'noadd'} = 1;
		$virt{'members'} = [ ];
		push(@rv, \%virt);
		}
	}

# Expand virtual folder sub-folders
foreach my $virt (grep { $_->{'type'} == 6 } @rv) {
	foreach my $k (keys %$virt) {
		next if ($k !~ /^\d+$/);
		next if ($virt->{$k} !~ /\t/);  # Old format
		local ($sfn, $id) = split(/\t+/, $virt->{$k}, 2);
		local $sf = &find_named_folder($sfn, \@rv, \%fcache);
		$virt->{'members'}->[$k] = [ $sf, $id ] if ($sf);
		delete($virt->{$k});
		}
	}

# Mark folders are using Notes mail encoding
foreach $f (@rv) {
	if ($f->{'file'} && $userconfig{"notes_".$f->{'file'}}) {
		$f->{'notes_decode'} = 1;
		}
	}

# Work out last-modified time of all folders, and set sortable flag
&set_folder_lastmodified(\@rv);

# Set searchable flag
foreach my $f (@rv) {
	$f->{'searchable'} = 1 if ($f->{'type'} != 6 ||
				   $f->{'id'} != $search_folder_id);
	}

# Set show to/from flags
foreach my $f (@rv) {
	if (!defined($f->{'show_to'})) {
		$f->{'show_to'} = $f->{'sent'} || $f->{'drafts'} ||
				  $userconfig{'show_to'};
		}
	if (!defined($f->{'show_from'})) {
		$f->{'show_from'} = !($f->{'sent'} || $f->{'drafts'}) ||
				    $userconfig{'show_to'};
		}
	}

# For Maildir folders, check if we can get the read flag from the folder files
foreach my $f (@rv) {
	if ($f->{'type'} == 1) {
		$f->{'flags'} = 2;
		}
	}

@list_folders_cache = @rv;
return @rv;
}

# get_spam_inbox_folder()
# Returns the folder to which spam should be moved
sub get_spam_inbox_folder
{
local ($inbox) = grep { $_->{'inbox'} } &list_folders();
return $inbox;
}

# save_folder(&folder, [&old])
# Creates or updates a folder
sub save_folder
{
local ($folder, $old) = @_;
mkdir($folders_dir, 0700) if (!-d $folders_dir);
if ($folder->{'type'} == 2) {
	# A POP3 folder
	$folder->{'id'} ||= time();
	local %pop3;
	foreach $k (keys %$folder) {
		if ($k ne "type" && $k ne "mode" && $k ne "remote" &&
		    $k ne "nowrite" && $k ne "index") {
			$pop3{$k} = $folder->{$k};
			}
		}
	&write_file("$user_module_config_directory/$folder->{'id'}.pop3",
		    \%pop3);
	chmod(0700, "$user_module_config_directory/$folder->{'id'}.pop3");
	}
elsif ($folder->{'type'} == 4) {
	# An IMAP folder
	local @exclude;
	if ($folder->{'imapauto'}) {
		# This type of folder needs to be really created or updated
		# on the server
		if (!$folder->{'id'}) {
			# Need to create
			local ($ok, $ih) = &imap_login($folder);
			local @irv = &imap_command($ih,
					"create \"$folder->{'name'}\"");
			$irv[0] || &error($irv[2]);
			$folder->{'id'} = $folder->{'mailbox'} =
				$folder->{'name'};
			}
		elsif ($folder->{'mailbox'} ne $folder->{'name'}) {
			# Need to rename
			local ($ok, $ih) = &imap_login($folder);
			local @irv = &imap_command($ih,
				"rename \"$folder->{'mailbox'}\" \"$folder->{'name'}\"");
			$irv[0] || &error($irv[2]);
			$folder->{'id'} = $folder->{'name'};
			$folder->{'id'} = $folder->{'mailbox'} =
				$folder->{'name'};
			}
		@exclude = ( "type", "mode", "remote", "nowrite", "index",
			     "id", "mailbox", "server", "user", "pass" );
		}
	else {
		# Just save details of IMAP folder in a file
		$folder->{'id'} ||= time();
		@exclude = ( "type", "mode", "remote", "nowrite", "index" );
		}
	local %imap;
	foreach my $k (keys %$folder) {
		if (&indexof($k, @exclude) == -1) {
			$imap{$k} = $folder->{$k};
			}
		}
	&write_file("$user_module_config_directory/$folder->{'id'}.imap",
		    \%imap);
	chmod(0700, "$user_module_config_directory/$folder->{'id'}.imap");
	}
elsif ($folder->{'type'} == 5) {
	# A composite
	$folder->{'id'} ||= time();
	local %comp;
	foreach $k (keys %$folder) {
		if ($k ne "type" && $k ne "mode" && $k ne "index" &&
		    $k ne "subfolders") {
			$comp{$k} = $folder->{$k};
			}
		}
	local ($sf, @sfns);
	foreach $sf (@{$folder->{'subfolders'}}) {
		local $sfn = &folder_name($sf);
		push(@sfns, $sfn);
		}
	$comp{'subfoldernames'} = join("\t", @sfns);
	&write_file("$user_module_config_directory/$folder->{'id'}.comp",
		    \%comp);
	chmod(0700, "$user_module_config_directory/$folder->{'id'}.comp");
	}
elsif ($folder->{'type'} == 6) {
	# A virtual folder
	$folder->{'id'} ||= time();
	local %virt;
	foreach $k (keys %$folder) {
		if ($k ne "type" && $k ne "mode" && $k ne "index" &&
		    $k ne "members") {
			$virt{$k} = $folder->{$k};
			}
		}
	local $i;
	local $mems = $folder->{'members'};
	for($i=0; $i<@$mems; $i++) {
		$virt{$i} = &folder_name($mems->[$i]->[0])."\t".
			    $mems->[$i]->[1];
		}
	&write_file("$user_module_config_directory/$folder->{'id'}.virt",
		    \%virt);
	chmod(0700, "$user_module_config_directory/$folder->{'id'}.virt");
	}
elsif ($folder->{'mode'} == 0) {
	# Updating a folder in ~/mail .. need to manage file, and config options
	local $path = "$folders_dir/$folder->{'name'}";
	if ($folders_dir eq "$remote_user_info[7]/Maildir") {
		# Maildir sub-folder .. put a . in the name
		$path =~ s/([^\/]+)$/.$1/;
		}
	if ($folder->{'name'} =~ /\//) {
		local $pp = $path;
		$pp =~ s/\/[^\/]+$//;
		system("mkdir -p ".quotemeta($pp));
		}
	if (!$old) {
		# Create the mailbox/maildir/MH dir
		if ($folder->{'type'} == 0) {
			open(FOLDER, ">>$path");
			close(FOLDER);
			chmod(0700, $path);
			}
		elsif ($folder->{'type'} == 1) {
			mkdir($path, 0700);
			mkdir("$path/cur", 0700);
			mkdir("$path/new", 0700);
			mkdir("$path/tmp", 0700);
			}
		elsif ($folder->{'type'} == 3) {
			mkdir($path, 0700);
			}
		}
	elsif ($old->{'name'} ne $folder->{'name'}) {
		# Just rename
		rename($old->{'file'}, $path);
		}
	if ($old) {
		delete($userconfig{'perpage_'.$old->{'name'}});
		delete($userconfig{'sent_'.$old->{'name'}});
		delete($userconfig{'hide_'.$old->{'name'}});
		delete($userconfig{'fromaddr_'.$old->{'name'}});
		}
	$userconfig{'perpage_'.$folder->{'name'}} = $folder->{'perpage'}
		if ($folder->{'perpage'});
	$userconfig{'sent_'.$folder->{'name'}} = $folder->{'sent'}
		if ($folder->{'sent'});
	$userconfig{'hide_'.$folder->{'name'}} = $folder->{'hide'}
		if ($folder->{'hide'});
	$userconfig{'fromaddr_'.$folder->{'name'}} = $folder->{'fromaddr'}
		if ($folder->{'fromaddr'});
	&save_user_module_config();
	$folder->{'file'} = $path;
	}
elsif ($folder->{'mode'} == 1) {
	# Updating or adding an external file folder
	local @mailboxes = split(/\t+/, $userconfig{'mailboxes'});
	if (!$old) {
		push(@mailboxes, $folder->{'file'});
		}
	else {
		delete($userconfig{'folder_'.$folder->{'file'}});
		delete($userconfig{'perpage_'.$folder->{'file'}});
		delete($userconfig{'sent_'.$folder->{'file'}});
		delete($userconfig{'hide_'.$folder->{'file'}});
		delete($userconfig{'fromaddr_'.$folder->{'file'}});
		local $idx = &indexof($folder->{'file'}, @mailboxes);
		$mailboxes[$idx] = $folder->{'file'};
		}
	$userconfig{'folder_'.$folder->{'file'}} = $folder->{'name'};
	$userconfig{'perpage_'.$folder->{'file'}} = $folder->{'perpage'}
		if ($folder->{'perpage'});
	$userconfig{'sent_'.$folder->{'file'}} = $folder->{'sent'};
	$userconfig{'hide_'.$folder->{'file'}} = $folder->{'hide'}
		if ($folder->{'hide'});
	$userconfig{'fromaddr_'.$folder->{'file'}} = $folder->{'fromaddr'}
		if ($folder->{'fromaddr'});
	$userconfig{'mailboxes'} = join("\t", @mailboxes);
	&save_user_module_config();
	}
elsif ($folder->{'mode'} == 2) {
	# The sent mail folder
	delete($userconfig{'perpage_sent_mail'});
	delete($userconfig{'hide_sent_mail'});
	delete($userconfig{'fromaddr_sent_mail'});
	local $sf = "$folders_dir/sentmail";
	if ($folder->{'file'} eq $sf) {
		delete($userconfig{'sent_mail'});
		}
	else {
		$userconfig{'sent_mail'} = $folder->{'file'};
		}
	$userconfig{'perpage_sent_mail'} = $folder->{'perpage'}
		if ($folder->{'perpage'});
	$userconfig{'hide_sent_mail'} = $folder->{'hide'}
		if ($folder->{'hide'});
	$userconfig{'fromaddr_sent_mail'} = $folder->{'fromaddr'}
		if ($folder->{'fromaddr'});
	&save_user_module_config();
	}
# Add to or update cache
if (defined(@list_folders_cache)) {
	if ($old) {
		local $idx = &indexof($old, @list_folders_cache);
		if ($idx >= 0) {
			$list_folders_cache[$idx] = $folder;
			}
		}
	else {
		push(@list_folders_cache, $folder);
		}
	}
}

# delete_folder(&folder)
# Removes some folder
sub delete_folder
{
local ($folder) = @_;
if ($folder->{'type'} == 2) {
	# A POP3 folder
	unlink("$user_module_config_directory/$folder->{'id'}.pop3");
	system("rm -rf $user_module_config_directory/$folder->{'id'}.cache");
	}
elsif ($folder->{'type'} == 4) {
	# An IMAP folder
	unlink("$user_module_config_directory/$folder->{'id'}.imap");
	system("rm -rf $user_module_config_directory/$folder->{'id'}.cache");

	if ($folder->{'imapauto'}) {
		# Remove actual folder from IMAP server too
		local ($ok, $ih) = &imap_login($folder);
		local @irv = &imap_command($ih, "delete \"$folder->{'name'}\"");
		$irv[0] || &error($irv[2]);
		}
	}
elsif ($folder->{'type'} == 5) {
	# A composite folder
	unlink("$user_module_config_directory/$folder->{'id'}.comp");
	}
elsif ($folder->{'type'} == 6) {
	# A virtual folder
	unlink("$user_module_config_directory/$folder->{'id'}.virt");
	}
elsif ($folder->{'mode'} == 0) {
	# Deleting a folder within ~/mail
	if ($folder->{'type'} == 0) {
		unlink($folder->{'file'});
		}
	else {
		system("rm -rf ".quotemeta($folder->{'file'}));
		}
	delete($userconfig{'perpage_'.$folder->{'name'}});
	delete($userconfig{'sent_'.$folder->{'name'}});
	delete($userconfig{'hide_'.$folder->{'name'}});
	delete($userconfig{'fromaddr_'.$folder->{'name'}});
	&save_user_module_config();
	}
elsif ($folder->{'mode'} == 1) {
	# Remove from list of external folders
	local @mailboxes = split(/\t+/, $userconfig{'mailboxes'});
	@mailboxes = grep { $_ ne $folder->{'file'} } @mailboxes;
	delete($userconfig{'folder_'.$folder->{'file'}});
	delete($userconfig{'perpage_'.$folder->{'file'}});
	delete($userconfig{'sent_'.$folder->{'file'}});
	delete($userconfig{'hide_'.$folder->{'file'}});
	delete($userconfig{'fromaddr_'.$folder->{'file'}});
	$userconfig{'mailboxes'} = join("\t", @mailboxes);
	&save_user_module_config();
	}
# Remove from cache
if (defined(@list_folders_cache)) {
	@list_folders_cache = grep { $_ ne $folder } @list_folders_cache;
	}
}

# notes_decode(&mail, &folder)
# Given a message forwarded by lotus notes, extra the real from and subject
# lines from the body
sub notes_decode
{
return if (!$_[1]->{'notes_decode'});
local ($from, $subject, $h);
if ($_[0]->{'body'} =~ /(^|Content-type:.*)\n\s*\nFrom: +(.*)/) {
	$from = $2;
	}
elsif ($_[0]->{'body'} =~ /(^|Content-type:.*)\n\s*\n(\([^\)]+\)\s*)?(\S.*)/) {
	$from = $3;
	}
$from =~ s/\s+on.*//;
$from =~ s/\d+\/\d+\/\d+\s+\d+:\d+\s*//;
$from = undef if ($from =~ /:/);
if ($_[0]->{'body'} =~ /\nSubject: +(.*)/) {
	$subject = $1;
	}
local ($ofrom) = &address_parts($_[0]->{'header'}->{'from'});
if ($from && $from !~ /\@\S+\.\S+/) {
	$from = "\"$from\" <$ofrom>";
	}
foreach $h ([ 'From', $from ],
	    [ 'Subject', $subject ]) {
	next if (!$h->[1]);
	local ($eh) = grep { lc($_->[0]) eq lc($h->[0]) } @{$_[0]->{'headers'}};
	if ($eh) {
		$eh->[1] = $h->[1];
		}
	else {
		push(@{$_[0]->{'headers'}}, $h);
		}
	$_[0]->{'header'}->{lc($h->[0])} = $h->[1];
	}
}

# need_delete_warn(&folder)
sub need_delete_warn
{
return 0 if ($_[0]->{'type'} == 6 && !$_[0]->{'delete'});
return 1 if ($userconfig{'delete_warn'} eq 'y');
return 0 if ($userconfig{'delete_warn'} eq 'n');
local $mf;
return $_[0]->{'type'} == 0 &&
       ($mf = &folder_file($_[0])) &&
       &disk_usage_kb($mf)*1024 > $userconfig{'delete_warn'};
}

# get_signature()
# Returns the users signature, if any
sub get_signature
{
local $sf = &get_signature_file();
$sf || return undef;
local $sig;
open(SIG, $sf) || return undef;
while(<SIG>) {
	$sig .= $_;
	}
close(SIG);
return $sig;
}

# get_signature_file()
# Returns the full path to the file that should contain the user's signature,
# or undef if none is defined
sub get_signature_file
{
return undef if ($userconfig{'sig_file'} eq '*');
local $sf = $userconfig{'sig_file'};
$sf = "$remote_user_info[7]/$sf" if ($sf !~ /^\//);
return &group_subs($sf);
}

# movecopy_select(number, &folders, &folder-to-exclude, copy-only)
# Returns HTML for selecting a folder to move or copy to
sub movecopy_select
{
local $rv;
if (!$_[3]) {
	$rv .= &ui_submit($text{'mail_move'}, "move".$_[0]);
	}
print &ui_submit($text{'mail_copy'}, "copy".$_[0]);
local @mfolders = grep { $_ ne $_[2] && !$_->{'nowrite'} } @{$_[1]};
$rv .= &folder_select(\@mfolders, undef, "mfolder$_[0]");
return $rv;
}

# show_folder_options(&folder, mode)
# Print HTML for editing the options for some folder
sub show_folder_options
{
local ($folder, $mode) = @_;

# Messages per page
print &ui_table_row($text{'edit_perpage'},
	&ui_opt_textbox("perpage", $folder->{'perpage'}, 5, $text{'default'}));

# Show as sent mail
if ($mode != 2) {
	print &ui_table_row($text{'edit_sentview'},
		&ui_yesno_radio("show_to", $folder->{'show_to'}));
	}

# From address for sent mail
print &ui_table_row($text{'edit_fromaddr'},
	&ui_opt_textbox("fromaddr", $folder->{'fromaddr'}, 30,
			$text{'default'})." ".
	&address_button("fromaddr", 0, 1));

# Hide from folder list?
print &ui_table_row($text{'edit_hide'},
	&ui_yesno_radio("hide", $folder->{'hide'}));
}

# parse_folder_options(&folder, mode, &in)
sub parse_folder_options
{
local ($folder, $mode, $in) = @_;
if (!$in->{'perpage_def'}) {
	$in->{'perpage'} =~ /^\d+$/ || &error($text{'save_eperpage'});
	$folder->{'perpage'} = $in->{'perpage'};
	}
else {
	delete($folder->{'perpage'});
	}
if ($mode != 2) {
	$folder->{'show_to'} = $in->{'show_to'};
	$folder->{'show_from'} = !$in->{'show_to'};
	}
if (!$in->{'fromaddr_def'}) {
	$in->{'fromaddr'} =~ /\S/ || &error($text{'save_efromaddr'});
	$folder->{'fromaddr'} = $in->{'fromaddr'};
	}
$folder->{'hide'} = $in->{'hide'};
}

# list_address_groups()
# Returns a list of address book entries, each an array reference containing
# the group name, members and index
sub list_address_groups
{
local @rv;
local $i = 0;
open(ADDRESS, $address_group_book);
while(<ADDRESS>) {
	s/\r|\n//g;
	local @sp = split(/\t+/, $_);
	if (@sp == 2) {
		push(@rv, [ $sp[0], $sp[1], $i ]);
		}
	$i++;
	}
close(ADDRESS);
if ($config{'global_address_group'}) {
	local $gab = &group_subs($config{'global_address_group'});
	open(ADDRESS, $gab);
	while(<ADDRESS>) {
		s/\r|\n//g;
		local @sp = split(/\t+/, $_);
		if (@sp == 2) {
			push(@rv, [ $sp[0], $sp[1] ]);
			}
		}
	close(ADDRESS);
	}
if ($userconfig{'sort_addrs'} == 1) {
	return sort { lc($a->[0]) cmp lc($b->[0]) } @rv;
	}
elsif ($userconfig{'sort_addrs'} == 2) {
	return sort { lc($a->[1]) cmp lc($b->[1]) } @rv;
	}
else {
	return @rv;
	}
}

# create_address_group(name, members)
# Adds an entry to the address group book
sub create_address_group
{
&open_tempfile(ADDRESS, ">>$address_group_book");
&print_tempfile(ADDRESS, "$_[0]\t$_[1]\n");
&close_tempfile(ADDRESS);
}

# modify_address_group(index, name, members)
# Updates some entry in the address group book
sub modify_address_group
{
&replace_file_line($address_group_book, $_[0], "$_[1]\t$_[2]\n");
}

# delete_address_group(index)
# Deletes some entry from the address group book
sub delete_address_group
{
&replace_file_line($address_group_book, $_[0]);
}

# list_folders_sorted()
# Like list_folders(), but applies the chosen sort
sub list_folders_sorted
{
local @folders = &list_folders();
local @rv;
if ($userconfig{'folder_sort'} == 0) {
	# Builtin, then ~/mail, then external
	local @builtin = grep { $_->{'mode'} >= 2 } @folders;
	local @local = grep { $_->{'mode'} == 0 } @folders;
	local @external = grep { $_->{'mode'} == 1 } @folders;
	@rv = (@builtin,
		(sort { lc($a->{'name'}) cmp lc($b->{'name'}) } @local),
		(sort { lc($a->{'name'}) cmp lc($b->{'name'}) } @external));
	}
elsif ($userconfig{'folder_sort'} == 1) {
	# Builtin, then rest sorted by name
	local @builtin = grep { $_->{'mode'} >= 2 } @folders;
	local @extra = grep { $_->{'mode'} < 2 } @folders;
	@rv = (@builtin,
		sort { lc($a->{'name'}) cmp lc($b->{'name'}) } @extra);
	}
elsif ($userconfig{'folder_sort'} == 2) {
	# All by name
	@rv = sort { lc($a->{'name'}) cmp lc($b->{'name'}) } @folders;
	}
if ($userconfig{'default_folder'} && $userconfig{'folder_sort'} <= 1) {
	# Move default folder to top of the list
	local $df = &find_named_folder($userconfig{'default_folder'}, \@rv);
	if ($df) {
		@rv = ( $df, grep { $_ ne $df } @rv );
		}
	}
return @rv;
}

# group_subs(filename)
# Replaces $group in a filename with the first valid primary or secondary
# that matches a file
sub group_subs
{
local @ginfo = getgrgid($remote_user_info[3]);
local $rv = $_[0];
$rv =~ s/\$group/$ginfo[0]/g;
if ($rv =~ /\$sgroup/) {
	# Try all secondary groups, and stop at the first one
	setgrent();
	while(@ginfo = getgrent()) {
		local @m = split(/\s+/, $ginfo[3]);
		if (&indexof($remote_user, @m) >= 0) {
			local $rv2 = $rv;
			$rv2 =~ s/\$sgroup/$ginfo[0]/g;
			if (-r $rv2) {
				$rv = $rv2;
				last;
				}
			}
		}
	endgrent() if ($gconfig{'os_type'} ne 'hpux');
	}
return $rv;
}

# set_module_index(folder-num)
sub set_module_index
{
$module_index_link = "/$module_name/index.cgi?folder=$_[0]&start=$in{'start'}";
$module_index_name = $text{'mail_indexlink'};
}

# check_modification(&folder)
# Display an error message if a folder has been modified since the time
# in $in{'mod'}
sub check_modification
{
local $newmod = &modification_time($_[0]);
if ($in{'mod'} && $in{'mod'} != $newmod && $userconfig{'check_mod'}) {
	# Changed!
	&error(&text('emodified', "index.cgi?folder=$_[0]->{'index'}"));
	}
}

# list_from_addresses()
# Returns a list of allowed From: addresses for the current user
sub list_from_addresses
{
local $http_host = $ENV{'HTTP_HOST'};
$http_host =~ s/:\d+$//;
if (&check_ipaddress($http_host)) {
	# Try to reverse-lookup IP
	local $rev = gethostbyaddr(inet_aton($acptip), AF_INET);
	$http_host = $rev if ($rev);
	}
$http_host =~ s/^(www|ftp|mail)\.//;
local @froms;
if ($config{'server_name'} eq 'ldap') {
	# Special mode - the From: addresses just come from LDAP
	local $entry = &get_user_ldap();
	push(@froms, $entry->get_value("mail"));
	push(@froms, $entry->get_value("mailAlternateAddress"));
	}
elsif ($remote_user =~ /\@/) {
	# From: address comes from username, which has an @ in it
	@froms = ( $remote_user );
	}
else {
	# Work out From: addresses from hostname
	local $hostname = $config{'server_name'} eq '*' ? $http_host :
		  $config{'server_name'} eq '' ? &get_system_hostname() :
						 $config{'server_name'};
	local @doms = split(/\s+/, $hostname);
	local $ru = $remote_user;
	$ru =~ s/\.\Q$http_host\E$//;
	if ($http_host =~ /^([^\.]+)/) {
		$ru =~ s/\.\Q$1\E//;
		}
	@froms = map { $ru.'@'.$_ } @doms;
	}
local @mfroms;
if ($config{'from_map'} && $remote_user !~ /\@/) {
	# Lookup username in from address mapping file, to get email.
	open(MAP, $config{'from_map'});
	while(<MAP>) {
		s/\r|\n//g;
		s/#.*$//;
		if (/^\s*(\S+)\s+(\S+)/ &&
		    ($1 eq $remote_user || &indexof($1, @froms) >= 0) &&
		    $config{'from_format'} == 0) {
			# Username on LHS matches
			push(@mfroms, $2);
			}
		elsif (/^\s*(\S+)\s+(\S+)/ &&
		    ($2 eq $remote_user || &indexof($2, @froms) >= 0) &&
		    $config{'from_format'} == 1) {
			# Username on RHS matches
			push(@mfroms, $1);
			}
		}
	close(MAP);
	}
if (@mfroms > 0) {
	# Got some results from mapping file .. use them
	if ($remote_user =~ /\@/) {
		# But still keep email-style login as the default
		@froms = ( $froms[0], @mfroms );
		}
	else {
		@froms = @mfroms;
		}
	}
local $ureal = $remote_user_info[6];
$ureal =~ s/,.*$//;
foreach $f (@froms) {
	$f = "\"$ureal\" <$f>"
		if ($ureal && $userconfig{'real_name'});
	}
return (\@froms, \@doms);
}

# update_delivery_notification(&mail, &folder)
# If the given mail is a DSN, update the original email so we know it has
# been read
sub update_delivery_notification
{
local ($mail, $folder) = @_;
return 0 if ($mail->{'header'}->{'content-type'} !~ /multipart\/report/i);
local $mid = $mail->{'header'}->{'message-id'};
&open_dsn_hash();
if ($dsnreplies{$mid} || $delreplies{$mid}) {
	# We have already done this DSN
	return 0;
	}
if (!defined($mail->{'body'}) && !$mail->{'parsed'} &&
    defined($mail->{'idx'})) {
	# This message has no body, perhaps because one wasn't fetched ..
	local @mail = &mailbox_list_mails($mail->{'idx'}, $mail->{'idx'},
					  $folder);
	$mail = $mail[$mail->{'idx'}];
	}
$dsnreplies{$mid} = $delreplies{$mid} = 1;

# Find the delivery or disposition status attachment
&parse_mail($mail);
local ($dsnattach) = grep { $_->{'header'}->{'content-type'} =~ /message\/disposition-notification/i } @{$mail->{'attach'}};
local ($delattach) = grep { $_->{'header'}->{'content-type'} =~ /message\/delivery-status/i } @{$mail->{'attach'}};

if ($dsnattach) {
	# Update the read status for the original message
	if ($dsnattach->{'data'} =~ /Original-Message-ID:\s*(.*)/) {
		$omid = $1;
		}
	else {
		return 0;
		}
	local ($faddr) = &split_addresses($mail->{'header'}->{'from'});
	&add_address_to_hash(\%dsnreplies, $omid, $faddr->[0]);
	return 1;
	}
elsif ($delattach) {
	# Update the delivery status for the original message, which will be
	# in a separate attachment
	local ($origattach) = grep { $_->{'header'}->{'content-type'} =~ /text\/rfc822-headers|message\/rfc822/i } @{$mail->{'attach'}};
	return 0 if (!$origattach);
	local $origmail = &extract_mail($origattach->{'data'});
	local $omid = $origmail->{'header'}->{'message-id'};
	return 0 if (!$omid);
	local ($faddr) = &split_addresses($origmail->{'header'}->{'from'});
	local $ds = &parse_delivery_status($delattach->{'data'});
	if ($ds->{'status'} =~ /^2\./) {
		&add_address_to_hash(\%delreplies, $omid, $faddr->[0]);
		}
	elsif ($ds->{'status'} =~ /^5\./) {
		&add_address_to_hash(\%delreplies, $omid, "!".$faddr->[0]);
		}
	}
else {
	return 0;
	}
}

# add_address_to_hash(&hash, messageid, address)
sub add_address_to_hash
{
local @cv = split(/\s+/, $_[0]->{$_[1]});
local $idx = &indexof($_[2], @cv);
if ($idx < 0) {
	$_[0]->{$_[1]} .= " " if (@cv);
	$_[0]->{$_[1]} .= time()." ".$_[2];
	}
}

# open_dsn_hash()
# Ensure the %dsnreplies and %delreplies hashes are tied
sub open_dsn_hash
{
if (!defined(%dsnreplies)) {
	&open_dbm_db(\%dsnreplies, "$user_module_config_directory/dsnreplies", 0600);
	}
if (!defined(%delreplies)) {
	&open_dbm_db(\%delreplies, "$user_module_config_directory/delreplies", 0600);
	}
}

# open_read_hash()
# Ensure the %read hash is tied
sub open_read_hash
{
if (!defined(%read)) {
	&open_dbm_db(\%read, "$user_module_config_directory/read", 0600);
	}
}

# get_special_folder()
# Returns the virtual folder containing messages marked as 'special', or undef
# if not defined yet.
sub get_special_folder
{
if (defined($special_folder_cache)) {
	return $special_folder_cache || undef;
	}
else {
	# Find for real
	local @folders = &list_folders();
	local ($s) = grep { $_->{'type'} == 6 &&
			    $_->{'id'} == $special_folder_id } @folders;
	$special_folder_cache = $s ? $s : "";
	return $s;
	}
}

# get_mail_read(&folder, &mail)
# Returns the read-mode flag for some email (0=unread, 1=read, 2=special)
# Checks the special folder first, then the read DBM
sub get_mail_read
{
local ($folder, $mail) = @_;
if (defined($get_mail_read_cache{$mail->{'id'}})) {
	# Already checked in this run
	return $get_mail_read_cache{$mail->{'id'}};
	}
local $sfolder = &get_special_folder();
local ($realfolder, $realid) = &get_underlying_folder($folder, $mail);
local $special = 0;
if ($sfolder) {
	# Is it in the special folder? If so, definately special
	local ($spec) = grep { $_->[0] eq $realfolder &&
			       $_->[1] eq $realid } @{$sfolder->{'members'}};
	if ($spec) {
		$special = 2;
		}
	}
local $rv;
if ($realfolder->{'flags'}) {
	# For folders which can store the flags in the message itself (such
	# as IMAP), use that
	$rv = ($mail->{'read'} ? 1 : 0) +
	      ($mail->{'special'} ? 2 : 0) +
	      ($mail->{'replied'} ? 4 : 0);
	}
if (!$realfolder->{'flags'} || ($realfolder->{'flags'} == 2 && !$rv)) {
	# Check read hash if this folder doesn't support flagging, or if
	# it couldn't give us an answer.
	&open_read_hash();
	$rv = int($read{$mail->{'header'}->{'message-id'}});
	}
$rv = ($rv|$special);
$get_mail_read_cache{$mail->{'id'}} = $rv;
return $rv;
}

# set_mail_read(&folder, &mail, read)
# Sets the read flag for some email, possibly updating the special folder.
# Read flags are 0=unread, 1=read, 2=special. Add 4 for replied.
sub set_mail_read
{
local ($folder, $mail, $read) = @_;
local ($realfolder, $realid);
if ($mail->{'id'}) {
	local $sfolder = &get_special_folder();
	($realfolder, $realid) = &get_underlying_folder($folder, $mail);
	print DEBUG "id=$mail->{'id'} realid=$realid\n";
	if ($sfolder || ($read&2) != 0) {
		local $spec;
		if ($sfolder) {
			# Is it already there?
			($spec) = grep { $_->[0] eq $realfolder &&
					 $_->[1] eq $realid }
				       @{$sfolder->{'members'}};
			print DEBUG "spec=$spec\n";
			}
		if (($read&2) != 0 && !$spec) {
			# Add to special folder
			if (!$sfolder) {
				# Create first
				$sfolder = { 'id' => $special_folder_id,
					     'type' => 6,
					     'name' => $text{'mail_special'},
					     'delete' => 1,
					     'members' => [ [
						$realfolder, $realid ] ],
					   };
				&save_folder($sfolder);
				$special_folder_cache = $sfolder;
				}
			else {
				# Just add
				push(@{$sfolder->{'members'}},
				     [ $realfolder,$realid ]);
				&save_folder($sfolder, $sfolder);
				}
			}
		elsif (($read&2) == 0 && $spec) {
			# Remove from special folder
			$sfolder->{'members'} =
			    [ grep { $_ ne $spec } @{$sfolder->{'members'}} ];
			&save_folder($sfolder, $sfolder);
			}
		}
	if ($realfolder->{'flags'}) {
		# Set the flag in the email itself, such as on an IMAP server
		local $mail->{'id'} = $realid; # So that IMAP can find it by UID
		&mailbox_set_read_flag($realfolder, $mail,
				       ($read&1),	    # Read
				       ($read&2),	    # Special
				       ($read&4));	    # Replied
		if ($realid ne $mail->{'id'} && ($read&2) && !$spec) {
			# ID changed .. fix in special folder
			($spec) = grep { $_->[0] eq $realfolder &&
					 $_->[1] eq $realid }
				       @{$sfolder->{'members'}};
			if ($spec) {
				$spec->[1] = $mail->{'id'};
				&save_folder($sfolder, $sfolder);
				}
			}
		}
	}
if (!$realfolder || !$realfolder->{'flags'} || $realfolder->{'flags'} == 2) {
	# Update read hash
	&open_read_hash();
	if ($read == 0) {
		delete($read{$mail->{'header'}->{'message-id'}});
		}
	else {
		$read{$mail->{'header'}->{'message-id'}} = $read;
		}
	}
if ($mail->{'id'}) {
	$get_mail_read_cache{$mail->{'id'}} = $read;
	}
}

# get_underlying_folder(&folder, &mail)
# For mail in some virtual folder, returns the real folder and ID
sub get_underlying_folder
{
local ($realfolder, $mail) = @_;
local $realid = $mail->{'id'};
while($realfolder->{'type'} == 5 || $realfolder->{'type'} == 6) {
	local ($sfn, $sid) = split(/\t+/, $realid, 2);
	$realfolder = &find_subfolder($realfolder, $sfn);
	$realid = $sid;
	}
return ($realfolder, $realid);
}

# spam_report_cmd()
# Returns a command for reporting spam, or undef if none
sub spam_report_cmd
{
local %sconfig = &foreign_config("spam");
if ($config{'spam_report'} eq 'sa_learn') {
	return &has_command($sconfig{'sa_learn'}) ? "$sconfig{'sa_learn'} --spam --mbox" : undef;
	}
elsif ($config{'spam_report'} eq 'spamassassin') {
	return &has_command($sconfig{'spamassassin'}) ? "$sconfig{'spamassassin'} --r" : undef;
	}
else {
	return &has_command($sconfig{'sa_learn'}) ?
		"$sconfig{'sa_learn'} --spam --mbox" :
	       &has_command($sconfig{'spamassassin'}) ?
		"$sconfig{'spamassassin'} --r" : undef;
	}
}

# ham_report_cmd()
# Returns a command for reporting ham, or undef if none
sub ham_report_cmd
{
local %sconfig = &foreign_config("spam");
return &has_command($sconfig{'sa_learn'}) ? "$sconfig{'sa_learn'} --ham --mbox" : undef;
}

# can_report_spam(&folder)
sub can_report_spam
{
return (&foreign_available("spam") || $config{'spam_always'}) &&
       &foreign_installed("spam") &&
       !$_[0]->{'sent'} && !$_[0]->{'drafts'} &&
       &spam_report_cmd();
}

# can_report_ham(&folder)
sub can_report_ham
{
return (&foreign_available("spam") || $config{'spam_always'}) &&
       &foreign_installed("spam") &&
       !$_[0]->{'sent'} && !$_[0]->{'drafts'} &&
       &ham_report_cmd();
}

# filter_by_status(&messages, status)
# Returns only messages with a particular status
sub filter_by_status
{
local %read;
dbmopen(%read, "$user_module_config_directory/read", 0600);
local (@rv, $mail);
foreach $mail (@{$_[0]}) {
	local $mid = $mail->{'header'}->{'message-id'};
	if ($read{$mid} == $_[1]) {
		push(@rv, $mail);
		}
	}
dbmclose(%read);
return @rv;
}

# show_mailbox_buttons(number, &folders, current-folder, &mail)
# Prints HTML for buttons to appear above or below a mail list
sub show_mailbox_buttons
{
local ($num, $folders, $folder, $mail) = @_;
local $spacer = "&nbsp;\n";

# Compose button
if ($userconfig{'open_mode'}) {
	# Compose button needs to pop up a window
	print &ui_submit($text{'mail_compose'}, "new", undef,
	      "onClick='window.open(\"reply_mail.cgi?new=1\", \"compose\", \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); return false'>");
	}
else {
	# Compose button can just submit and redirect
	print &ui_submit($text{'mail_compose'}, "new");
	}
print $spacer;

# Forward selected
if (@mail) {
	if ($userconfig{'open_mode'}) {
		print &ui_submit($text{'mail_forward'}, "forward", undef,
			"onClick='args = \"folder=$folder->{'index'}\"; for(i=0; i<form.d.length; i++) { if (form.d[i].checked) { args += \"&mailforward=\"+escape(form.d[i].value); } } window.open(\"reply_mail.cgi?\"+args, \"compose\", \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); return false'>");
		}
	else {
		# Forward button can just be a normal submit
		print &ui_submit($text{'mail_forward'}, "forward");
		}
	print $spacer;
	}

# Mark as buttons
if (@$mail) {
	foreach my $i (0 .. 2) {
		print &ui_submit($text{'view_markas'.$i}, 'markas'.$i);
		}
	print $spacer;
	}
	
# Copy/move to folder
if (@mail && @$folders > 1) {
	print &movecopy_select($_[0], $folders, $folder);
	print $spacer;
	}

# Delete
if (@mail) {
	print &ui_submit($text{'mail_delete'}, "delete");
	print $spacer;
	}

# Blacklist / report spam
if (@mail && (&can_report_spam($folder) &&
    	      $userconfig{'spam_buttons'} =~ /list/ || $folder->{'spam'})) {
	print &ui_submit($text{'mail_black'}, "black");
	if ($userconfig{'spam_del'}) {
		print &ui_submit($text{'view_razordel'}, "razor");
		}
	else {
		print &ui_submit($text{'view_razor'}, "razor");
		}
	print $spacer;
	}

# Whitelist / report ham
if (@mail && (&can_report_ham($folder) &&
	      $userconfig{'ham_buttons'} =~ /list/ ||
	      $folder->{'spam'})) {
	if ($userconfig{'white_move'} && $folder->{'spam'}) {
		print &ui_submit($text{'mail_whitemove'}, "white");
		}
	else {
		print &ui_submit($text{'mail_white'}, "white");
		}
	if ($userconfig{'ham_move'} && $folder->{'spam'}) {
		print &ui_submit($text{'view_hammove'}, "ham");
		}
	else {
		print &ui_submit($text{'view_ham'}, "ham");
		}
	print $spacer;
	}

if ($userconfig{'open_mode'}) {
	# Show mass open button
	print &ui_submit($text{'mail_open'}, "new", undef,
	      "onClick='for(i=0; i<form.d.length; i++) { if (form.d[i].checked) { window.open(\"view_mail.cgi?folder=$folder->{'index'}&idx=\"+escape(form.d[i].value), \"view\"+i, \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); } } return false'>");
	print $spacer;
	}

print "<br>\n";
}

# expand_to(list)
# Given a string containing multiple email addresses and group names,
# expand out the group names (if any)
sub expand_to
{
$_[0] =~ s/\r//g;
$_[0] =~ s/\n/ /g;
%address_groups = map { $_->[0], $_->[1] } &list_address_groups()
	if (!defined(%address_groups));
if ($userconfig{'real_expand'}) {
	%real_expand_names = map { $_->[1], $_->[0] }
				 grep { $_->[1] } &list_addresses()
		if (!defined(%real_expand_names));
	}
local @addrs = &split_addresses($_[0]);
local (@alladdrs, $a, $expanded);
foreach $a (@addrs) {
	if (defined($address_groups{$a->[0]})) {
		push(@alladdrs, &split_addresses($address_groups{$a->[0]}));
		$expanded++;
		}
	elsif (defined($real_expand_names{$a->[0]})) {
		push(@alladdrs, &split_addresses($real_expand_names{$a->[0]}));
		$expanded++;
		}
	else {
		push(@alladdrs, $a);
		}
	}
return $expanded ? join(", ", map { $_->[2] } @alladdrs)
		 : $_[0];
}

# connect_qmail_ldap([return-error])
# Connect to the LDAP server used for Qmail. Returns an LDAP handle on success,
# or an error message on failure.
sub connect_qmail_ldap
{
eval "use Net::LDAP";
if ($@) {
	local $err = &text('ldap_emod', "<tt>Net::LDAP</tt>");
	if ($_[0]) { return $err; }
	else { &error($err); }
	}

# Connect to server
local $port = $config{'ldap_port'} || 389;
local $ldap = Net::LDAP->new($config{'ldap_host'}, port => $port);
if (!$ldap) {
	local $err = &text('ldap_econn',
			   "<tt>$config{'ldap_host'}</tt>","<tt>$port</tt>");
	if ($_[0]) { return $err; }
	else { &error($err); }
	}

# Start TLS if configured
if ($config{'ldap_tls'}) {
	$ldap->start_tls();
	}

# Login
local $mesg;
if ($config{'ldap_login'}) {
	$mesg = $ldap->bind(dn => $config{'ldap_login'},
			    password => $config{'ldap_pass'});
	}
else {
	$mesg = $ldap->bind(anonymous => 1);
	}
if (!$mesg || $mesg->code) {
	local $err = &text('ldap_elogin', "<tt>$config{'ldap_host'}</tt>",
		     $dn, $mesg ? $mesg->error : "Unknown error");
	if ($_[0]) { return $err; }
	else { &error($err); }
	}
return $ldap;
}

# get_user_ldap()
# Looks up the LDAP information for the current mailbox user, and returns a
# Net::LDAP::Entry object.
sub get_user_ldap
{
local $ldap = &connect_qmail_ldap();
local $rv = $ldap->search(base => $config{'ldap_base'},
			  filter => "(uid=$remote_user)");
&error("Failed to get LDAP entry : ",$rv->error) if ($rv->code);
local ($u) = $rv->all_entries();
&error("Could not find LDAP entry") if (!$u);
$ldap->unbind();
return $u;
}

# would_exceed_quota(&folder, &mail, ...)
# Checks if the addition of a given email messages
# exceed any quotas. Called when saving a draft or copying an email.
# Returns undef if OK, or an error message
sub would_exceed_quota
{
local ($folder, @mail) = @_;

# Get quotas in force
local ($total, $count, $totalquota, $countquota) = &get_user_quota();
return undef if (!$totalquota && !$countquota);

# Work out how much we are adding
local $m;
local $adding = 0;
foreach $m (@mail) {
	$adding += ($m->{'size'} || &mail_size($m));
	}

# Check against size limit
if ($totalquota && $total + $adding > $totalquota) {
	return &text('quota_inbox', &nice_size($totalquota));
	}

# Check against count limit
if ($countquota && $count + scalar(@mail) > $countquota) {
	return &text('quota_inbox2', $countquota);
	}

return undef;
}

# get_user_quota()
# If any quotas are in force, returns the total size of all folders, the total
# number of messages, the maximum size, and the maximum number of messages
sub get_user_quota
{
return ( ) if (!$config{'ldap_quotas'} && !$config{'max_quota'});

# Work out current size of all local folders
local $f;
local $total = 0;
local $count = 0;
foreach $f (&list_folders()) {
	if ($f->{'type'} == 0 || $f->{'type'} == 1 || $f->{'type'} == 3) {
		$total += &folder_size($f);
		$count += &mailbox_folder_size($f);
		}
	}

# Get the configured quota
local $configquota = $config{'max_quota'};

# Get the LDAP limit
local $ldapquota;
local $ldapcount;
if ($config{'ldap_host'} && $config{'ldap_quotas'}) {
	local $entry = &get_user_ldap();
	$ldapquota = $entry->get_value("mailQuotaSize");
	$ldapcount = $entry->get_value("mailQuotaCount");
	}

local $quota = defined($configquota) && defined($ldapquota) ?
		min($configquota, $ldapquota) :
	       defined($configquota) ? $configquota :
	       defined($ldapquota) ? $ldapquota : undef;
return ($total, $count, $quota, $ldapcount);
}

sub min
{
return $_[0] < $_[1] ? $_[0] : $_[1];
}

# get_sort_field(&folder)
# Returns the field and direction on which sorting is done for the current user
sub get_sort_field
{
local ($folder) = @_;
return ( ) if (!$folder->{'sortable'});
local $file = &folder_name($folder);
$file =~ s/\//_/g;
my %sort;
if (&read_file_cached("$user_module_config_directory/sort.$file", \%sort)) {
	return ($sort{'field'}, $sort{'dir'});
	}
return ( );
}

# save_sort_field(&folder, field, dir)
sub save_sort_field
{
local $file = &folder_name($_[0]);
$file =~ s/\//_/g;
my %sort = ( 'field' => $_[1], 'dir' => $_[2] );
&write_file("$user_module_config_directory/sort.$file", \%sort);
}

# field_sort_link(title, field, folder-idx, start)
# Returns HTML for a link to switch sorting mode
sub field_sort_link
{
local ($title, $field, $folder, $start) = @_;
local ($sortfield, $sortdir) = &get_sort_field($folder);
local $dir = $sortfield eq $field ? !$sortdir : 0;
local $img = $sortfield eq $field && $dir ? "sortascgrey.gif" :
	     $sortfield eq $field && !$dir ? "sortdescgrey.gif" :
	     $dir ? "sortasc.gif" : "sortdesc.gif";
if ($folder->{'sortable'}) {
	return "<a href='sort.cgi?field=".&urlize($field)."&dir=".&urlize($dir)."&folder=".&urlize($folder->{'index'})."&start=".&urlize($start)."'>$title <img valign=middle src=../images/$img border=0>";
	}
else {
	return $title;
	}
}

# view_mail_link(&folder, id, start, from-to-text)
sub view_mail_link
{
local ($folder, $id, $start, $txt) = @_;
local $qid = &urlize($id);
local $qstart = &urlize($start);
local $url = "view_mail.cgi?start=$qstart&id=$qid&folder=$folder->{'index'}";
if ($userconfig{'open_mode'}) {
	return "<a href='' onClick='window.open(\"$url\", \"viewmail\", \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); return false'>".
	       &simplify_from($txt)."</a>";
	}
else {
	return "<a href='$url'>".&simplify_from($txt)."</a>";
	}
}

# mail_page_header(title, headstuff, bodystuff)
sub mail_page_header
{
if ($userconfig{'open_mode'}) {
	&popup_header(@_);
	}
else {
	&ui_print_header(undef, $_[0], "", undef, 0, 0, 0, undef, $_[1], $_[2]);
	}
}

# mail_page_footer(link, text, ...)
sub mail_page_footer
{
if ($userconfig{'open_mode'}) {
	&popup_footer();
	}
else {
	&ui_print_footer(@_);
	}
}

# get_auto_schedule(&folder)
# Returns the automatic schedule structure for the given folder
sub get_auto_schedule
{
local ($folder) = @_;
local $id = $folder->{'id'} || &urlize($folder->{'file'});
local %rv;
&read_file("$user_module_config_directory/$id.sched", \%rv) ||
	return undef;
return \%rv;
}

# save_auto_schedule(&folder, &sched)
# Updates the automatic schedule structure for the given folder
sub save_auto_schedule
{
local ($folder, $sched) = @_;
local $id = $folder->{'id'} || &urlize($folder->{'file'});
if ($sched) {
	&write_file("$user_module_config_directory/$id.sched", $sched);
	}
else {
	unlink("$user_module_config_directory/$id.sched");
	}
}

# setup_auto_cron()
# Creates the Cron job that runs auto.pl
sub setup_auto_cron
{
&foreign_require("cron", "cron-lib.pl");
local @jobs = &cron::list_cron_jobs();
local ($job) = grep { $_->{'command'} eq $auto_cmd &&
		      $_->{'user'} eq $remote_user } @jobs;
if (!$job) {
	$job = { 'command' => $auto_cmd,
		 'active' => 1,
		 'user' => $remote_user,
		 'mins' => int(rand()*60),
		 'hours' => '*',
		 'days' => '*',
		 'months' => '*',
		 'weekdays' => '*' };
	&cron::create_cron_job($job);
	}
&cron::create_wrapper($auto_cmd, $module_name, "auto.pl");
}

# addressbook_to_whitelist()
# If SpamAssassin is installed, update the user's whitelist with all
# addressbook entries
sub addressbook_to_whitelist
{
if ($userconfig{'white_book'} && &foreign_installed("spam")) {
	&foreign_require("spam", "spam-lib.pl");
	local $conf = &spam::get_config();
	local @white = &spam::find_value("whitelist_from", $conf);
	local %white = map { lc($_), 1 } @white;
	foreach my $a (&list_addresses()) {
		if (!$white{lc($a->[0])}) {
			push(@white, $a->[0]);
			}
		}
	&spam::save_directives($conf, "whitelist_from", \@white, 1);
	&flush_file_lines();
	}
}

# addressbook_add_whitelist(address, ...)
# Add some email address to the whitelist
sub addressbook_add_whitelist
{
local (@addrs) = @_;
if (&foreign_installed("spam")) {
	&foreign_require("spam", "spam-lib.pl");
	local $conf = &spam::get_config();
	local @white = &spam::find_value("whitelist_from", $conf);
	local %white = map { lc($_), 1 } @white;
	foreach my $a (@addrs) {
		if (!$white{lc($a)}) {
			push(@white, $a);
			}
		}
	&spam::save_directives($conf, "whitelist_from", \@white, 1);
	&flush_file_lines();
	}
}

# addressbook_remove_whitelist(address)
# Delete some address from the whitelist
sub addressbook_remove_whitelist
{
local ($addr) = @_;
if ($userconfig{'white_book'} && &foreign_installed("spam")) {
	&foreign_require("spam", "spam-lib.pl");
	local $conf = &spam::get_config();
	local @white = &spam::find_value("whitelist_from", $conf);
	@white = grep { lc($_) ne lc($addr) } @white;
	&spam::save_directives($conf, "whitelist_from", \@white, 1);
	&flush_file_lines();
	}
}

# left_right_align(left, right)
# Returns a table for left and right aligning some HTML
sub left_right_align
{
local ($l, $r) = @_;
return "<table cellpadding=0 cellspacing=0 width=100%><tr><td align=left>$l</td><td align=right>$r</td></tr></table>";
}

# Returns 1 if downloading all attachment is possible
sub can_download_all
{
return &has_command("zip");
}

# select_status_link(name, form, &folder, &mails, start, end, status, label)
# Returns HTML for selecting messages
sub select_status_link
{
return &theme_select_status_link(@_) if (defined(&theme_select_status_link));
local ($name, $formno, $folder, $mail, $start, $end, $status, $label) = @_;
$formno = int($formno);
local @sel;
for(my $i=$start; $i<=$end; $i++) {
	local $read = &get_mail_read($folder, $mail->[$i]);
	if ($status == 0) {
		push(@sel, ($read&1) ? 0 : 1);
		}
	elsif ($status == 1) {
		push(@sel, ($read&1) ? 1 : 0);
		}
	elsif ($status == 2) {
		push(@sel, ($read&2) ? 1 : 0);
		}
	}
local $js = "var sel = [ ".join(",", @sel)." ]; ";
$js .= "for(var i=0; i<sel.length; i++) { document.forms[$formno].${name}[i].checked = sel[i]; }";
$js .= "return false;";
return "<a href='#' onClick='$js'>$label</a>";
}

# address_link(address)
# Turns an address into a link for adding it to the addressbook
sub address_link
{
## split_addresses() pattern-matches "[<>]", so 7-bit encodings
## such as ISO-2022-JP must be converted to EUC before feeding.
local @addrs = &split_addresses(&eucconv(&decode_mimewords($_[0])));
local @rv;
foreach $a (@addrs) {
	## TODO: is $inbook{} MIME or locale-encoded?
	if ($inbook{lc($a->[0])}) {
		push(@rv, &eucconv_and_escape($a->[2]));
		}
	else {
		## name= will be EUC encoded now since split_addresses()
		## is feeded with EUC converted value.
		push(@rv, "<a href='add_address.cgi?addr=".&urlize($a->[0]).
			  "&name=".&urlize($a->[1])."&id=$qid".
			  "&folder=$in{'folder'}&start=$in{'start'}$subs'>".
			  &eucconv_and_escape($a->[2])."</a>");
		}
	}
return join(" , ", @rv);
}

# get_preferred_from_address()
# Returns the from address for the current user, which may come from their
# address book, or from the module config. Will include the real name too,
# where possible.
sub get_preferred_from_address
{
local ($froms, $doms) = &list_from_addresses();
local ($defaddr) = grep { $_->[3] == 2 } &list_addresses();
if ($defaddr) {
	# From address book
	return $defaddr->[1] ? "\"$defaddr->[1]\" <$defaddr->[0]>"
			      : $defaddr->[0];
	}
else {
	# Account default
	return $froms->[0];
	}
}

# remove_own_email(addresses)
# Given a string containing email addresses, remove those belonging to the user
sub remove_own_email
{
local ($addrs) = @_;
local @addrs = &split_addresses($addrs);

# Build our own addresses
local %own;
foreach my $a (&list_addresses()) {
	$own{$a->[0]}++ if ($a->[3]);
	}
local ($froms) = &list_from_addresses();
foreach my $f (@$froms) {
	local ($addr) = &split_addresses($f);
	$own{$addr->[0]}++;
	}

# See what we have to remove
local @others = grep { !$own{$_->[0]} } @addrs;
if (scalar(@others) == scalar(@addrs) || !scalar(@others)) {
	# No need to change the string
	return $addrs;
	}
else {
	# Return just those left
	return join(", ", map { $_->[2] } @others);
	}
}

1;

