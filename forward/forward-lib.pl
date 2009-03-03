# forward-lib.pl
# Common functions for editing .forward

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
do 'autoreply-file-lib.pl';

# Copy scripts to /etc/usermin and set up smrsh if needed while we still can
# (before a user switch)
foreach $script ("autoreply.pl", "filter.pl") {
	local $rpath = "$module_root_directory/$script";
	local $cpath = "$module_config_directory/$script";
	local @rst = stat($rpath);
	local @cst = stat($cpath);
	if (!@cst || $cst[7] != $rst[7]) {
		&copy_source_dest($rpath, $cpath);
		&set_ownership_permissions(undef, undef, 0755, $cpath);
		}
	if ($config{'smrsh_dir'} && !-r "$config{'smrsh_dir'}/$script") {
		symlink($cpath, "$config{'smrsh_dir'}/$script");
		}
	}

# If vacation is installed, link it from /etc/smrsh too
$vacation_path = &has_command("vacation");
if ($vacation_path) {
	if ($config{'smrsh_dir'} && !-r "$config{'smrsh_dir'}/vacation") {
		symlink($vacation_path, "$config{'smrsh_dir'}/vacation");
		}
	}

&switch_to_remote_user();
&create_user_config_dirs();

$forward_file = "$remote_user_info[7]/.forward";
&foreign_require("mailbox", "mailbox-lib.pl");
$mail_path = &mailbox::mailbox_file();

# list_aliases()
# Returns an array of data structures, each containing information about
# one sendmail alias from .forward
sub list_aliases
{
local($lnum, @rv, $file, $lalias);
$lnum = 0;
open(AFILE, $forward_file);
while(<AFILE>) {
	s/\r|\n//g;	# remove newlines
	if (/^(#*)\s*(.*)$/) {
		local(%alias, @values, $v);
		$alias{'eline'} = $alias{'line'} = $lnum;
		$alias{'file'} = $forward_file;
		$alias{'enabled'} = $1 ? 0 : 1;
		$v = $alias{'value'} = $2;
		while($v =~ /^\s*,?\s*()"([^"]+)"(.*)$/ ||
		      $v =~ /^\s*,?\s*(\|)"([^"]+)"(.*)$/ ||
		      $v =~ /^\s*,?\s*()([^,\s]+)(.*)$/) {
			push(@values, $1.$2); $v = $3;
			}
		$alias{'values'} = \@values;
		$alias{'num'} = scalar(@rv);
		if (&indexof($alias{'name'}, @skip) < 0) {
			push(@rv, \%alias);
			$lalias = \%alias;
			}
		}
	elsif (/^(#*)\s+(\S.*)$/ && $lalias &&
	       ($1 && !$lalias->{'enabled'} ||
		!$1 && $lalias->{'enabled'})) {
		# continuation of last alias
		$lalias->{'eline'} = $lnum;
		local $v = $2;
		$lalias->{'value'} .= $v;
		while($v =~ /^\s*,?\s*()"([^"]+)"(.*)$/ ||
		      $v =~ /^\s*,?\s*(\|)"([^"]+)"(.*)$/ ||
		      $v =~ /^\s*,?\s*()([^,\s]+)(.*)$/) {
			push(@{$lalias->{'values'}}, $1.$2); $v = $3;
			}
		}
	else { $lalias = undef; }
	$lnum++;
	}
close(AFILE);
return @rv;
}

