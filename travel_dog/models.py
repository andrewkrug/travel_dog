# Implement logic for the api used to build the homepage
import os
import random
import uuid

from boto3.dynamodb.conditions import Key, Attr
from faker import Faker
from logging import getLogger


log = getLogger(__name__)


class User(object):
    def __init__(self, table):
        self.id = None
        self.username = None
        self.surname = None
        self.givenname = None
        self.age = None
        self.location = None
        self.address = None
        self.favorite_location_img = None
        self.favorite_location_url = None
        self.table = table
        self.adversary = False

    def create(self):
        result = self.table.put_item(
            Item={
                "id": self.id,
                "username": self.username,
                "surname": self.surname,
                "given_name": self.givenname,
                "age": self.age,
                "location": self.location,
                "address": self.address,
                "favorite_location_img": self.favorite_location_img,
                "favorite_location_url": self.favorite_location_url,
            }
        )

        return result

    def update(self, updated_profile):
        result = self.table.put_item(
            Item={
                "id": updated_profile["id"],
                "username": updated_profile["username"],
                "surname": updated_profile["surname"],
                "given_name": updated_profile["given_name"],
                "age": updated_profile["age"],
                "location": updated_profile["location"],
                "address": updated_profile["address"],
                "favorite_location_img": updated_profile["favorite_location_img"],
                "favorite_location_url": updated_profile["favorite_location_url"],
            }
        )
        return result

    def find(self, username):
        result = self.table.query(KeyConditionExpression=(Key("username").eq(username)))
        if len(result.get("Items", [])) > 0:
            profile = result["Items"][0]
            self.id = profile["id"]
            self.username = profile["username"]
            self.surname = profile["surname"]
            self.givenname = profile["given_name"]
            self.age = profile["age"]
            self.location = profile["location"]
            self.address = profile["address"]
            self.favorite_location_img = profile["favorite_location_img"]
            self.favorite_location_url = profile["favorite_location_url"]
            return profile
        else:
            return {}

    @property
    def fake(self):
        f = Faker()
        p = f.profile()
        profile = {}
        profile["id"] = uuid.uuid4().hex
        profile["username"] = p["username"]
        profile["surname"] = p["name"].split(" ")[1]
        profile["given_name"] = p["name"].split(" ")[0]
        profile["age"] = random.randrange(16, 99)
        profile["location"] = f.city()
        profile["address"] = p["residence"]
        profile["favorite_location_img"] = get_random_photo()
        profile["favorite_location_url"] = "https://www.google.com"

        if self.adversary:
            profile["favorite_location_img"] = get_random_cat()
            profile["ssn"] = f.ssn()
            profile["credit_card"] = f.credit_card_full()
        else:
            self.favorite_location_img = profile["favorite_location_img"]

        self.id = profile["id"]
        self.username = profile["username"]
        self.surname = profile["surname"]
        self.given_name = profile["given_name"]
        self.age = profile["age"]
        self.location = profile["location"]
        self.address = profile["address"]
        self.favorite_location_url = profile["favorite_location_url"]

        return profile

    def all(self):
        results = self.table.scan(Limit=100, Select="ALL_ATTRIBUTES").get("Items", [])
        if self.adversary:
            for result in results:
                result["favorite_location_img"] = get_random_cat()
        return results


def get_random_photo():
    return random.choice(os.listdir("static/dogs"))  # change dir name to whatever


def get_random_cat():
    return "http://placekitten.com/g/200/300"


def seed(table):
    u = User(table=table)
    resp = u.all()
    if len(resp) == 0:
        p = u.fake
        u.id = uuid.uuid4().hex
        u.username = "liebogusp"
        u.surname = "liebogus"
        u.givenname = "pablo"
        u.create()
        for x in range(0, 100):
            p = u.fake
            u.id = uuid.uuid4().hex
            u.create()
            log.info(f"Fake user created.")
    return True
