#!/usr/local/bin/perl
# add_address.cgi
# Add an address from an email to the user's address book
use strict;
use warnings;
our %in;

require './mailbox-lib.pl';
&ReadParse();
&create_address($in{'addr'}, $in{'name'});
my @sub = split(/\0/, $in{'sub'});
my $subs = join("", map { "&sub=$_" } @sub);
my $qid = &urlize($in{'id'});
&redirect("view_mail.cgi?id=$qid&folder=$in{'folder'}$subs");
