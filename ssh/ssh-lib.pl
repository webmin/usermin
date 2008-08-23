# ssh-lib.pl
# Common functions for manipulating the users .ssh directory files

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();

$ssh_directory = "$remote_user_info[7]/.ssh";
$ssh_client_config = "$ssh_directory/config";
$authorized_keys = "$ssh_directory/authorized_keys";
$known_hosts = "$ssh_directory/known_hosts";

# find_value(name, &config)
sub find_value
{
foreach $c (@{$_[1]}) {
	if (lc($c->{'name'}) eq lc($_[0])) {
		return wantarray ? @{$c->{'values'}} : $c->{'values'}->[0];
		}
	}
return wantarray ? ( ) : undef;
}

# find(value, &config)
sub find
{
local @rv;
foreach $c (@{$_[1]}) {
	if (lc($c->{'name'}) eq lc($_[0])) {
		push(@rv, $c);
		}
	}
return wantarray ? @rv : $rv[0];
}

# save_directive(name, &config, [value*])
sub save_directive
{
local @o = &find($_[0], $_[1]);
local @n = grep { defined($_) } @_[2..@_-1];
local $lref = &read_file_lines($_[1]->[0]->{'file'});
local $id = ("\t" x $_[1]->[0]->{'indent'});
local $i;
for($i=0; $i<@o || $i<@n; $i++) {
	if ($o[$i] && $n[$i]) {
		# Replacing a line
		$lref->[$o[$i]->{'line'}] = "$id$_[0] $n[$i]";
		}
	elsif ($o[$i]) {
		# Removing a line
		splice(@$lref, $o[$i]->{'line'}, 1);
		foreach $c (@{$_[1]}) {
			if ($c->{'line'} > $o[$i]->{'line'}) {
				$c->{'line'}--;
				}
			}
		}
	elsif ($n[$i]) {
		# Adding a line
		local $ll = $_[1]->[@{$_[1]}-1]->{'line'};
		splice(@$lref, $ll+1, 0, "$id$_[0] $n[$i]");
		}
	}
}

# scmd(double)
sub scmd
{
if ($cmd_count % 2 == 0) {
	print "<tr>\n";
	}
elsif ($_[0]) {
	print "<td colspan=2></td> </tr>\n";
	print "<tr>\n";
	$cmd_count = 0;
	}
$cmd_count += ($_[0] ? 2 : 1);
}

# ecmd()
sub ecmd
{
if ($cmd_count % 2 == 0) {
	print "</tr>\n";
	}
}



# get_client_config()
# Returns a list of structures, one for each host
sub get_client_config
{
local @rv = ( { 'dummy' => 1,
		'indent' => 0,
		'file' => $ssh_client_config,
		'line' => -1,
		'eline' => -1 } );
local $host;
local $lnum = 0;
open(CLIENT, $ssh_client_config);
while(<CLIENT>) {
	s/\r|\n//g;
	s/^\s*#.*$//g;
	s/^\s*//g;
	local ($name, @values) = split(/\s+/, $_);
	if (lc($name) eq 'host') {
		# Start of new host
		$host = { 'name' => $name,
			  'values' => \@values,
			  'file' => $ssh_client_config,
			  'line' => $lnum,
			  'eline' => $lnum,
			  'members' => [ { 'dummy' => 1,
					   'indent' => 1,
					   'file' => $ssh_client_config,
					   'line' => $lnum } ] };
		push(@rv, $host);
		}
	elsif ($name) {
		# A directive inside a host
		local $dir = { 'name' => $name,
			       'values' => \@values,
			       'file' => $ssh_client_config,
			       'line' => $lnum };
		push(@{$host->{'members'}}, $dir);
		$host->{'eline'} = $lnum;
		}
	$lnum++;
	}
close(CLIENT);
return \@rv;
}

# create_host(&host)
sub create_host
{
local $lref = &read_file_lines($ssh_client_config);
$_[0]->{'line'} = $_[0]->{'eline'} = scalar(@$lref);
push(@$lref, "Host ".join(" ", @{$_[0]->{'values'}}));
$_[0]->{'members'} = [ { 'dummy' => 1,
			 'indent' => 1,
			 'file' => $ssh_client_config,
			 'line' => $_[0]->{'line'} } ];
}

