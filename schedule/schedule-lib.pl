# Functions for scheduled email notification

BEGIN { push(@INC, ".."); };
use WebminCore;
use Time::Local;
&init_config();

$cron_cmd = "$module_config_directory/email.pl";
$atmode_cmd = "$module_config_directory/atmode.pl";
if (!-x $cron_cmd && $< == 0) {
	&create_wrapper($cron_cmd, $module_name, "email.pl");
	}
if (!-x $atmode_cmd && $< == 0) {
	&create_wrapper($atmode_cmd, $module_name, "atmode.pl");
	}

&switch_to_remote_user();
&create_user_config_dirs();
&foreign_require("cron", "cron-lib.pl");
&foreign_require("mailbox", "mailbox-lib.pl");

$schedules_dir = "$user_module_config_directory/schedules";
$messages_dir = "$user_module_config_directory/messages";
$files_dir = "$user_module_config_directory/files";
$old_cron_cmd = "$user_module_config_directory/email.pl";
$old_atmode_cmd = "$user_module_config_directory/atmode.pl";

# list_schedules()
# Returns a list of all scheduled messages
sub list_schedules
{
local @rv;
opendir(DIR, $schedules_dir);
foreach $f (readdir(DIR)) {
	next if ($f eq "." || $f eq "..");
	local $sched = &get_schedule($f);
	push(@rv, $sched) if ($sched);
	}
closedir(DIR);
return @rv;
}

# get_schedule(id)
sub get_schedule
{
local $file = "$schedules_dir/$_[0]";
local %sched;
&read_file($file, \%sched);
$sched{'id'} = $_[0];
$sched{'file'} = $file;
$sched{'mfile'} = "$messages_dir/$_[0]";
open(MAIL, $sched{'mfile'});
while(<MAIL>) {
	$sched{'mail'} .= $_;
	}
close(MAIL);
return \%sched;
}

# save_schedule(&sched)
sub save_schedule
{
mkdir($schedules_dir, 0700) if (!-d $schedules_dir);
mkdir($messages_dir, 0700) if (!-d $messages_dir);
$_[0]->{'id'} ||= time().$$;
local $file = $_[0]->{'file'} || "$schedules_dir/$_[0]->{'id'}";
local %copy = %{$_[0]};
delete($copy{'mail'});
&write_file($file, \%copy);
local $mfile = $_[0]->{'mfile'} || "$messages_dir/$_[0]->{'id'}";
&open_tempfile(MAIL, ">$mfile");
&print_tempfile(MAIL, $_[0]->{'mail'});
&close_tempfile(MAIL);
}

# delete_schedule(&sched)
sub delete_schedule
{
unlink($_[0]->{'file'});
unlink($_[0]->{'mfile'});
system("rm -rf ".quotemeta("$files_dir/$_[0]->{'id'}"));
}

# list_schedule_files(&sched)
# Returns a list of files attached to a scheduled email
sub list_schedule_files
{
local ($sched) = @_;
return ( ) if (!$sched->{'id'});
local @rv;
opendir(DIR, "$files_dir/$sched->{'id'}");
foreach my $f (readdir(DIR)) {
	next if ($f eq "." || $f eq "..");
	local $path = "$files_dir/$sched->{'id'}/$f";
	if (-l $path) {
		# A server-side file
		push(@rv, { 'file' => readlink($path),
			    'id' => $f,
			    'type' => 0,
			    'size' => nice_size(recursive_disk_usage(resolve_links($path))) });
		}
	else {
		# An uploaded file
		push(@rv, { 'file' => $path,
			    'id' => $f,
			    'type' => 1,
			    'size' => nice_size(recursive_disk_usage($path)) });
		}
	}
closedir(DIR);
return sort { lc($a->{'id'}) cmp lc($b->{'id'}) } @rv;
}

