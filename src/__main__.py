import json
from time import sleep
from nginx import NginxConfigCreator

from Logger import logger

ncc = NginxConfigCreator()

if __name__ == '__main__':
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