# modify_host(&host)
sub modify_host
{
local $lref = &read_file_lines($ssh_client_config);
$lref->[$_[0]->{'line'}] = "Host ".join(" ", @{$_[0]->{'values'}});
}

# delete_host(&host)
sub delete_host
{
local $lref = &read_file_lines($ssh_client_config);
splice(@$lref, $_[0]->{'line'}, $_[0]->{'eline'} - $_[0]->{'line'} + 1);
}

# list_auths()
# Returns a list of authorized key structures
sub list_auths
{
local @rv;
local $lnum = 0;
open(AUTHS, $authorized_keys);
while(<AUTHS>) {
	s/\r|\n//g;
	s/#.*$//;
	if (/^((.*)\s+)?(\d+)\s+(\d+)\s+(\d+)\s+(\S+)$/) {
		# SSH1 style line
		local $auth = { 'name' => $6,
				'key' => $5,
				'exp' => $4,
				'bits' => $3,
				'opts' => $2,
				'type' => 1,
				'line' => $lnum,
				'index' => scalar(@rv) };
		$auth->{'opts'} =~ s/\s+$//;
		push(@rv, $auth);
		}
	elsif (/^((.*)\s+)?([a-z]\S+)\s+(\S+)\s+(\S+)/) {
		# SSH2 style line
		local $auth = { 'name' => $5,
				'key' => $4,
				'opts' => $2,
				'keytype' => $3,
				'type' => 2,
				'line' => $lnum,
				'index' => scalar(@rv) };
		$auth->{'opts'} =~ s/\s+$//;
		push(@rv, $auth);
		}
	$lnum++;
	}
close(AUTHS);
return @rv;
}

# create_auth(&auth)
sub create_auth
{
local $lref = &read_file_lines($authorized_keys);
push(@$lref, &auth_line($_[0]));
&flush_file_lines();
}

# delete_auth(&auth)
sub delete_auth
{
local $lref = &read_file_lines($authorized_keys);
splice(@$lref, $_[0]->{'line'}, 1);
&flush_file_lines();
}

# modify_auth(&auth)
sub modify_auth
{
local $lref = &read_file_lines($authorized_keys);
$lref->[$_[0]->{'line'}] = &auth_line($_[0]);
&flush_file_lines();
}

# parse_options(string, &opts)
sub parse_options
{
local $opts = $_[0];
while($opts =~ /^([^=\s,]+)=\"([^\"]*)\",?(.*)$/ ||
      $opts =~ /^([^=\s,]+)=([^=\s,]+),?(.*)$/ ||
      $opts =~ /^([^=\s,]+)(),?(.*)$/) {
	push(@{$_[1]->{$1}}, $2);
	$opts = $3;
	}
}

# join_options(&opts)
sub join_options
{
local @rv;
foreach $o (keys %{$_[0]}) {
	foreach $ov (@{$_[0]->{$o}}) {
		if (defined($ov)) {
			push(@rv, "$o=\"$ov\"");
			}
		else {
			push(@rv, $o);
			}
		}
	}
return join(",", @rv);
}

sub auth_line
{
if ($_[0]->{'type'} == 2) {
	# SSH 2 format line
	return join(" ", $_[0]->{'opts'} ? ( $_[0]->{'opts'} ) : ( ),
			 $_[0]->{'keytype'}, $_[0]->{'key'}, $_[0]->{'name'} );
	}
else {
	# SSH 1 format line
	return join(" ", $_[0]->{'opts'} ? ( $_[0]->{'opts'} ) : ( ),
			 $_[0]->{'bits'}, $_[0]->{'exp'}, $_[0]->{'key'}, $_[0]->{'name'} );
	}
}

