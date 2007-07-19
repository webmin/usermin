#!/usr/local/bin/perl
# add_address.cgi
# Add an address from an email to the user's address book

require './mailbox-lib.pl';
&ReadParse();
&create_address($in{'addr'}, $in{'name'});
@sub = split(/\0/, $in{'sub'});
$subs = join("", map { "&sub=$_" } @sub);
$qid = &urlize($in{'id'});
&redirect("view_mail.cgi?id=$qid&folder=$in{'folder'}$subs");

