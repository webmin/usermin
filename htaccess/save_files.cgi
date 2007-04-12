#!/usr/local/bin/perl
# save_files.cgi
# Save some kind of per-files options

require './htaccess-lib.pl';
&ReadParse();
$hconf = &get_htaccess_config($in{'file'});
$d = $hconf->[$in{'idx'}];
$conf = $d->{'members'};
@edit = &editable_directives($in{'type'}, 'directory');

&error_setup(&text('efailed', $text{"type_$in{'type'}"}));
&parse_inputs(\@edit, $conf, $hconf);

&redirect("files_index.cgi?file=".&urlize($in{'file'})."&idx=$in{'idx'}");
