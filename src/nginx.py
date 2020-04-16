import os

from Logger import logger


class NginxConfigCreator:
    class Site:
        def __init__(self, domain, host, type, cloudflare, endpoint):
            self.domain = domain
            self.host = host
            self.type = type
            self.cloudflare = cloudflare
            self.url = endpoint

    def __init__(self, nginx_conf_path: str = "/etc/nginx/sites-enabled/default"):
        """
        :param nginx_conf_path: The path where the nginx config file on teh host / container lies.
        """

        self.nginx_conf_path = nginx_conf_path

        self.sites = []
        self.http_to_https = False
        self.config = """
        add_header X-XSS-Protection "1; mode=block";
        server_tokens off;
        """

    def __make_site_generic(self, site: Site):
        return """
    #################################################################################################
    # %s#
    #################################################################################################
    server {
        listen 80;
        client_max_body_size 250m;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload';
    
        server_name %s;
        location / {proxy_pass %s;}
    }
    """ % ((f"{site.host} ({site.domain})" + " " * 94)[:94].upper(), site.host, site.url)

    def __make_site_wordpress(self, site: Site):
        return """
    #################################################################################################
    # %s#
    #################################################################################################
    server {
        listen 80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    
        server_name %s;
        location / {proxy_pass %s;}
    }
    """ % ((f"{site.host} ({site.domain})" + " " * 94)[:94].upper(), site.host, site.url)

    def __make_site_emby(self, site: Site):
        return """
    #################################################################################################
    # %s#
    #################################################################################################
    server {
        listen 80;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload';
    
        server_name %s;
        location / {proxy_pass %s;}
    }
    """ % ((f"{site.host} ({site.domain})" + " " * 94)[:94].upper(), site.host, site.url)

    def run(self, config: dict):
        try:
            logger.info("Making new config.......")

            for domain in config["nginx"].keys():
                for host in config["nginx"][domain].keys():
                    json_obj = {"domain": domain, "host": host, **config["nginx"][domain][host]}
                    self.sites.append(self.Site(**json_obj))

            for site in self.sites:
                if site.type.upper() == "GENERIC":
                    self.config += self.__make_site_generic(site) + "\n\n"
                elif site.type.upper() == "WORDPRESS":
                    self.config += self.__make_site_wordpress(site) + "\n\n"
                elif site.type.upper() == "EMBY":
                    self.config += self.__make_site_emby(site) + "\n\n"

            if self.http_to_https:
                self.config += """
        # Redirect all HTTP -> HTTPS
        server {	
            listen 80 default_server;
            server_name _;
            return 301 https://$host$request_uri;
        }
        """

            with open(self.nginx_conf_path, "w+") as f:
                f.write(self.config)

            logger.debug("Successfully created new Nginx config.")

            logger.debug("Restarting nginx........")
            os.system("service nginx restart")
            logger.info("Successfully updated Nginx (config and service).")

        except InterruptedError as e:
            logger.error(e)
