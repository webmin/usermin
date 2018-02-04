#!/usr/local/bin/perl
# index.cgi
# Display mail forwarding from .forward file

require './forward-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);
&ReadParse();

if ($config{'mail_system'} == 0) {
	# See if we can use or offer simple mode
	$simple = &get_simple();
	}
if ($simple) {
	# Possible .. show selector
	$in{'simple'} = 1 if (!defined($in{'simple'}));
	print $text{'index_mode'},"\n";
	foreach $s (1, 0) {
		if ($s == $in{'simple'}) {
			print "<span data-unckecked>" . $text{'index_simple'.$s},"</span>\n";
			}
		else {
			print "<a href='index.cgi?simple=$s'>",$text{'index_simple'.$s},"</a>\n";
			}
		print "&nbsp;|&nbsp;\n" if ($s != 0);
		}
	print "<p>\n";
	}

if ($in{'simple'} && $simple) {
	# Simple mode for Sendmail
	print &ui_form_start("save_simple.cgi", "post");
	print &ui_table_start($text{'index_header'}, undef, 2);

	print &ui_table_row($text{'index_local'},
			    &ui_checkbox("local", 1, $text{'index_localyes'},
					 $simple->{'local'}));

	print &ui_table_row($text{'index_forward'},
			    &ui_checkbox("forward", 1,$text{'index_forwardyes'},
					 $simple->{'forward'})." ".
			    &ui_textbox("forwardto", $simple->{'forward'} ||
					     $userconfig{'forwardto'}, 50));

	# Autoreply active and text
	print &ui_table_row($text{'index_auto'},
			    &ui_checkbox("auto", 1,$text{'index_autoyes'},
					 $simple->{'auto'})."<br>\n".
			    &ui_textarea("autotext", $simple->{'autotext'},
					 5, 70));

	# Attached files
	if ($config{'attach'}) {
		$ftable = "";
		$i = 0;
		foreach $f (@{$simple->{'autoreply_file'}}, undef) {
			$ftable .= &ui_textbox("file_$i", $f, 50)." ".
				   &file_chooser_button("file_$i")."<br>\n";
			$i++;
			}
		print &ui_table_row($text{'index_files'}, $ftable);
		}

	$period = $simple->{'replies'} && $simple->{'period'} ?
			int($simple->{'period'}/60) :
		  $simple->{'replies'} ? 60 : undef;
	print &ui_table_row($text{'index_period'},
	    &ui_opt_textbox("period", $period, 3, $text{'index_noperiod'})." ".
	    $text{'index_mins'});

	$df = &mailbox::get_preferred_from_address();
	$mode = $simple->{'from'} eq $df || !$simple->{'autotext'} ? 2 :
		$simple->{'from'} ? 0 : 1,
	print &ui_table_row($text{'index_from'},
		&ui_radio("from_def", $mode,
			  [ [ 1, $text{'index_fromauto'} ],
			    [ 2, $text{'index_fromdef'} ],
			    [ 0, $text{'index_fromaddr'}." ".
				 &ui_textbox("from", $simple->{'from'} || $df,
					     50) ] ]));

	# Character set
	$cs = $simple ? $simple->{'charset'} :
	      &get_charset() eq $default_charset ? undef : &get_charset();
	$csmode = $cs eq &get_charset() ? 2 :
		  $cs ? 0 : 1;
	print &ui_table_row($text{'index_charset'},
		&ui_radio("charset_def", $csmode,
			  [ [ 1, $text{'default'}." ($default_charset)" ],
			    &get_charset() eq $default_charset ? ( ) :
				( [ 2, $text{'index_charsetdef'}.
				       " (".&get_charset().")" ] ),
			    [ 0, $text{'index_charsetother'} ] ])." ".
		&ui_textbox("charset", $csmode == 0 ? $cs : "", 20));
	
	print &ui_table_end();
	print &ui_form_end([ [ "save", $text{'save'} ] ]);
	}
