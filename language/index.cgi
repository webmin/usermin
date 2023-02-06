#!/usr/local/bin/perl
# edit_lang.cgi
# Language config form

require './language-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

print $text{'index_intro'},"<p>\n";

print &ui_form_start("change_lang.cgi");
print &ui_table_start(undef, "width=100%", 2);

# Language
my $ulang = $gconfig{'lang_'.$remote_user};
my $ulangauto = load_language_auto();
print &ui_table_row($text{'index_lang'},
  &ui_select("lang", $ulang,
	[ [ "", $text{'index_global'} ],
	  map { [ $_->{'lang'}, $_->{'desc'}."" ] }
	      &list_languages() ]) ." ". 
	&ui_checkbox("langauto", 1, $text{'langauto_include'}, $ulangauto));

# Locale
my $ulocale = $gconfig{'locale_'.$remote_user};
eval "use DateTime; use DateTime::Locale; use DateTime::TimeZone;";
if (!$@) {
        my $locales = &list_locales();
        my %localesrev = reverse %{$locales};
    print &ui_table_row($text{'index_locale'},
      &ui_select("locale", $ulocale,
	           [ [ "", $text{'index_global'} ],
	             map { [ $localesrev{$_}, $_ ] } sort values %{$locales} ]));
        }

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'index_ok'} ] ]);

&ui_print_footer("/", $text{'index'});

