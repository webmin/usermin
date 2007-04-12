#!/usr/local/bin/perl
# manual.cgi
# Display a text box for manually editing directives

require './htaccess-lib.pl';
&ReadParse();
if (defined($in{'idx'})) {
	# files within .htaccess file
	$hconf = &get_htaccess_config($in{'file'});
	$d = $hconf->[$in{'idx'}];
	$file = $in{'file'};
	$start = $d->{'line'}+1; $end = $d->{'eline'}-1;
	$title = &text('htfile_header', &dir_name($d),
		       "<tt>$in{'file'}</tt>");
	$return = "htaccess_index.cgi"; $rmsg = $text{'htindex_return'};
	}
else {
	# .htaccess file
	$file = $in{'file'};
	$title = &text('htindex_header', "<tt>$in{'file'}</tt>");
	$return = "htaccess_index.cgi"; $rmsg = $text{'htindex_return'};
	$dir = "files_index.cgi";
	}
&ui_print_header($title, $text{'manual_title'}, "");

print &text('manual_header', "<tt>$file</tt>"),"<p>\n";
print "<form action=manual_save.cgi method=post enctype=multipart/form-data>\n";
foreach $h ('virt', 'idx', 'file') {
	if (defined($in{$h})) {
		print "<input type=hidden name=$h value='$in{$h}'>\n";
		push(@args, "$h=$in{$h}");
		}
	}
$args = join('&', @args);

print "<textarea rows=15 cols=80 name=directives>\n";
$lref = &read_file_lines($file);
if (!defined($start)) {
	$start = 0;
	$end = @$lref - 1;
	}
for($i=$start; $i<=$end; $i++) {
	print &html_escape($lref->[$i]),"\n";
	}
print "</textarea><br><input type=submit value=\"$text{'save'}\"></form>\n";

&ui_print_footer("$return?$args", $rmsg);

# print_directives(&list, indent)
sub print_directives
{
foreach $c (@{$_[0]}) {
	next if ($c->{'name'} eq 'dummy');
	if ($c->{'type'}) {
		print $_[1],"<",$c->{'name'}," ",$c->{'value'},">\n";
		&print_directives($c->{'members'}, $_[1].' ');
		print $_[1],"</",$c->{'name'},">\n";
		}
	else {
		print $_[1],$c->{'name'}," ",$c->{'value'},"\n";
		}
	}
}