elsif ($config{'mail_system'} == 0) {
	# Sendmail forwarding
	print "$text{'index_desc'}<p>\n";
	@aliases = &list_aliases();
	if (@aliases) {
		# find a good place to split
		$lines = 0;
		for($i=0; $i<@aliases; $i++) {
			$aline[$i] = $lines;
			$al = scalar(@{$aliases[$i]->{'values'}});
			$lines += ($al ? $al : 1);
			}
		$midline = int(($lines+1) / 2);
		for($mid=0; $mid<@aliases && $aline[$mid] < $midline; $mid++) { }

		# render tables
		print "<table width=100%> <tr><td width=50% valign=top>\n";
		&aliases_table(@aliases[0..$mid-1]);
		print "</td><td width=50% valign=top>\n";
		if ($mid < @aliases) { &aliases_table(@aliases[$mid..$#aliases]); }
		print "</td></tr> </table>\n";
		}
	else {
		print "<b>$text{'index_none'}</b> <p>\n";
		}
	}
else {
	# Qmail forwarding
	print "$text{'index_desc'}<p>\n";
	@aliases = &list_dotqmails();
	if (@aliases) {
		# find a good place to split
		$lines = 0;
		for($i=0; $i<@aliases; $i++) {
			$aline[$i] = $lines;
			$al = scalar(@{$aliases[$i]->{'values'}});
			$lines += ($al ? $al : 1);
			}
		$midline = int(($lines+1) / 2);
		for($mid=0; $mid<@aliases && $aline[$mid] < $midline; $mid++) { }

		# render tables
		print "<table width=100%> <tr><td width=50% valign=top>\n";
		&dotqmail_table(@aliases[0..$mid-1]);
		print "</td> <td>&nbsp;</td> <td width=50% valign=top>\n";
		if ($mid < @aliases) { &dotqmail_table(@aliases[$mid..$#aliases]); }
		print "</td></tr> </table>\n";
		}
	else {
		print "<b>$text{'index_none'}</b> <p>\n";
		}
	}

if (!$in{'simple'} || !$simple) {
	@links = ( "<a href='edit_alias.cgi?new=1'>$text{'index_add'}</a>" );
	if ($config{'mail_system'} == 0 && $config{'edit'}) {
		push(@links, "<a href='edit_forward.cgi'>".
		      	     &text('index_edit', "<tt>.forward</tt>")."</a>");
		}
	print &ui_links_row(\@links);
	}

&ui_print_footer("/", $text{'index'});

sub aliases_table
{
print &ui_columns_start([ $text{'aliases_to'},
			  $text{'aliases_enabled'} ], 100, 2);
foreach my $a (@_) {
	my @cols;
	my $e = "<a href=\"edit_alias.cgi?num=$a->{'num'}\">";
	foreach $v (@{$a->{'values'}}) {
		($anum, $astr) = &alias_type($v);
		$e .= &text("aliases_type$anum", "<tt>$astr</tt>")."<br>\n";
		}
	$e .= "</a>";
	push(@cols, $e);
	push(@cols, $a->{'enabled'} ? $text{'yes'} :
                	"<font color=#ff0000>$text{'no'}</font>");
	print &ui_columns_row(\@cols);
	}
print &ui_columns_end();
}

sub dotqmail_table
{
print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'aliases_from'}</b></td> <td><b>$text{'aliases_to'}</b></td> </tr>\n";
foreach $a (@_) {
	print "<tr $cb>\n";
	print "<td><a href=\"edit_alias.cgi?file=$a->{'file'}\">",
	      $a->{'name'} ? "$remote_user-$a->{'name'}" : $remote_user,
	      "</td> <td>\n";
	foreach $v (@{$a->{'values'}}) {
		($anum, $astr) = &alias_type($v);
		print &text("aliases_type$anum", "<tt>$astr</tt>"),"<br>\n";
		}
	print "</td> </tr>\n";
	}
print "</table>\n";

}

