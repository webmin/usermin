#!/usr/local/bin/perl
# index.cgi
# Display user's plan file

require './plan-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

print &ui_form_start("save_plan.cgi", "form-data");
$host = &get_system_hostname();
print &text('index_desc', "<tt>$remote_user\@$host</tt>"),"<br>\n";
print &ui_textarea("plan", &read_file_contents($plan_file), 20, 70),"<br>\n";
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("/", $text{'index'});

