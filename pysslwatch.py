  #!/usr/bin/env python
  
import subprocess
import sys
import re
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
from datetime import datetime
from subprocess import Popen, PIPE
import pysslwatchparse
import os
import yaml

############################################################
# Configure the following.
#
# Make sure to set your alert/from email addresses
# or you'll never get any messages sent to you.
#
# You can also define environmental variables:
# SSLWATCH_NOTIFY_EMAIL
# SSLWATCH_FROM_EMAIL
#


openssl = '/usr/bin/openssl'
sendmail = '/usr/sbin/sendmail'
warn = 30  #days
critical = 10 #days
debug_level = 1 #0=nothing; >0 messages to STDOUT
log_file = '/var/log/pysslwatch.log'
notify_email = '<Email address to send reports to>'
from_email = '<Your from email address>'
subject = '[SUBJECT LINE] Your SSL report'
conf_location = '/etc/nginx/conf.d'

ignore_confs = [
    ]

ignore_domains = [
    ]


###########No touchy########

def send_mail(msg_bundle):
    body = "Hey there!  Here's a report on your SSL certs.\n\n\n"
    for site in msg_bundle:
        if msg_bundle[site]['level'] == 'critical':
            body +=  'CRITICAL!!! Site: '+site+' Issuer: '+msg_bundle[site]['issuer']+' has '+str(msg_bundle[site]['days_left'])+' days before certificate expires\n\n'
        elif msg_bundle[site]['level'] == 'warning':
            body +=  'WARNING Site: '+site+' Issuer: '+msg_bundle[site]['issuer']+' has '+str(msg_bundle[site]['days_left'])+' days before certificate expires\n\n'
        elif msg_bundle[site]['level'] == '':
            body +=  'Site: '+site+' Issuer: '+msg_bundle[site]['issuer']+' has '+str(msg_bundle[site]['days_left'])+' days before certificate expires\n\n'
        elif msg_bundle[site]['level'] == 'fatal_error':
            body += 'Site: '+site+' Message: '+msg_bundle[site]['message']+'\n\n'
        else:
            log('Something went horribly wrong.')
    body += '\n\nThanks!  IT Dept.\n\n\n'
    if debug_level > 1: #Don't send
        print(body)
    else:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = notify_email
        msg['From'] = from_email
        p = Popen([sendmail,'-t','-oi'], stdin=PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
        #print(p.returncode)
    
def get_cert_info(host):
    if debug_level > 0:
        print("Checking " + host)
        
    cert_info = {}        
    try:

        cmd = (
            f"echo | {openssl} s_client -showcerts -servername {host} -connect {host}:443 2>/dev/null | "
            f"{openssl} x509 -inform pem -noout -enddate -issuer"
        )
        out = subprocess.check_output(cmd, shell=True)

        out = out.decode('utf-8')  
        cert_dict = out.split('\n')
        prog  = re.compile(r"(notAfter|issuer)=(.+)")

        for i in cert_dict:
            res = prog.match(i)
            if res:
                cert_info[res.group(1)] = res.group(2)

        if not cert_info:
            return None
        else:
            return cert_info
    except Exception as e:
        if debug_level > 1:
            print(f'{e}')
        log(f"Could not obtain cert info for {host}:{e} ")


def check_date(cert_exp_date):
    """Return the number of days left before expiration"""
    right_now = datetime.utcnow()
    right_then = datetime.strptime(cert_exp_date,  '%b %d %H:%M:%S %Y %Z')
    return  abs((right_then - right_now).days)

def log(msg):
    with open(log_file, 'a') as fh:
        fh.write(msg+'\n')

    if debug_level > 1:
        print(msg+'\n')


def main(sites):
    global warn
    global critical
    
    mail_msg = {}
    level = ''

    for site in sites:
        c_info =  get_cert_info(site)

        if not c_info:
            
            log(f'{site} Could not obtain cert info.')
            
            mail_msg[site] = {
                'level': 'fatal_error',
                'message': 'Could not obtain cert info',
                'days_left': 0,
                'exp_date': 0,
                'issuer': 'Unknown'
            }
            continue


        days_left = check_date(c_info['notAfter'])
        if days_left < critical:
            level = "critical"
        elif days_left < warn:
            level = "warning"

        if debug_level > 0:
            log("Site: "+site+" Issuer: "+c_info['issuer']+" has "+str(days_left)+" days before certificate expires")

        #Send only warning/critical
        if debug_level < 1 and level != '':
            mail_msg[site] = {
                'days_left':days_left,
                'level': level,
                'issuer': c_info['issuer'],
                'exp_date':c_info['notAfter'],
                'message': ''
            }
        elif debug_level == 1: #Send everything
            mail_msg[site] = {
                'days_left':days_left,
                'level': level,
                'issuer': c_info['issuer'],
                'exp_date':c_info['notAfter'],
                'message': ''
            }

                        
        level = ''
    if len(mail_msg) > 0:
        send_mail(mail_msg)


def config():
    with open('config.yaml', 'r') as fh:
        global notify_email
        global from_email
        global subject
        global debug_level
        global openssl
        global conf_location
        global log_file
        global ignore_confs
        global ignore_domains
        global warn
        global critical
        
        config = yaml.safe_load(fh)
        if 'defaults' in config:
            print("Found defaults.")
            if 'notify_email' in config['defaults']:
                notify_email = config['defaults']['notify_email']
            if 'from_email' in config['defaults']:
                from_email = config['defaults']['from_email']
            if 'subject' in config['defaults']:
                subject = config['defaults']['subject']
            if 'debug' in config['defaults']:
                debug_level = config['defaults']['debug']

            if 'warn' in config['defaults']:
                warn = config['defaults']['warn']
            if 'critical' in config['defaults']:
                critical = config['defaults']['critical']
                
            if 'system' in config:
                if 'openssl' in config['system']:
                    openssl = config['system']['openssl']
                if 'conf_location' in config['system']:
                    conf_location = config['system']['conf_location']
                if 'log_file' in config['system']:
                    log_file = config['system']['log_file']
                if 'sendmail' in config['system']:
                    sendmail = config['system']['sendmail']
                

            if 'ignore' in config:
                if 'domains' in config['ignore']:
                    ignore_domains = config['ignore']['domains']
                if 'confs' in config['ignore']:
                    ignore_confs = config['ignore']['confs']

def test():
    print('Configuration settings:')
    print('-----------------------')
    print('DEFAULTS')
    print(f'Notify email: {notify_email}')
    print(f'From email: {from_email}')
    print(f'Subject: {subject}')
    print(f'Debug level: {debug_level}')
    print('\n')
    print("System settings:")
    
    print(f'Open ssl bin directory (Default /usr/bin/openssl): {openssl}')
    print(f'Webserver conf location (Default /etc/nginx/conf.d): {conf_location}')
    print(f'Log file location (Default /var/www/pysslwatch.log): {log_file}')
    print('\n')
    print('IGNORE LISTS')
    print(f'Domains to ignore: {ignore_domains}')
    print(f'Confs to ignore: {ignore_confs}')


    print('--------END---------')
                
if __name__ == "__main__":

    #Make sure defaults are set up correctly.
    if 'PYSSLWATCH_NOTIFY_EMAIL' in os.environ:
        a_email = os.environ['PYSSLWATCH_NOTIFY_EMAIL']
        if a_email != None:
            notify_email = a_email

    if 'PYSSLWATCH_FROM_EMAIL' in os.environ:
        f_email = os.environ['PYSSLWATCH_FROM_EMAIL']
        if f_email != None:
            from_email = f_email    

    #Now we load configs and override anything we just got if we can:
    config()
            
    if conf_location == '':
        print('NGINX configuration file location not defined.')
        exit(1)

    if len(sys.argv) > 1:
        main([sys.argv[1]])
    else:
        parse = pysslwatchparse.SSLWatchParse(conf_location, ignore_confs, ignore_domains)
        try:
            domains = parse.getDomains()
        except Exception as e:
            log(e)
            
        main(domains)
        
