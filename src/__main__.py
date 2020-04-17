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
from time import sleep
from nginx import NginxConfigCreator

from Logger import logger


def main():
    """ The application's main loop """

    ncc = NginxConfigCreator()

    while True:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
        ncc.run(config)  # generates new Nginx config

        config_old = config
        while config == config_old:
            with open("config.json", "r") as f:
                config = json.loads(f.read())
            sleep(config["server"]["config_check_interval"])
        logger.info("Config has changed. Generating Nginx config and restarting service.")


if __name__ == '__main__':
    main()