# alias_form([alias])
# Display a form for editing or creating an alias. Each alias can map to
# 1 or more programs, files, lists or users
sub alias_form
{
local($a, @values, $v, $type, $val, @typenames);

$a = $_[1];
if ($a) { @values = @{$a->{'values'}}; }
@typenames = map { $text{"aform_type$_"} } (0 .. 8);
$typenames[0] = "&lt;$typenames[0]&gt;";

my @js; for($i=0; $i<=@values; $i++) {
	($type, $val) = $values[$i] ? &alias_type($values[$i]) : (0, "");
	push @js,"document.forms[0].val_$i.disabled=".(($type==0||$type==7||$type==8)?"true":"false")
	}

&ui_print_header(undef, $_[0],"", undef, undef, undef, undef, undef,undef, "onload=\"".join(";",@js)."\"");
print "<form method=post action=save_alias.cgi name=edit_aliases>\n";
if ($a) {
	print "<input type=hidden name=num value='$a->{'num'}'>\n";
	print "<input type=hidden name=file value='$a->{'file'}'>\n";
	}
else { print "<input type=hidden name=new value=1>\n"; }
print "<table border>\n";
print "<tr $tb> <td><b>",$a ? $text{'aform_edit'}
			    : $text{'aform_create'},"</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";
if ($config{'mail_system'} == 0) {
	print "<tr> <td><b>$text{'aform_enabled'}</b></td>\n";
	printf "<td><input type=radio name=enabled value=1 %s> $text{'yes'}\n",
		!$a || $a->{'enabled'} ? "checked" : "";
	printf "<input type=radio name=enabled value=0 %s> $text{'no'}</td></tr>\n",
		!$a || $a->{'enabled'} ? "" : "checked";
	}
else {
	print "<tr> <td><b>$text{'aform_name'}</b></td>\n";
	printf "<td><input type=radio name=name_def value=1 %s> <tt>%s</tt>\n",
		$a->{'name'} ? '' : 'checked', $remote_user;
	print "&nbsp;" x 3;
	printf "<input type=radio name=name_def value=0 %s> <tt>%s-</tt>",
		$a->{'name'} ? 'checked' : '', $remote_user;
	printf "<input name=name size=20 value='%s'></td> </tr>\n",
		$a->{'name'};
	}

local %types = map { $_, 1 } split(/\,/, $config{'types'});
$types{8} = $types{5};
for($i=0; $i<=@values; $i++) {
	($type, $val) = $values[$i] ? &alias_type($values[$i]) : (0, "");
	print "<tr> <td valign=top><b>$text{'aform_val'}</b></td>\n";
	print "<td><select name=type_$i onchange=\"".
		"document.forms[0].val_$i.disabled=(this.value=='0'||this.value=='7'||this.value=='8');\">\n";
	for($j=0; $j<@typenames; $j++) {
		next if ($j == 2 && $config{'mail_system'} == 1);
		next if ($j == 7 && $config{'mail_system'} == 1 && !$mail_path);
		next if ($j == 8 && !$vacation_path);
		next if ($j && !$types{$j});
		printf "<option value=$j %s>$typenames[$j]\n",
			$type == $j ? "selected" : "";
		}
	print "</select>\n";
	print "<input name=val_$i size=30 value=\"$val\">\n";
	local $lnk = $config{'mail_system'} == 1 ? "file=$a->{'file'}"
						 : "num=$a->{'num'}";
	if ($type == 2 && $a) {
		print "<a href='edit_afile.cgi?$lnk&vfile=$val'>",
		      "$text{'aform_afile'}</a>\n";
		}
	elsif ($type == 5 && $a) {
		print "<a href='edit_rfile.cgi?$lnk&vfile=$val'>",
		      "$text{'aform_afile'}</a>\n";
		}
	elsif ($type == 6 && $a) {
		print "<a href='edit_ffile.cgi?$lnk&vfile=$val'>",
		      "$text{'aform_afile'}</a>\n";
		}
	elsif ($type == 8 && $a) {
		print "<a href='edit_vacation.cgi?$lnk&idx=$i'>$text{'aform_vacation'}</a>\n";
		}
	print "</td></tr>\n";
	}
print "<tr> <td colspan=2 align=right>\n";
if ($a) {
	print "<input type=submit value=$text{'save'}>\n";
	print "<input type=submit name=delete value=$text{'delete'}>\n";
	}
else { print "<input type=submit value=$text{'create'}>\n"; }
print "</td> </tr>\n";
print "</table></td></tr></table></form>\n";
&ui_print_footer("index.cgi?simple=0", $text{'index_return'});
}