# create_schedule_file(&sched, path|data, uploaded-filename)
# Adds a file to a scheduled email
sub create_schedule_file
{
local ($sched, $path, $uploaded) = @_;
mkdir($files_dir, 0700) if (!-d $files_dir);
mkdir("$files_dir/$sched->{'id'}", 0700) if (!-d "$files_dir/$sched->{'id'}");
if ($uploaded) {
	$uploaded =~ s/^(.*)[\/\\]//;
	&open_tempfile(FILE, ">$files_dir/$sched->{'id'}/$uploaded");
	&print_tempfile(FILE, $path);
	&close_tempfile(FILE);
	}
else {
	local $short = $path;
	$short =~ s/^(.*)[\/\\]//;
	symlink($path, "$files_dir/$sched->{'id'}/$short");
	}
}

# delete_schedule_file(&sched, &file)
sub delete_schedule_file
{
local ($sched, $file) = @_;
unlink("$files_dir/$sched->{'id'}/$file->{'id'}");
}

# find_cron_job(&sched)
# Finds the cron job for some scheduled email
sub find_cron_job
{
local @jobs = &cron::list_cron_jobs();
local ($job) = grep { $_->{'user'} eq $remote_user &&
		      ($_->{'command'} eq "$cron_cmd $_[0]->{'id'}" ||
		       $_->{'command'} eq "$old_cron_cmd $_[0]->{'id'}") } @jobs;
return $job;
}

# my_email_address([with-name])
sub my_email_address
{
local ($froms, $doms) = &mailbox::list_from_addresses();
if (@$froms) {
	local ($fp) = &mailbox::split_addresses($froms->[0]);
	if ($fp) {
		return $_[0] ? $fp->[2] : $fp->[0];
		}
	}
return $remote_user.'@'.&get_system_hostname();
}

# create_atmode_job()
# If any jobs exist that are scheduled at a specific time, create a cron job
# to check for them once per minute
sub create_atmode_job
{
local @ats = grep { $_->{'at'} } &list_schedules();
if (@ats) {
	local @jobs = &cron::list_cron_jobs();
	local ($badjob) = grep { $_->{'user'} eq $remote_user &&
				 $_->{'command'} eq $old_atmode_cmd } @jobs;
	if ($badjob) {
		&cron::delete_cron_job($badjob);
		}
	local ($job) = grep { $_->{'user'} eq $remote_user &&
			      $_->{'command'} eq $atmode_cmd } @jobs;
	if (!$job) {
		local @mins = map { $_*5 } (0 .. 11);
		$job = { 'command' => $atmode_cmd,
			 'user' => $remote_user,
			 'active' => 1,
			 'mins' => join(",", @mins),
			 'hours' => '*',
			 'days' => '*',
			 'months' => '*',
			 'weekdays' => '*' };
		&cron::create_cron_job($job);
		}
	}
}

# make_email(&schedule)
sub make_email
{
local ($sched) = @_;
local $myaddr = &my_email_address(1);
local $data = $sched->{'mail'};
if ($config{'attach'} && $sched->{'mailfile'}) {
	open(FILE, $sched->{'mailfile'});
	while(<FILE>) {
		$data .= $_;
		}
	close(FILE);
	}
local @attach;
foreach my $file (&list_schedule_files($sched)) {
	local $type = &guess_mime_type($file->{'id'},
				       "application/octet-stream").
		      "; name=\"$file->{'id'}\"";
	local $disp = "inline; filename=\"$file->{'id'}\"";
	push(@attach,
		{ 'headers' => [ [ 'Content-type', $type ],
				 [ 'Content-Disposition', $disp ],
				 [ 'Content-Transfer-Encoding', 'base64' ] ],
		  'data' => &read_file_contents($file->{'file'}) });
	}
return { 'headers' => [ [ 'From' => $sched->{'from'} || $myaddr ],
			[ 'To' => &mailbox::expand_to($sched->{'to'}) ||
				  $myaddr ],
			[ 'Cc' => &mailbox::expand_to($sched->{'cc'}) ],
			[ 'Bcc' => &mailbox::expand_to($sched->{'bcc'}) ],
			[ 'Subject' => $sched->{'subject'} ] ],
	  'attach' => [ { 'headers' => [ [ 'Content-type', ($sched->{'is_html'} ? 'text/html' : 'text/plain') ] ],
			  'data' => $data },
			@attach ]
	};
}

