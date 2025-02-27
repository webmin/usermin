## Changelog

#### 2.201
* Fix to properly escape HTML in date fields
* Fix the line height of plain-text email body

#### 2.200
* Add ability to use zoom window in/out using standard hotkeys in Terminal module
* Fix Usermin manual installation using setup script
* Fix to enhance display support for Fetchmail module
* Updated Chinese translations
* Update German translations

#### 2.102
* Update the Authentic theme to the latest version with various fixes and improvements

#### 2.100
* Add support for parsing iCalendar event files in the Mailbox module
* Fix issues with Terminal module to correct text display problems in editor mode
* Fix to store Terminal module logs in the /var/webmin directory
* Fix to display the Spam folder nicely in the Mailbox module

#### 2.010
* Fix ProFTPd module to use actual UI library
* Fix to using the `qrencode` command to generate QR codes locally instead of the remote Google Chart API
* Update Authentic theme to the latest version

#### 2.001
* Add support for reading gzipped email messages
* Fix new signing key import on Debian and derivatives
* Fix print email functionality for Read User Mail module
* Fix various XSS related issues

#### 2.000
* Add the Terminal module to Usermin
* Add support for loading images via the server when reading mail
* Fix to properly stop Usermin #89
* Update Authentic theme to the latest version with new vertical column layout

#### 1.861
* Add ability to set shell character encoding and set `TERM` environmental variable in the new Terminal module
* Add various improvements to the Framed Theme (and renaming “Gray Framed Theme” to “Framed Theme”)
* Fix to remove RC4 from the list of strong ciphers
* Fix error handling in MySQL/MariaDB Database server module when executing SQL commands
* Fix bugs for modules granting anonymous access
* Update Authentic theme to the latest version

#### 1.860
* Add enforcement of HTTP Strict Transport Security (HSTS) policy in SSL enabled mode
* Add Mint Linux support
* Update Authentic theme to the latest version

#### 1.853
* Add better support for CentOS Stream Linux for new installs
* Add support for mirror and RAID volumes in the LVM module
* Update Authentic theme with bug fixes and improvements in File Manager and other areas

#### 1.840
* Add a number of small features and improvements
* Fix a critical security issue (CVE-2022-30708)

#### 1.834
* Bug fixes release

#### 1.833
* Bug fixes release

#### 1.832
* Add support for archive extraction and folder uploads in File Manager
* Update translations
* Update Authentic theme to the latest version

#### 1.830
* Bug fixes release

#### 1.823
* Bug fixes release  

#### 1.820
* Update translations
* Update Authentic theme to the latest version

#### 1.812
* Bug fixes for 2FA sign-in and other minor issues  

#### 1.810
* Improvements in MySQL user management
* Update Authentic theme to the latest version

#### 1.802
* Add automatic translations for all modules for all supported languages
* Update Authentic theme to the latest version

#### 1.791
* Update Authentic theme with improvements to File Manager and overall UI  

#### 1.780
* Add security vulnerability fixes (urgent upgrade recommended)  

#### 1.770
* Fix various bugs
* Update translations
* Update Authentic theme to the latest version

#### 1.741
* Translation updates (German, Catalan, Bulgarian)  
* Update Authentic theme to the latest version

#### 1.730
* Add numerous translation updates
* Add a major new version of the Authentic theme  

#### 1.630
* Add various translation improvements
* Fix to disables insecure SSLv2 and SSLv3 by default

#### 1.510
* Added the new Gray Framed Theme, and made it the default for new installs.

#### 1.500
* Added support for Ubuntu 12.04.

#### 1.460
* Major Dutch translation updates, thanks to Gandyman.

#### 1.440
* Catalan translation updates by Jaume Badiella.

#### 1.430
* Added a `robots.txt` file to block indexing of Usermin by search engines.

#### 1.410
* Dutch translation updates, thanks to Gandyman.

#### 1.400
* Improved Usermin's search function to include links to relevant help pages and UI text.
* Changed the layout of search results to match Webmin's style.

#### 1.380
* Catalan translation updates by Jaume Badiella.
* Converted all core modules to use the new `WebminCore` Perl module instead of `web-lib.pl`, improving memory use and load time.

#### 1.340
* Many Greek translation updates, thanks to Vagelis Koutsomitros.

#### 1.330
* Big Czech translation updates, thanks to Petr Vanek and the Czech translation team.
* Made all popups XSS-safe, removing the need for referrer protection that previously broke some browsers.
* Usermin session IDs are now stored as MD5 hashes to prevent session capture via `sessiondb` DBM.

#### 1.320
* Links from unknown referrers are now blocked by default to prevent XSS attacks. This may affect browsers that don’t supply a `Referer:` header.

#### 1.310
* Added a search box to the left frame of the blue theme for finding modules, config options, help pages, and text.
* Set an HTTP `Expires` header for all static content (images, CSS, etc.) to improve caching.
* Changed the error message shown when Webmin detects an unauthorized link from another webpage.

#### 1.280
* Added support for blocking users with too many failed login attempts, configurable in Webmin's Usermin Configuration module.

#### 1.260
* Improved support for automatic domain name prepending by checking the first and second parts of the hostname in the URL.
* Added support for Slam64 Linux.
* Fixed XSS vulnerabilities in `pam_login.cgi`.

#### 1.250
* Large file uploads are no longer read into memory by `miniserv.pl`.
* Changed the default theme for all installs to the new framed blue theme.
* Updated UI links (e.g., select all, invert selection) to include separators.

#### 1.190
* The `From:` address for feedback emails is now taken from the Read Mail module.
* Proxy settings configured in Webmin's Usermin Configuration module are now passed to Usermin via `http_proxy` and `ftp_proxy` environment variables.

#### 1.180
* Added support for DAV clients.

#### 1.170
* Fixed a potential security hole caused by a bug in Perl.

#### 1.160
* Replaced all calls to the `crypt()` function with code that uses the `Crypt::UnixCrypt` Perl module on systems where `crypt()` is broken.

#### 1.150
* Fixed a bug that could allow a remote attack if full PAM conversation mode was enabled.

#### 1.110
* Reduced the size of all subheadings in the default MSC theme.

#### 1.100
* Enabled password timeouts by default during Usermin installation or upgrades to protect against brute-force password attacks.

#### 1.090
* Added support for Solaris 10.
* Included additional translations for various languages and modules.
* Improved OS version handling for configuration files to reduce the number of standard config files.

#### 1.080
* Fixed a security hole in `maketemp.pl`, which could allow an attacker to overwrite critical system files by creating a symbolic link in `/tmp/.usermin` before installation (CVE bug CAN-2004-0559).
* When PAM authentication is used, expired passwords are now detected, and users are prompted to change them (if enabled in the Usermin Configuration module).

#### 1.070
* Fixed a security issue where an attacker could lock valid users by sending bogus usernames or passwords.
* Fixed a bug that prevented user limiting from working when Usermin was run from `inetd`.
