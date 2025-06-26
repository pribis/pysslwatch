  #!/usr/bin/env python
  
import subprocess
import sys
import re
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
from datetime import datetime
import pysslwatchparse

OPENSSL = "/usr/bin/openssl"
warn = 30  #days
critical = 10 #days
debug_level = 1
alert_email = "admin@boxcarpress.com"
from_email = "ssl_alert@boxcarpress.com"

def send_mail(msg_bundle):
    body = "Hey there!  Here's a report on your SSL certs.\n\n\n"
    for site in msg_bundle:
        if msg_bundle[site]['level'] == "critical":
            body +=  "CRITICAL!!! Site: "+site+" Issuer: "+msg_bundle[site]['issuer']+" has "+str(msg_bundle[site]['days_left'])+" days before certificate expires\n\n"
        elif msg_bundle[site]['level'] == "warning":
            body +=  "WARNING Site: "+site+" Issuer: "+msg_bundle[site]['issuer']+" has "+str(msg_bundle[site]['days_left'])+" days before certificate expires\n\n"
        elif msg_bundle[site]['level'] == "" and debug_level > 0: #Send info anyway
            body +=  "Site: "+site+" Issuer: "+msg_bundle[site]['issuer']+" has "+str(msg_bundle[site]['days_left'])+" days before certificate expires\n\n"
        else: 
            pass
    body += "\n\nThanks!  IT Dept.\n\n\n"
    if debug_level > 1:
        print(body)
    else:
        if debug_level > 0:          msg = MIMEText(body)
        msg['Subject'] = "Boxcar SSL Certificate Report"
        msg['To'] = alert_email
        msg['From'] = from_email
        s = smtplib.SMTP('localhost')
        s.sendmail(from_email, [alert_email], msg.as_string())
        s.quit()
    
def get_cert_info(host):
    out = subprocess.check_output("echo | "+OPENSSL+" s_client -showcerts -servername "+host+" -connect "+host+":443 2>/dev/null | "+OPENSSL+" x509 -inform pem -noout -enddate -issuer", shell=True)
    out = out.decode('utf-8')  
    cert_dict = out.split('\n')
    prog  = re.compile(r"(notAfter|issuer)=(.+)")
    cert_info = {}
    for i in cert_dict:
        res = prog.match(i)
        if res:
            cert_info[res.group(1)] = res.group(2)
    return cert_info

def check_date(cert_exp_date):
    """Return the number of days left before expiration"""
    right_now = datetime.utcnow()
    right_then = datetime.strptime(cert_exp_date,  '%b %d %H:%M:%S %Y %Z')
    return  abs((right_then - right_now).days)

def log(msg):
    pass

def main(sites):
    mail_msg = {}
    level = ""

    for site in sites:
        c_info =  get_cert_info(site)
        days_left = check_date(c_info['notAfter'])
        if days_left < critical:
            level = "critical"
        elif days_left < warn:
            level = "warning"
        elif debug_level > 0:
            level = ""
            log("Site: "+site+" Issuer: "+c_info['issuer']+" has "+str(days_left)+" days before certificate expires")
        else:
            continue 

        mail_msg[site] = {
            'days_left':days_left,
            'level': level,
            'issuer': c_info['issuer'],
            'exp_date':c_info['notAfter']
        }

    if len(mail_msg) > 0:
        send_mail(mail_msg)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main([sys.argv[1]])
    else:
        parse = pysslwatchparse.SSLWatchParse()
        [print(a) for a in parse.getDomains()]

        domains = parse.getDomains()
        main(domains)
        
