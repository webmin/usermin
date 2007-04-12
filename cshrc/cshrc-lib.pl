# cshrc-lib.pl

do '../web-lib.pl';
&init_config();
require '../ui-lib.pl';
&switch_to_remote_user();
&create_user_config_dirs();

if ($remote_user_info[8] =~ /\/(csh|tcsh)$/) {
	@cshrc_files = ( "$remote_user_info[7]/.cshrc",
			 "$remote_user_info[7]/.login" );
	@cshrc_types = ( 0, 1 );
	}
elsif ($remote_user_info[8] =~ /\/bash$/ ||
       &resolve_links($remote_user_info[8]) =~ /\/bash$/) {
	@cshrc_files = ( "$remote_user_info[7]/.bashrc",
			 "$remote_user_info[7]/.profile" );
	@cshrc_types = ( 0, 1 );
	}
else {
	@cshrc_files = ( "$remote_user_info[7]/.profile" );
	@cshrc_types = ( 1 );
	}

1;

