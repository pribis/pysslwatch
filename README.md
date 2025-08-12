# pysslwatch

## Watch SSL certs and report results, highlighting expiration concerns.

pysslwatch goes through the server conf files and extracts all the domains
and checks the certificate expiration status. It will inform you of any
pending expirations by giving you a WARNING or CRITICAL notification.

**[Note: only Nginx is supported at this time.]**

### Config
The script itself contains a nominal amount of default configuration, but it is
not complete and the script will fail if you don't set up the config.yml file correctly. 
You may edit these values at the head of the script, but this isn't the recommended way.

Instead, use the config.yml.example file. First rename it to config.yml and then
edit it for your particular needs. You may want to set debug=2, which will print
info but not email the results. debug=1 will print results and email. debug=0 will
not print any results except where the system call to openssl fails. 

The configuration falls through this way:
1. config.yml (overrides all values)
2. environmental variables (overrides defaults)
3. defaults 

The two environmental variables you can set are:
PYSSLWATCH_NOTIFY_EMAIL
PYSSLWATCH_FROM_EMAIL

As already mentioned, these will be overridden by the config.yml.

Most of the configuration file is self-explanatory, but a couple of
items are worth mentioning.

warn: the number of days within which you should be warned of pending expiration. 
critical: Like warn but now you *really* ought to do something soon.
ignore: confs will ignore an entire configuration file. domains will ignore a single
domain. You may use either/both or neither. 

### Usage
The way I use it is to put the contents of the pysslwatch folder somewhere and then
call pysslwatch.py from a shell script within the /etc/cron.daily folder.  But you
can simply call it anytime you want an overview of your cert statuses.

The program assumes your conf files contain only server_names listening on port 443.

The program will try and fail gracefully where it can.

Information will be logged to /var/log/pysslwatch.log (Or wherever you set this in
the config.yml file). The logging level can be changed for the program, but it will 
always log to that file regardless. 

If you choose to set environmental variables for the email settings you will need to make
sure you run pysslwatch as that user or else set the variables in the cron script. I mostly
included that capability for testing purposes, but it is there should you choose to use it.


### License
This script is free to use in anyway you see fit. Consider it licensed under the GNU GPL (v3).
I **do not** take responsibility for anything bad that might happen running this program.
**Use at your own risk**.  As with any script you run on your system, read through the code
and understand what it is doing. The code isn't that long and should be easy to understand
by anyone familiar with Python.

