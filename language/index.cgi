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
my $ulangneutral = $gconfig{"langneutral_$remote_user"};
my $selectjs = <<EOF;
<script>
(function () {
    const select = document.querySelector('select[name="lang"]'),
          span = document.querySelector('span[data-neutral]'),
	  checkbox = document.querySelector('input[name="langneutral"]');
    const update = function() {
        const selected = select.options[select.selectedIndex],
              show = selected.getAttribute('data-neutral') === '1';
        span.style.visibility = show ? 'visible' : 'hidden';
	if (!show) checkbox.checked = false;
    }
    update();
    select.addEventListener('change', update);
})();
</script>
EOF

print &ui_table_row($text{'index_lang'},
  &ui_select("lang", $ulang,
	[ [ "", $text{'index_global'} ],
	  map { [ $_->{'lang'}, $_->{'desc'}, "data-neutral='$_->{'neutral'}'" ] }
	      &list_languages() ]) .
          "<wbr data-group><span data-nowrap>&nbsp;&nbsp;". 
            &ui_checkbox("langauto", 1,
                $text{'langauto_include'}, $ulangauto).
            "&nbsp;&nbsp;<span data-neutral>".
            &ui_checkbox("langneutral", 1,
                $text{'langneutral_include'}, $ulangneutral).
            "</span>".
          "</span>$selectjs");

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

