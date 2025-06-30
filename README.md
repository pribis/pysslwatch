#pysslwatch#

##Watch SSL certs and report results, highlighting expiration concerns.##

pysslwatch goes through the server conf files and extracts all the domains
and checks the certificate expiration status. It will highlight any
pending expirations.

**[Note: only Nginx is supported at this time.]**

The script can be minimally configurated. The instructions are in the pysslwatch.py
file itself.

The way I use it is to put the contents of the pysslwatch folder somewhere and then
call pysslwatch.py from a shell script within the /etc/cron.daily folder.  But you
can simply call it anytime you want an overview of your cert statuses.

The program will try and fail gracefully where it can.


This script is free to use in anyway you see fit. Consider it licensed under GNU GPL.
I **do not** take responsibility for anything bad that might happen running this program.
**Use at your own risk**.  As with any script you run on your system, read through the code
and understand what is going on. The code isn't that long and should be easy to understand
by anyone familiar with Python. Even a noob should be able to figure it out.

