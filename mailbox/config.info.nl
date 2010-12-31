line1=Inbox formaat en locatie,11
mail_system=Mail opslag formaat voor Inbox,4,0-Sendmail stijl enkele file (mbox),1-Qmail stijl directory (Maildir),3-MH stijl directory (MH),2-Remote POP3 server,4-Remote IMAP server
mail_dir=Sendmail mail file locatie,3,File onder home directory
mail_file=Sendmail mail file in home directory,0
mail_qmail=Qmail of MH directory locatie,3,Subdirectory onder home directory
mail_dir_qmail=Qmail of MH directory in home directory,0
mail_style=Mail subdirectory stijl,4,0-mail/username,1-mail/u/username,2-mail/u/us/username,3-mail/u/s/username
pop3_server=POP3 of IMAP server naam,3,<tt>localhost</tt>

line2=Versturen email,11
send_mode=Verstuur mail via verbinding naar,3,Sendmail executable
no_crlf=toevoegen carriage return ( \r ) aan iedere regel?,1,0-Ja,1-Nee
smtp_user=SMTP login naam voor mail server,3,Geen
smtp_pass=SMTP wachtwoord voor mail server,3,Geen
smtp_auth=SMTP authenticatie methode,4,-Standaard,Cram-MD5-Cram&#45;MD5,Digest-MD5-Digest&#45;MD5,Plain-Plain,Login-Login
smtp_port=Poort nummer voor SMTP,1,Standaard (25)
sendmail_path=Sendmail opdracht,0
no_orig_ip=Browser IP toevoegen in X-Originele-IP header?,1,0-Ja,1-Nee
no_mailer=Webmin versie toevoegen in X-Mailer header?,1,0-Ja,1-Nee

line3=Gebruiker van adressen,11
server_name=Standaard hostnaam voor Van: adressen,10,-Van echte hostnaam,*-Van URL,ldap-Opzoeken in LDAP
edit_from=Bewerken toestaan Van: adres,1,1-Ja,0-Nee (altijd gebruikersnaam@hostnaam),2-Alleen het gebruikersnaam gedeelte
from_map=Van: adres mapping file,3,Geen
from_format=Adres mapping file formaat,1,0-Gebruikersnaam naar adres (genericstabel),1-Adres naar gebruikersnaam (virtusertabel)

line3.5=Qmail+LDAP opties,11
ldap_host=LDAP server,3,Niet gebruikt
ldap_port=LDAP poort,3,Standaard
ldap_login=Login voor LDAP server,0
ldap_pass=Password voor LDAP server,0
ldap_base=Base voor mail gebruikers,0

line3.6=Spam opties,11
spam_report=Rapporteer spam met gebruik van,1,sa_learn-sa&#45;learn &#45;&#45;spam,spamassassin-spamassasin &#45;r,-Beslis automatisch
spam_always=Laat spam opties zien indien SpamAssassin module is,1,1-Geinstalleerd,0-Geinstalleerd en beschikbaar

line3.7=Mail quota opties,11
max_quota=Maximum toegestane grote voor alle folders (bytes),3,Ongelimiteerd
ldap_quotas=Forceer LDAP quotas?,1,1-Ja,0-Nee

line4=Other settings en Beperkingen,11
server_attach=Sta toegang toe aan server-zijde files?,1,2-Bijvoegen en Weghalen,1-Alleen bijvoegen,0-Niets
max_attach=Maximum totale bijlage grote,3,Ongelimiteerd
global_address=Globale adres boek file,3,Geen
global_address_group=Globale adres groep boek file,3,Geen
folder_types=Echte folder soorten toestaan,2,local-File onder ~/mail,ext-Externe file,pop3-POP3 server,imap-IMAP server
folder_virts=Toegestane virtuele folder soorten,2,virt-Virtuele,comp-Compositie
pop_locks=Controleer voor POP3 slot files?,1,1-Ja,0-Nee
shortindex=Basis filenaam voor index files,1,1-Laatste gedeelte van de filenaam,0-Volledige filenaam

