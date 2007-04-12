#!/usr/local/bin/perl
# save_htaccess.cgi
# Save some kind of per-directory options file

require './htaccess-lib.pl';
&ReadParse();
$conf = &get_htaccess_config($in{'file'});
@edit = &editable_directives($in{'type'}, 'htaccess');

&error_setup(&text('efailed', $text{"type_$in{'type'}"}));
&parse_inputs(\@edit, $conf, $conf);

&redirect("htaccess_index.cgi?file=".&urlize($in{'file'}));