# create_alias(&details)
# Create a new alias
sub create_alias
{
if ($config{'mail_system'} == 0) {
	&open_tempfile(AFILE, ">>$forward_file");
	&print_tempfile(AFILE, $_[0]->{'enabled'} ? "" : "# ",
	    join(',', map { /\s/ ? "\"$_\"" : $_ } @{$_[0]->{'values'}}),"\n");
	&close_tempfile(AFILE);
	&set_forward_perms();
	}
else {
	&open_tempfile(AFILE, ">$remote_user_info[7]/".
		($_[0]->{'name'} ? ".qmail-$_[0]->{'name'}" : ".qmail"));
	foreach $v (@{$_[0]->{'values'}}) {
		&print_tempfile(AFILE, $v,"\n");
		}
	&close_tempfile(AFILE);
	}
}

# delete_alias(&details)
sub delete_alias
{
if ($config{'mail_system'} == 0) {
	local $lref = &read_file_lines($_[0]->{'file'});
	local $len = $_[0]->{'eline'} - $_[0]->{'line'} + 1;
	splice(@$lref, $_[0]->{'line'}, $len);
	&flush_file_lines();
	}
else {
	unlink("$remote_user_info[7]/$_[0]->{'file'}");
	}
}

# modify_alias(&old, &details)
# Update some existing alias
sub modify_alias
{
if ($config{'mail_system'} == 0) {
	local $str = ($_[1]->{'enabled'} ? "" : "# ") .
		     join(',', map { /\s/ ? "\"$_\"" : $_ } @{$_[1]->{'values'}});
	local $lref = &read_file_lines($_[0]->{'file'});
	local $len = $_[0]->{'eline'} - $_[0]->{'line'} + 1;
	splice(@$lref, $_[0]->{'line'}, $len, $str);
	&flush_file_lines();
	}
else {
	&delete_alias($_[0]);
	&create_alias($_[1]);
	}
}

# alias_type(string)
# Return the type and destination of some alias string
sub alias_type
{
local @rv;
if ($_[0] =~ /^\|($user_module_config_directory|$module_config_directory)\/autoreply.pl\s+(\S+)/) {
	@rv = (5, $2);
	}
elsif ($_[0] =~ /^\|($user_module_config_directory|$module_config_directory)\/filter.pl\s+(\S+)/) {
	@rv = (6, $2);
	}
elsif ($vacation_path && $_[0] =~ /^\|$vacation_path\s*(.*)/) {
	@rv = (8, $1);
	}
elsif ($_[0] =~ /^\|(.*)$/) {
	@rv = (4, $1);
	}
elsif ($_[0] eq $mail_path) {
	@rv = (7, undef);
	}
elsif ($_[0] =~ /^(\..*)$/ && $config{'mail_system'} == 1) {
	@rv = (3, $1);
	}
elsif ($_[0] =~ /^(\/.*)$/) {
	@rv = (3, $1);
	}
elsif ($_[0] =~ /^:include:(.*)$/ && $config{'mail_system'} == 0) {
	@rv = (2, $1);
	}
elsif ($_[0] =~ /^\\($remote_user)$/ && $config{'mail_system'} == 0) {
	@rv = (7, undef);
	}
elsif ($remote_user =~ /^(\S+)\@(\S+)$/ &&
       $_[0] eq "\\$1-$2" && $config{'mail_system'} == 0) {
	# Virtualmin created user for Postfix when username contains @
	@rv = (7, undef);
	}
elsif ($_[0] =~ /^&(.*)$/) {
	@rv = (1, $1);
	}
else {
	@rv = (1, $_[0]);
	}
return wantarray ? @rv : $rv[0];
}

