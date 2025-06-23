import nginxparser
import os

file_path = '/etc/nginx/conf.d/bellastationery.com.conf'
domains = []
class sslwatchparse:
    confLocDef = '/etc/nginx/conf.d'
    #Go trough all conf files, grabbing up domains
    #This assumes all domains are https.
    #Pass the location of your confs.  Default is /etc/nginx/conf.d
    def getDomains(confLocation):
        try:
            with open(file_path, 'r') as f:
                parsed_content = nginxparser.loads(f.read())

            for block in parsed_content:
                if block[0] == 'server':
                    for item in block:
                        if isinstance(item, list) and item[0] == 'server_name':
                            domains.extend(item[1].split())
            print("Extracted Domains:", domains)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
    


    #Remove dups and, if specified, remove www.
    def cleanup(makenaked=True):
        pass

    
    
