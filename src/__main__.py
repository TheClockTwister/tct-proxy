"""
This file is executed by the container at runtime. The routine will run as follows:

1. Check if config has changed.
2. If so, re-generate a new config for /etc/nginx/sites-enabled/default
3. Restart nginx service

The main function can be imported and included into other applications, however, I do not provide large
compatibility, since this is not the primary intention of this application. You may run it in a second
program, but if so, it will run in an infinite loop, reserving the full thread.
"""

import json
import os
from time import sleep
from requests import get

from nginx import NginxConfigCreator
from Logger import logger
from cloudflare import Account


def get_public_ip() -> str:
    return get("https://api.ipify.org").text


def check_cf_zone(account: Account, domain: str):
    zones = account.get_zones()
    if domain in [zone.name for zone in zones]:
        logger.debug(f"Found {domain} in CloudFlare zones.")
        return True
    else:
        logger.debug(f"{domain} is not a registered CloudFlare zone.")
        return False


def wait_for_config_change(current_config: dict) -> dict:
    config_old = current_config
    sleep(current_config["server"]["config_check_interval"])
    while config == config_old:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
        sleep(config["server"]["config_check_interval"])
    logger.info("Config has changed. Generating Nginx config and restarting service.")
    return config


def main():
    """ The application's main loop """

    with open("config.json", "r") as f:
        config = json.loads(f.read())

    ncc = NginxConfigCreator()
    acc = Account(config["cloudflare"]["account"], config["cloudflare"]["email"], config["cloudflare"]["auth_key"])
    public_ip = get_public_ip()

    while True:

        # generates new Nginx config
        ncc.run(config)

        # get all (domain_name, host) where cloudflare==True
        cf_hosts = [(domain_name, hostname, host) if host["cloudflare"] else None for (domain_name, domain) in config["nginx"].items() for (hostname, host) in domain.items()]
        zones = acc.get_zones()  # For all CF-synced hosts
        for domain_name, hostname, host in cf_hosts:
            logger.info(f"CloudFlare sync is enabled for {hostname}.")

            if domain_name in [zone.name for zone in zones]:
                logger.debug(f"Zone '{domain_name}' is already registered.")
            else:
                logger.info(f"New zone '{domain_name}' will be registered.")
                acc.add_zone(domain_name)

        config = wait_for_config_change(config)  # this waits for a changed config and returns (updates) the new version


if __name__ == '__main__':
    main()
