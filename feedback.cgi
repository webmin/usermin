#!/usr/local/bin/perl
# Send the usermin feedback form

require './web-lib.pl';
&init_config();
require './ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();
&ReadParseMime();
&error_setup($text{'feedback_err'});
$gconfig{'feedback'} || &error($text{'feedback_ecannot'});

# Construct the email body
$in{'text'} =~ s/\r//g;
$date = localtime(time());
$ver = &get_webmin_version();
if ($in{'name'} && $in{'email'}) {
	$from = "$in{'name'} <$in{'email'}>";
	$email = $in{'email'};
	}
elsif ($in{'email'}) {
	$email = $from = $in{'email'};
	}
else {
	$email = $from = "feedback\@".&get_system_hostname();
	}
local $m = $in{'module'};
$m || !$in{'config'} || &error($text{'feedback_emodule'});
&check_os_support($m) && $m !~ /\.\./ || &error($text{'feedback_emodule2'});
if ($m) {
	%minfo = &get_module_info($m);
	$ver .= " (Module: $minfo{'version'})" if ($minfo{'version'});
	$module = "$m ($minfo{'desc'})";
	}
else {
	$module = "None";
	}
@tolist = ( $gconfig{'feedback'} );
foreach $t (@tolist) {
	$headers .= "To: $t\n";
	}
$headers .= "From: $from\n";
$headers .= "Subject: $text{'feedback_title'}\n";

$attach[0] = <<EOF;
Content-Type: text/plain
Content-Transfer-Encoding: 7bit

Name:            $in{'name'}
Email address:   $in{'email'}
Date:            $date
Usermin version: $ver
Module:          $module
Browser:         $ENV{'HTTP_USER_AGENT'}
EOF

$attach[0] .= "\n".$in{'text'}."\n";

if ($in{'config'}) {
	# Attach the user's preferences as a text file
	&read_file("$user_config_directory/$m/config", \%mconfig);
	if (keys %mconfig) {
		local $a;
		$a .= "Content-Type: text/plain; name=\"config\"\n";
		$a .= "Content-Transfer-Encoding: 7bit\n";
		$a .= "\n";
		foreach $k (keys %mconfig) {
			$a .= "$k=$mconfig{$k}\n";
			}
		push(@attach, $a);
		}
	}

# Include uploaded attached files
foreach $u ('attach0', 'attach1') {
	if ($in{$u} ne '') {
		local $a;
		local $name = &short_name($in{"${u}_filename"});
		local $type = $in{"${u}_content_type"};
		$type = &guess_mime_type($name) if (!$type);
		$a .= "Content-type: $type; name=\"$name\"\n";
		$a .= "Content-Transfer-Encoding: base64\n";
		$a .= "\n\n";
		$a .= &encode_base64($in{$u});
		push(@attach, $a);
		}
	}

# Build the MIME email
$bound = "bound".time();
$mail = $headers;
$mail .= "Content-Type: multipart/mixed; boundary=\"$bound\"\n";
$mail .= "MIME-Version: 1.0\n";
$mail .= "\n";
$mail .= "This is a multi-part message in MIME format.\n";
foreach $a (@attach) {
	$mail .= "\n--".$bound."\n";
	$mail .= $a;
	}
$mail .= "\n--".$bound."--\n";

if ($gconfig{'feedbackmail'}) {
	$ok = &send_via_smtp($gconfig{'feedbackmail'});
	$sent = 3 if ($ok);
	}

if (!$sent) {
	# Try to send the email by calling sendmail -t
	$sendmail = &has_command("sendmail");
	if (-x $sendmail && open(MAIL, "| $sendmail -t")) {
		print MAIL $mail;
		if (close(MAIL)) {
			$sent = 2;
			}
		}
	}

if (!$sent) {
	# Try to connect to a local SMTP server
	$ok = &send_via_smtp("localhost");
	$sent = 1 if ($ok);
	}

if ($sent) {
	# Tell the user that it was sent OK
	&ui_print_header(undef, $text{'feedback_title'}, "", undef, 0, 1);
	if ($sent == 3) {
		print &text('feedback_via', join(",", @tolist),
			    "<tt>$gconfig{'feedbackmail'}</tt>"),"\n";
		}
	elsif ($sent == 2) {
		print &text('feedback_prog', join(",", @tolist),
			    "<tt>$sendmail</tt>"),"\n";
		}
	else {
		print &text('feedback_via', join(",", @tolist),
			    "<tt>localhost</tt>"),"\n";
		}
	print "<p>\n";
	&ui_print_footer("/", $text{'index'});
	}
else {
	# Give up! Tell the user ..
	&error($text{'feedback_esend'});
	}

sub send_via_smtp
{
local $error;
&open_socket($_[0], 25, MAIL, \$error);
return 0 if ($error);
&smtp_command(MAIL) || return 0;
&smtp_command(MAIL, "helo ".&get_system_hostname()."\r\n") || return 0;
&smtp_command(MAIL, "mail from: $email\r\n") || return 0;
foreach $t (@tolist) {
	&smtp_command(MAIL, "rcpt to: $t\r\n") || return 0;
	}
&smtp_command(MAIL, "data\r\n");
$mail =~ s/\r//g;
$mail =~ s/\n/\r\n/g;
print MAIL $mail;
&smtp_command(MAIL, ".\r\n");
&smtp_command(MAIL, "quit\r\n");
close(MAIL);
return 1;
}

# smtp_command(handle, command)
sub smtp_command
{
local ($m, $c) = @_;
print $m $c;
local $r = <$m>;
return $r =~ /^[23]\d+/;
}

sub short_name
{
$_[0] =~ /([^\\\/]+)$/;
return $1;
}

