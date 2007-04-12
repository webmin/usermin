#!/usr/local/bin/perl
# editor.pl
# Called by chfn to edit freebsd user details

sleep(1);
open(FILE, $ARGV[0]);
@lines = <FILE>;
close(FILE);
open(FILE, ">$ARGV[0]");
foreach $l (@lines) {
	if ($l =~ /^(Shell):/i) {
		$l = "$1: $ENV{'EDITOR_SHELL'}\n";
		}
	elsif ($l =~ /^(Full Name):/i) {
		$l = "$1: $ENV{'EDITOR_REAL'}\n";
		}
	elsif ($l =~ /^(Office Location):/i) {
		$l = "$1: $ENV{'EDITOR_OFFICE'}\n";
		}
	elsif ($l =~ /^(Office Phone):/i) {
		$l = "$1: $ENV{'EDITOR_OPHONE'}\n";
		}
	elsif ($l =~ /^(Home Phone):/i) {
		$l = "$1: $ENV{'EDITOR_HPHONE'}\n";
		}
	print FILE $l;
	}
close(FILE);

