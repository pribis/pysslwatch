import nginxparser_eb
import os
import glob

file_path = '/etc/nginx/conf.d/bellastationery.com.conf'

class SSLWatchParse:
    domains = []
    confLocDefault = '/etc/nginx/conf.d'
    #Go trough all conf files, grabbing up domains
    #This assumes all domains are https.
    #Pass the location of your confs.  Default is /etc/nginx/conf.d
    def getDomains(self):
        try:
            for f in os.listdir(self.confLocDefault):
                if f == '.' or f =='..':
                    continue

                with open(self.confLocDefault+'/'+f, 'r') as fh:
                    parsed_content = nginxparser_eb.load(fh)
                for block in parsed_content:
                    if block[1][0][0] == 'server_name':
                        domain_names = block[1][0][1].split()
                        [self.domains.append(d) for d in domain_names]
                        

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
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
                new_domains.append(d)
                

        return list(set(new_domains))

    
    
