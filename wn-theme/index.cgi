#!/usr/local/bin/perl
# Show two frames, one on the left for modules and folders, and one on the
# right for the actual content

do './web-lib.pl';
&init_config();

# Display the frameset
&PrintHeader();
print "<!doctype html public \"-//W3C//DTD HTML 3.2 Final//EN\">\n";
print "<html><head><title>WorldNews Webmail</title></head>\n";
print "<frameset cols='150,*' border=0>\n";
$goto = &get_goto_module();
if ($goto) {
	print "<frame scrolling=no noresize src='left.cgi' name=left>\n";
	print "<frame scrolling=auto noresize src='$goto->{'dir'}/' name=body>\n";
	}
else {
	print "<frame scrolling=no noresize src='left.cgi' name=left>\n";
	print "<frame scrolling=auto noresize src='/mailbox/index.cgi' name=body>\n";
	}
print "</frameset></html>\n";

