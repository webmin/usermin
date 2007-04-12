# proc-lib.pl
# Functions for managing processes

do '../web-lib.pl';
&init_config();
if (!$ENV{'FOREIGN_MODULE_NAME'}) {
	&switch_to_remote_user();
	&create_user_config_dirs();
	}
do "$config{ps_style}-lib.pl";
use POSIX;

%access = ( 'edit' => 1,
	    'run' => 1 );

$no_module_config = 1;
$user_processes_only = 1;

sub process_info
{
local @plist = &list_processes($_[0]);
return @plist ? %{$plist[0]} : ();
}

# index_links(current)
sub index_links
{
local(%linkname, $l);
print "<b>$text{'index_display'} : </b>&nbsp;&nbsp;\n";
foreach $l ("tree", "user", "size", "cpu", "search", "run") {
	if ($l ne $_[0]) { print "<a href=index_$l.cgi>"; }
	else { print "<b>"; }
	print $text{"index_$l"};
	if ($l ne $_[0]) { print "</a>"; }
	else { print "</b>"; }
	print "&nbsp;\n";
	}
print "<p>\n";
open(INDEX, "> $user_module_config_directory/index");
$0 =~ /([^\/]+)$/;
print INDEX "$1?$in\n";
close(INDEX);
}

# cut_string(string, [length])
sub cut_string
{
local $len = $_[1] || $config{'cut_length'};
if ($len && length($_[0]) > $len) {
	return substr($_[0], 0, $len)." ...";
	}
return $_[0];
}

# switch_acl_uid()
sub switch_acl_uid
{
}