# create_wrapper(wrapper-path, module, script)
# Creates a wrapper script which calls a script in some module's directory
# with the proper webmin environment variables set. Copied from the cron module,
# so that it can be called before requireing cron-lib.pl
sub create_wrapper
{
local $perl_path = &get_perl_path();
&open_tempfile(CMD, ">$_[0]");
&print_tempfile(CMD, <<EOF
#!$perl_path
open(CONF, "$config_directory/miniserv.conf");
while(<CONF>) {
\$root = \$1 if (/^root=(.*)/);
}
close(CONF);
\$ENV{'WEBMIN_CONFIG'} = "$ENV{'WEBMIN_CONFIG'}";
\$ENV{'WEBMIN_VAR'} = "$ENV{'WEBMIN_VAR'}";
chdir("\$root/$_[1]");
exec("\$root/$_[1]/$_[2]", \@ARGV) || die "Failed to run \$root/$_[1]/$_[2] : \$!";
EOF
	);
&close_tempfile(CMD);
chmod(0755, $_[0]);
}

# next_run(&sched)
# Returns the unix time at which the given scheduled email will next be sent
sub next_run
{
local ($sched) = @_;
if ($sched->{'at'}) {
	return $sched->{'at'};
	}
else {
	local $now = time();
	local @tm = localtime($now);

	local @mins = &cron_all_ranges($sched->{'mins'}, 0, 59);
	local @hours = &cron_all_ranges($sched->{'hours'}, 0, 23);
	local @days = &cron_all_ranges($sched->{'days'}, 1, 31);
	local @months = &cron_all_ranges($sched->{'months'}, 1, 12);
	local @weekdays = &cron_all_ranges($sched->{'weekdays'}, 0, 6);
	local ($min, $hour, $day, $month, $year);
	local @possible;
	foreach $min (@mins) {
		foreach $hour (@hours) {
			foreach $day (@days) {
				foreach $month (@months) {
					foreach $year ($tm[5] .. $tm[5]+7) {
						local $tt;
						eval { $tt = timelocal(0, $min, $hour, $day, $month-1, $year) };
						next if ($tt < $now);
						local @ttm = localtime($tt);
						next if (&indexof($ttm[6], @weekdays) < 0);
						push(@possible, $tt);
						last;
						}
					}
				}
			}
		}
	@possible = sort { $a <=> $b } @possible;
	return $possible[0];
	}
}

# cron_first(list, min, max, current)
# Returns the lowest value from expanding a cron range >= current
sub cron_first
{
local @r = &cron_range($_[0], $_[1], $_[2]);
local $r;
foreach $r (sort { $a <=> $b } @r) {
	if ($r >= $_[3]) {
		return $r;
		}
	}
return undef;
}

# cron_range(range, min, max)
sub cron_range
{
local ($w, $min, $max) = @_;
local $j;
local %inuse;
if ($w eq "*") {
	# all values
	for($j=$min; $j<=$max; $j++) { $inuse{$j}++; }
	}
elsif ($w =~ /^\*\/(\d+)$/) {
	# only every Nth
	for($j=$min; $j<=$max; $j+=$1) { $inuse{$j}++; }
	}
elsif ($w =~ /^(\d+)-(\d+)\/(\d+)$/) {
	# only every Nth of some range
	for($j=$1; $j<=$2; $j+=$3) { $inuse{int($j)}++; }
	}
elsif ($w =~ /^(\d+)-(\d+)$/) {
	# all of some range
	for($j=$1; $j<=$2; $j++) { $inuse{int($j)}++; }
	}
else {
	# One value
	$inuse{int($w)}++;
	}
return sort { $a <=> $b } (keys %inuse);
}

# cron_all_ranges(comma-list, min, max)
sub cron_all_ranges
{
local @rv;
foreach $r (split(/,/, $_[0])) {
	push(@rv, &cron_range($r, $_[1], $_[2]));
	}
return sort { $a <=> $b } @rv;
}



1;

