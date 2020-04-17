"""
This file contains all classes required to use the CloudFlare API
"""

from requests import get, post, delete
from typing import List, Union, Dict

from Logger import logger


class Record:
    """ This class represents a DNS record (like A, AAAA, MX, CNAME etc.). """

    def __init__(self, json_object: dict):
        self.id: str = json_object["id"]
        self.type: str = json_object["type"]
        self.name: str = json_object["name"]
        self.content: str = json_object["content"]
        self.proxiable: bool = json_object["proxiable"]
        self.proxied: bool = json_object["proxied"]
        self.ttl: int = json_object["ttl"]
        self.locked: bool = json_object["locked"]
        self.zone_id: str = json_object["zone_id"]
        self.zone_name: str = json_object["zone_name"]
        self.modified_on: str = json_object["modified_on"]
        self.created_on: str = json_object["created_on"]
        self.meta: dict = json_object["meta"]


class Zone:
    """ This class represents a domain zone (like example.com). """

    def __init__(self, auth_headers: dict, json_object: dict):
        self.id: str = json_object["id"]
        self.type: str = json_object["type"]
        self.name: str = json_object["name"]
        self.development_mode: int = json_object["development_mode"]
        self.original_name_servers: List[str] = json_object["original_name_servers"]
        self.original_registrar: str = json_object["original_registrar"]
        self.original_dnshost: str = json_object["original_dnshost"]
        self.created_on: str = json_object["created_on"]
        self.modified_on: str = json_object["modified_on"]
        self.activated_on: str = json_object["activated_on"]
        self.owner: Dict[str:Union[str, dict]] = json_object["owner"]
        self.account: Dict[str:str] = json_object["account"]
        self.permissions: List[str] = json_object["permissions"]
        self.plan: Dict[str:Union[str, bool, int]] = json_object["plan"]
        self.plan_pending: Dict[str:Union[str, bool, int]] = json_object["plan_pending"]
        self.status: str = json_object["status"]
        self.paused: bool = json_object["paused"]
        self.type: str = json_object["type"]
        self.name_servers: List[str] = json_object["name_servers"]

        self.__auth_headers = auth_headers

    def get_records(self) -> List[Record]:
        """ Returns a list of all registered records. """

        records = get(f"https://api.cloudflare.com/client/v4/zones/{self.id}/dns_records", headers=self.__auth_headers).json()
        try:  # this fails on API error
            records = records["result"]
            return [Record(x) for x in records]
        except Exception as e:
            logger.error(e)
            return []

    def add_record(self, type: str, name: str, content: str, proxied: bool, priority: int = 10, ttl: int = 1):
        """ Adds a new record to the zone. (TTL value of 1 == AUTO) """

        response = post(f"https://api.cloudflare.com/client/v4/zones/{self.id}/dns_records", headers=self.__auth_headers,
                        json={"type": type, "name": name, "content": content, "ttl": ttl, "priority": priority, "proxied": proxied}).json()
        if response["success"]:
            return True
        else:
            return response["errors"]


class Account:
    """ This class represents your CloudFlare account and serves the fundamental methods. """

    def __init__(self, account_id: str, email: str, auth_key: str):
        if account_id is None or email is None or auth_key is None:
            logger.error(f"CloudFlare email, auth_key and account id shall not be None (account_id: {account_id}, email: {email}, auth_key: {auth_key}).")
            exit(1)
        self.id = account_id
        self.email = email
        self.__auth_key = auth_key
        self.__auth_headers = {"X-Auth-Email": self.email, "X-Auth-Key": self.__auth_key, "Content-Type": "application/json"}

    def get_zones(self) -> List[Zone]:
        """ Returns a list of all registered records. """

        zones = get(f"https://api.cloudflare.com/client/v4/zones", headers=self.__auth_headers).json()
        try:  # this fails on API error
            zones = zones["result"]
            return [Zone(self.__auth_headers, x) for x in zones]
        except Exception as e:
            logger.error(e)
            return []

    def add_zone(self, name: str):
        """ Adds a new zone to the account. """

        response = post(f"https://api.cloudflare.com/client/v4/zones", headers=self.__auth_headers,
                        json={"name": name, "account": {"id": self.id}}).json()
        if response["success"]:
            return True
        else:
            return response["errors"]

    def delete_zone(self, zone: Zone):
        """ Remove/de-register a zone from the account."""

        response = delete(f"https://api.cloudflare.com/client/v4/zones/{zone.id}", headers=self.__auth_headers).json()
        if response["success"]:
            return True
        else:
            return response["errors"]