# safe_process_exec(command, uid, gid, handle, input, fixtags, bsmode)
# Executes the given command as the given user/group and writes all output
# to the given file handle. Finishes when there is no more output or the
# process stops running. Returns the number of bytes read.
sub safe_process_exec
{
# setup pipes and fork the process
local $chld = $SIG{'CHLD'};
$SIG{'CHLD'} = \&safe_exec_reaper;
pipe(OUTr, OUTw);
pipe(INr, INw);
local $pid = fork();
if (!$pid) {
	#setsid();
	untie(*STDIN);
	untie(*STDOUT);
	untie(*STDERR);
	open(STDIN, "<&INr");
	open(STDOUT, ">&OUTw");
	open(STDERR, ">&OUTw");
	$| = 1;
	close(OUTr); close(INw);

	if ($_[1]) {
		if (defined($_[2])) {
			# switch to given UID and GID
			$( = $_[2]; $) = "$_[2] $_[2]";
			$< = $> = $_[1];
			}
		else {
			# switch to UID and all GIDs
			local @u = getpwuid($_[1]);
			$( = $u[3];
			$) = "$u[3] ".join(" ", $u[3], &other_groups($u[0]));
			$< = $> = $u[2];
			}
		}

	# run the command
	delete($ENV{'FOREIGN_MODULE_NAME'});
	delete($ENV{'SCRIPT_NAME'});
	exec("/bin/sh", "-c", $_[0]);
	print "Exec failed : $!\n";
	exit 1;
	}
close(OUTw); close(INr);

# Feed input (if any)
print INw $_[4];
close(INw);

# Read and show output
local $fn = fileno(OUTr);
local $got = 0;
local $out = $_[3];
local $line;
while(1) {
	local ($rmask, $buf);
	vec($rmask, $fn, 1) = 1;
	local $sel = select($rmask, undef, undef, 1);
	if ($sel > 0 && vec($rmask, $fn, 1)) {
		# got something to read.. print it
		sysread(OUTr, $buf, 1024) || last;
		$got += length($buf);
		if ($_[5]) {
			$buf =~ s/&/&amp;/g;
			$buf =~ s/</&lt;/g;
			$buf =~ s/>/&gt;/g;
			}
		if ($_[6]) {
			# Convert backspaces and returns
			$line .= $buf;
			while($line =~ s/^([^\n]*\n)//) {
				local $one = $1;
				while($one =~ s/.\010//) { }
				print $out $one;
				}
			}
		else {
			print $out $buf;
			}
		}
	elsif ($sel == 0) {
		# nothing to read. maybe the process is done, and a subprocess
		# is hanging things up
		last if (!kill(0, $pid));
		}
	}
close(OUTr);
print $out $line;
$SIG{'CHLD'} = $chld;
return $got;
}

# safe_process_exec_logged(..)
# Like safe_process_exec, but also logs the command
sub safe_process_exec_logged
{
&additional_log('exec', undef, $_[0]);
return &safe_process_exec(@_);
}

sub safe_exec_reaper
{
local $xp;
do {    local $oldexit = $?;
	$xp = waitpid(-1, WNOHANG);
	$? = $oldexit if ($? < 0);
	} while($xp > 0);
}

# pty_process_exec(command, [uid, gid])
# Starts the given command in a new pty and returns the pty filehandle and PID
sub pty_process_exec
{
local ($ptyfh, $ttyfh, $pty, $tty) = &get_new_pty();
local $pid = fork();
if (!$pid) {
	close(STDIN); close(STDOUT); close(STDERR);
	untie(*STDIN); untie(*STDOUT); untie(*STDERR);
	setsid();
	#setpgrp(0, $$);
	if ($_[1]) {
		$( = $u[3]; $) = "$_[2] $_[2]";
		($>, $<) = ($_[1], $_[1]);
		}
	open(STDIN, "<$tty");
	open(STDOUT, ">&$ttyfh");
	open(STDERR, ">&STDOUT");
	close($ptyfh);
	exec($_[0]);
	print "Exec failed : $!\n";
	exit 1;
	}
close($ttyfh);
return ($ptyfh, $pid);
}

# pty_process_exec_logged(..)
# Like pty_process_exec, but logs the command as well
sub pty_process_exec_logged
{
&additional_log('exec', undef, $_[0]);
return &pty_process_exec(@_);
}

# find_process(name)
# Returns an array of all processes matching some name
sub find_process
{
local $name = $_[0];
local @rv = grep { $_->{'args'} =~ /$name/ } &list_processes();
return wantarray ? @rv : $rv[0];
}

$has_lsof_command = &has_command("lsof");

# find_socket_processes(protocol, port)
# Returns all processes using some port and protocol
sub find_socket_processes
{
local @rv;
open(LSOF, "lsof -i '$_[0]:$_[1]' |");
while(<LSOF>) {
	if (/^(\S+)\s+(\d+)/) {
		push(@rv, $2);
		}
	}
close(LSOF);
return @rv;
}

# find_process_sockets(pid)
# Returns all network connections made by some process
sub find_process_sockets
{
local @rv;
open(LSOF, "lsof -i tcp -i udp -n |");
while(<LSOF>) {
	if (/^(\S+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*(TCP|UDP)\s+(.*)/
	    && $2 eq $_[0]) {
		local $n = { 'fd' => $4,
			     'type' => $5,
			     'proto' => $7 };
		local $m = $8;
		if ($m =~ /^([^:\s]+):([^:\s]+)\s+\(listen\)/i) {
			$n->{'lhost'} = $1;
			$n->{'lport'} = $2;
			$n->{'listen'} = 1;
			}
		elsif ($m =~ /^([^:\s]+):([^:\s]+)->([^:\s]+):([^:\s]+)\s+\((\S+)\)/) {
			$n->{'lhost'} = $1;
			$n->{'lport'} = $2;
			$n->{'rhost'} = $3;
			$n->{'rport'} = $4;
			$n->{'state'} = $5;
			}
		elsif ($m =~ /^([^:\s]+):([^:\s]+)/) {
			$n->{'lhost'} = $1;
			$n->{'lport'} = $2;
			}
		push(@rv, $n);
		}
	}
close(LSOF);
return @rv;
}

# find_process_files(pid)
# Returns all files currently held open by some process
sub find_process_files
{
local @rv;
open(LSOF, "lsof -p '$_[0]' |");
while(<LSOF>) {
	if (/^(\S+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+),(\d+)\s+(\d+)\s+(\d+)\s+(.*)/) {
		push(@rv, { 'fd' => lc($4),
			    'type' => lc($5),
			    'device' => [ $6, $7 ],
			    'size' => $8,
			    'inode' => $9,
			    'file' => $10 });
		}
	}
close(LSOF);
return @rv;
}



1;

