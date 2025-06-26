import nginxparser_eb
import os
import glob
import re

class SSLWatchParse:
    domains = []
    conf_location = ''
    ignore_confs = []
    ignore_domains = []
    
    def __init__(conf_location, ignore_confs, ignore_domains):
        pass

    def getDomains():
        pattern = re.compile(r'\s*(server_name\s+.+)\s*;')
        try:
            for f in os.listdir(conf_location):
                if f == '.' or f =='..':
                    continue
                if f in ignore_confs:
                    continue

                with open(conf_location+'/'+f, 'r') as fh:
                    for line in fh:
                        match = pattern.findall(line)
                        if match:
                            domain_names = match[0].split()
                            [self.domains.append(d.strip()) for d in domain_names[1:] if d not in ignore_domains]
                        

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

    
    