# list_knowns()
# Returns a list of known host structures
sub list_knowns
{
local @rv;
local $lnum = 0;
open(KNOWNS, $known_hosts);
while(<KNOWNS>) {
	s/\r|\n//g;
	s/#.*$//;
	#Handle hashed type 2 keys
	if (/^\|1\|(\S+=)\|(\S+=)\s(.+)\s(\S+=)\s*(.*)$/) {
		local $known = { 'comment' => $5,
				 'key' => $4,
				 'salt' => $1,
				 'hash' => $2,
				 'type' => $3,
				 'hosts' => [ split(/,/, '*HASHED*') ],
				 'line' => $lnum,
				 'index' => scalar(@rv) };
		push(@rv, $known);
		}
	#Handle hashed type 1 keys
	elsif (/^\|1\|(\S+=)\|(\S+=)\s(\d+)\s(\d+)\s(\S+)\s*(.*)$/) {
		local $known = { 'comment' => $6,
				 'key' => $5,
				 'type' => 'ssh-rsa1',
				 'salt' => $1,
				 'hash' => $2,
				 'exp' => $4,
				 'bits' => $3,
				 'hosts' => [ split(/,/, '*HASHED*') ],
				 'line' => $lnum,
				 'index' => scalar(@rv) };
		push(@rv, $known);
		}
	#Handle type 2 keys
	elsif (/^(\S+)\s+(.+)\s(\S+=)\s*(.*)$/) {
		local $known = { 'comment' => $4,
				 'key' => $3,
				 'type' => $2,
				 'hosts' => [ split(/,/, $1) ],
				 'line' => $lnum,
				 'index' => scalar(@rv) };
		push(@rv, $known);
		}
	#Handle type 1 keys
	elsif (/^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s*(.*)$/) {
		local $known = { 'comment' => $5,
				 'key' => $4,
				 'type' => 'ssh-rsa1',
				 'exp' => $3,
				 'bits' => $2,
				 'hosts' => [ split(/,/, $1) ],
				 'line' => $lnum,
				 'index' => scalar(@rv) };
		push(@rv, $known);
		}
	$lnum++;
	}
close(KNOWNS);
return @rv;
}

# create_known(&known)
sub create_known
{
local $lref = &read_file_lines($known_hosts);
push(@$lref, &known_line($_[0]));
&flush_file_lines();
}

# delete_known(&known)
sub delete_known
{
local $lref = &read_file_lines($known_hosts);
splice(@$lref, $_[0]->{'line'}, 1);
&flush_file_lines();
}

# modify_known(&known)
sub modify_known
{
local $lref = &read_file_lines($known_hosts);
$lref->[$_[0]->{'line'}] = &known_line($_[0]);
&flush_file_lines();
}

sub known_line
{
if ($_[0]->{'type'} eq 'ssh-rsa1') {
	return join(" ", join(",", @{$_[0]->{'hosts'}}), $_[0]->{'bits'}, $_[0]->{'exp'},
			$_[0]->{'key'}, $_[0]->{'comment'} ? ( $_[0]->{'comment'} ) : ( ) );
	}
else {
	return join(" ", join(",", @{$_[0]->{'hosts'}}), $_[0]->{'type'},
			$_[0]->{'key'}, $_[0]->{'comment'} ? ( $_[0]->{'comment'} ) : ( ) );
}
}

# get_ssh_type()
# Returns either 'openssh' or 'ssh'
sub get_ssh_type
{
local $out = `ssh -V 2>&1 </dev/null`;
return $out =~ /openssh/i ? 'openssh' :
       $out =~ /Sun_SSH/i ? 'openssh' :
			    'ssh';
}

# get_ssh_version()
# Returns the SSH version number
sub get_ssh_version
{
local $out = `ssh -V 2>&1 </dev/null`;
if ($out =~ /(sshd\s+version\s+([0-9\.]+))/i ||
    $out =~ /(ssh\s+secure\s+shell\s+([0-9\.]+))/i) {
	# Classic commercial SSH
	return $2;
	}
elsif ($out =~ /(OpenSSH.([0-9\.]+))/i) {
	# OpenSSH .. assume all versions are supported
	return $2;
	}
elsif ($out =~ /(Sun_SSH_([0-9\.]+))/i) {
	# Solaris 9 SSH is actually OpenSSH 2.x
	return 2.0;
	}
elsif (($out = $config{'sshd_version'}) && ($out =~ /(Sun_SSH_([0-9\.]+))/i)) {
	# Probably Solaris 10 SSHD that didn't display version.  Use it.
	return 2.0;
	}
else {
	return undef;
	}
}

1;

