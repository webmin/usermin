#!/usr/local/bin/perl
# save_folder.cgi
# Create, modify or delete a folder
# XXX check for external clash

## 2007/02/19 kabe:
##  do not "keys(%isdir)==3" for Maildir/ check; Courier-IMAP et al
##  could add other things beside tmp/, new/, cur/.
##  (Usermin also adds .usermin-maildircache by itself)

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
if (!$in{'new'}) {
	$folder = $folders[$in{'idx'}];
	$old = { %$folder };
	}
else {
	$folder->{'mode'} = $in{'mode'};
	}
&error_setup($text{'save_err'});

# Validate inputs
if (!$in{'delete'}) {
	&parse_folder_options($folder, $in{'mode'}, \%in);
	}

# Can this type of folder be edited?
if ($in{'mode'} == 0) {
	$folder_types{'local'} || &error($text{'save_ecannot'});
	}
elsif ($in{'mode'} == 1) {
	$folder_types{'ext'} || &error($text{'save_ecannot'});
	}

if ($in{'mode'} == 0) {
	if ($in{'delete'} && $in{'confirm'}) {
		# Deleting a folder within ~/mail
		&delete_folder($folder);
		}
	elsif ($in{'delete'} && !$in{'confirm'}) {
		# Confirming a delete
		&ui_print_header(undef, $text{'save_title'}, "");

		print "<form action=save_folder.cgi>\n";
		print "<input type=hidden name=idx value='$in{'idx'}'>\n";
		print "<input type=hidden name=mode value='$in{'mode'}'>\n";
		print "<input type=hidden name=confirm value='1'>\n";
		$sz = &nice_size(&folder_size($folder));
		print "<center><b>",&text('save_rusure', $folder->{'name'},
			  "<tt>$folder->{'file'}</tt>", $sz),"</b><p>\n";
		print "<input type=submit name=delete ",
		      "value='$text{'save_delete'}'>\n";
		print "</center></form>\n";

		&ui_print_footer("list_folders.cgi", $text{'folders_return'});
		exit;
		}
	else {
		# Creating or renaming a folder within ~/mail
		$in{'name'} =~ /\S/ || &error($text{'save_ename'});
		$in{'name'} =~ /\.\./ && &error($text{'save_ename2'});
		$in{'name'} ne 'sentmail' && $in{'name'} ne 'drafts' ||
			&error($text{'save_esys'});
		$path = "$folders_dir/$in{'name'}";
		if ($folders_dir eq "$remote_user_info[7]/Maildir") {
			# Maildir sub-folder .. put a . in the name
			$path =~ s/([^\/]+)$/.$1/;
			}
		if ($old && $old->{'name'} ne $in{'name'}) {
			($clash) = grep { $_->{'file'} eq $path } @folders;
			$clash && &error($text{'save_eclash'});
			}
		$folder->{'type'} = $in{'type'};
		$folder->{'name'} = $in{'name'};
		&save_folder($folder, $old);
		}
	}
elsif ($in{'mode'} == 1) {
	if ($in{'delete'}) {
		# Just remove from list of external folders
		&delete_folder($folder);
		}
	else {
		# Adding or updating an external folder
		&verify_external($in{'file'});
		if ($old && $in{'file'} ne $old->{'file'}) {
			($clash) = grep { $_->{'file'} eq $in{'file'} }
					@folders;
			$clash && &error($text{'save_eclash'});
			}
		$in{'name'} || &error($text{'save_ename'});
		$folder->{'name'} = $in{'name'};
		$folder->{'file'} = $in{'file'};
		&save_folder($folder, $old);
		}
	}
elsif ($in{'mode'} == 2) {
	# Changing the path to the sent mail folder
	if ($in{'sent_def'}) {
		$folder->{'file'} = "$folders_dir/sentmail";
		}
	else {
		&verify_external($in{'sent'});
		$folder->{'file'} = $in{'sent'};
		}
	&save_folder($folder);
	}
&redirect("list_folders.cgi?refresh=".&urlize($folder->{'name'}));

sub verify_external
{
if (-d $_[0]) {
	local ($f, %isdir);
	opendir(DIR, $_[0]);
	foreach $f (readdir(DIR)) {
		$isdir{$f}++ if (-d "$_[0]/$f" && $f ne "." && $f ne "..");
		}
	closedir(DIR);
	if (keys(%isdir)) {
		$isdir{'cur'} && $isdir{'new'} && $isdir{'tmp'} ||
			&error(&text('save_emaildir', $_[0]));
		}
	}
elsif (-r $_[0]) {
	open(FOLDER, $_[0]);
	local $line = <FOLDER>;
	close(FOLDER);
	!$line || $line =~ /^From\s+(\S+).*\d+/ ||
		&error(&text('save_embox', $_[0]));
	}
else {
	&error(&text('save_efile', $_[0]));
	}
$_[0] =~ /^\Q$folders_dir\E\// && &error(&text('save_eindir', $folders_dir));
}

