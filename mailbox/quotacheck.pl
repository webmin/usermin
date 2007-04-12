#!/usr/bin/perl
# Called from Procmail to check if some user is over his LDAP quota, and if
# so bounces it. Exits with 0 if OK, 100 if over quota, or 111 if a temporary
# error occurred

use Net::LDAP;

@ARGV == 6 || temperr("usage: quotacheck.pl <email> <ldap-host> <ldap-port> <ldap-based> <ldap-login> <ldap-pass>");
($email, $host, $port, $base, $login, $pass) = @ARGV;

# Read in email
$size = 0;
while(<STDIN>) {
	$size += length($_);
	}

# Connect to LDAP
$ldap = Net::LDAP->new($host, port => $port);
$ldap || temperr("Failed to connect to LDAP server $host:$port");
$mesg = $ldap->bind(dn => $login, password => $pass);
if (!$mesg || $mesg->code) {
	temperr("Failed to login to LDAP server as $login : ",
		$mesg ? $mesg->error : "Unknown error");
	}

# Lookup the email address
$rv = $ldap->search(base => $base,
		    filter => "(|(mail=$email)(mailAlternateAddress=$email))");
if ($rv->code) {
	temperr("Failed to lookup user in LDAP : ",$rv->error);
	}
($user) = $rv->all_entries();
exit(0) if (!$user);		# Non-LDAP, so no quota

# Check the current size of all the user's folders
$mms = $user->get_value('mailMessageStore');
$inbox = { 'type' => &folder_type($mms),
	   'file' => $mms };
@folders = ( $inbox );
$fdir = $user->get_value('homeDirectory')."/mail";
opendir(DIR, $fdir);
while($f = readdir(DIR)) {
	next if ($f eq "." || $f eq "..");
	$path = "$fdir/$f";
	$folder = { 'type' => &folder_type($path),
		    'file' => $path };
	push(@folders, $folder);
	}
closedir(DIR);
$total = &folder_size(@folders);
print "Current size: $total\n";
print "Extra size: $size\n";

# Compare to quota
$quota = $user->get_value('mailQuotaSize');
print "Allowed quota: $quota\n";
if ($quota && $total + $size > $quota) {
	print STDERR "Quota exceeded\n";
	exit(100);
	}
exit(0);

sub temperr
{
print STDERR @_,"\n";
exit(111);
}

# folder_size(&folder, ...)
# Sets the 'size' field of one or more folders, and returns the total
sub folder_size
{
local ($f, $total);
foreach $f (@_) {
	if ($f->{'type'} == 0) {
		# Single mail file - size is easy
		local @st = stat($f->{'file'});
		$f->{'size'} = $st[7];
		}
	elsif ($f->{'type'} == 1) {
		# Maildir folder size is that of all mail files
		local $qd;
		$f->{'size'} = 0;
		foreach $qd ('cur', 'new') {
			local $mf;
			opendir(QDIR, "$f->{'file'}/$qd");
			while($mf = readdir(QDIR)) {
				next if ($mf eq "." || $mf eq "..");
				local @st = stat("$f->{'file'}/$qd/$mf");
				$f->{'size'} += $st[7];
				}
			closedir(QDIR);
			}
		}
	elsif ($f->{'type'} == 3) {
		# MH folder size is that of all mail files
		local $mf;
		$f->{'size'} = 0;
		opendir(MHDIR, $f->{'file'});
		while($mf = readdir(MHDIR)) {
			next if ($mf eq "." || $mf eq "..");
			local @st = stat("$f->{'file'}/$mf");
			$f->{'size'} += $st[7];
			}
		closedir(MHDIR);
		}
	elsif ($f->{'type'} == 5) {
		# Size of a combined folder is the size of all sub-folders
		return &folder_size(@{$f->{'subfolders'}});
		}
	else {
		# Cannot get size of a remote folder
		$f->{'size'} = undef;
		}
	$total += $f->{'size'};
	}
return $total;
}

# folder_type(file_or_dir)
sub folder_type
{
return -d "$_[0]/cur" ? 1 : -d $_[0] ? 3 : 0;
}



