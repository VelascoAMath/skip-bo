import dataclasses
import json
import secrets
import uuid
from configparser import ConfigParser

import peewee

from BaseModel import BaseModel


@dataclasses.dataclass(init=False, order=True)
class User(BaseModel):
    name: str = peewee.TextField(default="", null=False, unique=True)
    display: str = peewee.TextField(default="", null=False)
    token: str = peewee.TextField(default=lambda: secrets.token_hex(16), null=False)
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display": self.display,
            "token": self.token,
        }
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return User.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return User(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            display=data["display"],
            token=data["token"],
        )
    
    class Meta:
        table_name = 'user'
    
    @classmethod
    def exists_by_name(cls, name: str):
        return User.get_or_none(User.name == name) is not None
    
    @classmethod
    def get_by_name(cls, name: str):
        return User.get(User.name == name)


def main():
    parser = ConfigParser()
    parser.read("database.ini")
    postgres_args = dict(parser.items("postgresql"))
    db = peewee.PostgresqlDatabase(**postgres_args)
    db.create_tables([User])
    
    u = User(
        id=uuid.uuid4(),
        name="Alfredo",
        display="Alfredo",
        token="secret token",
    )
    
    # print(u)
    # print(u.toJSON())
    # print(User.from_json(u.toJSON()))
    # print(u == User.from_json(u.toJSON()))
    
    if User.get_or_none(User.name == "Alfredo") is not None:
        u = User.get(User.name == "Alfredo")
        u.save()
    else:
        u = User(name="Alfredo")
        # print(u)
        u.save(force_insert=True)
    
    u2 = User.get_by_id(u.id)
    # print(u2)
    # print(u == u2)
    u2 = User.get(User.name == "Alfredo")
    print(u2)
    print(u == u2)


if __name__ == "__main__":
    main()