# list_dotqmails()
# Returns a list of .qmail* files in the user's home directory
sub list_dotqmails
{
local @rv;
opendir(DIR, $remote_user_info[7]);
while($f = readdir(DIR)) {
	next if ($f !~ /^\.qmail(-(\S+))?$/);
	push(@rv, &get_dotqmail($f));
	}
closedir(DIR);
return @rv;
}

sub get_dotqmail
{
$_[0] =~ /^\.qmail(-(\S+))?$/;
local $alias = { 'file' => $_[0],
		 'name' => $2 };
open(AFILE, "$remote_user_info[7]/$_[0]");
while(<AFILE>) {
	s/\r|\n//g;
	s/#.*$//g;
	if (/\S/) {
		push(@{$alias->{'values'}}, $_);
		}
	}
close(AFILE);
return $alias;
}

sub set_forward_perms
{
chmod(0644, $forward_file);
}

sub make_absolute
{
if ($_[0] =~ /^\//) {
	return $_[0];
	}
else {
	return "$remote_user_info[7]/$_[0]";
	}
}

sub make_relative
{
if ($_[0] =~ /^\Q$remote_user_info[7]\/\E(.*)$/) {
	return $1;
	}
else {
	return $_[0];
	}
}

# get_simple()
# If the current forwarding rules are simple (local delivery, autoreply
# and forwarding only), return a hash ref containing the settings. Otherwise,
# return undef.
sub get_simple
{
local @aliases = &list_aliases();
local $simple;
foreach my $a (@aliases) {
	foreach my $v (@{$a->{'values'}}) {
		local ($atype, $aval) = &alias_type($v);
		if ($atype == 1) {
			# Forward to an address
			return undef if ($simple->{'forward'});
			$simple->{'forward'} = $aval;
			}
		elsif ($atype == 7) {
			# Local delivery
			$simple->{'local'} = 1;
			}
		elsif ($atype == 5) {
			# Usermin autoreply program
			return undef if ($simple->{'autoreply'});
			$simple->{'autoreply'} = &make_absolute($aval);
			$simple->{'auto'} = 1;
			&read_autoreply($simple->{'autoreply'}, $simple);
			}
		else {
			# Some un-supported rule
			return undef;
			}
		}
	}
$simple ||= { 'local' => 1 };	# if no settings, assume local delivery
if (!$simple->{'autoreply'}) {
	# Get autoreply message from default file
	$simple->{'autoreply'} = &make_absolute("autoreply.txt");
	&read_autoreply($simple->{'autoreply'}, $simple);
	}
return $simple;
}

# save_simple(&simple)
# Creates a .forward file with the given simple settings
sub save_simple
{
local ($simple) = @_;
if ($simple->{'local'} && !$simple->{'forward'} && !$simple->{'auto'}) {
	# If doing only local delivery, just remove .forward
	&unlink_file($forward_file);
	}
else {
	# Need to create .forward
	&open_tempfile(FORWARD, ">$forward_file");
	if ($simple->{'local'}) {
		if ($remote_user =~ /^(\S+)\@(\S+)$/ &&
		    defined(getpwnam("$1-$2"))) {
			# Handle users created by Virtualmin for Postfix
			# with @ in names
			&print_tempfile(FORWARD, "\\$1-$2\n");
			}
		else {
			&print_tempfile(FORWARD, "\\$remote_user\n");
			}
		}
	if ($simple->{'forward'}) {
		&print_tempfile(FORWARD, $simple->{'forward'},"\n");
		}
	if ($simple->{'auto'}) {
		local $afile = $simple->{'autoreply'};
		&print_tempfile(FORWARD, "\"|$module_config_directory/autoreply.pl $afile $remote_user\"\n");
		}
	&close_tempfile(FORWARD);
	&set_forward_perms();
	}

if ($simple->{'autotext'}) {
	# Save autoreply text
	if (!$simple->{'autoreply'}) {
		# Create autoreply file
		$simple->{'autoreply'} =
			"$remote_user_info[7]/autoreply.txt";
		}
	&write_autoreply($simple->{'autoreply'}, $simple);
	}
}

1;

