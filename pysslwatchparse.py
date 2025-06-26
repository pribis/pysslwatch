import nginxparser_eb
import os
import glob
import re

file_path = '/etc/nginx/conf.d/bellastationery.com.conf'
class SSLWatchParse:
    domains = []
    #confLocDefault = '/etc/nginx/conf.d'
    confLocDefault = '/Users/brian/tmp/certs'
    #Go trough all conf files, grabbing up domains
    #This assumes all domains are https.
    #Pass the location of your confs.  Default is /etc/nginx/conf.d
    def getDomains(self, ignore_confs):
        pattern = re.compile(r'\s*(server_name\s+.+)\s*;')
        try:
            for f in os.listdir(self.confLocDefault):
                if f == '.' or f =='..':
                    continue
                if f in ignore_confs:
                    continue
                
                with open(self.confLocDefault+'/'+f, 'r') as fh:
                    for line in fh:
                        match = pattern.findall(line)
                        if match:
                            domain_names = match[0].split()
                            [self.domains.append(d.strip()) for d in domain_names[1:]]
                        

        except FileNotFoundError as e:
            print(f"Error: File not found at {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

            
        return self.cleanup(self.domains, True)
    def removeDups():
        pass

    #Remove dups and, if specified, remove www.
    def cleanup(self, domains, makenaked=True):
        new_domains = []

        for d in domains:
            old_domains = d.split('.')
            if old_domains[0] == 'www':
                new_domains.append('.'.join(old_domains[1:]))
            else:
                if len(d) > 0 and d != 'localhost':
                    new_domains.append(d)
                

        return list(set(new_domains))

    
    
