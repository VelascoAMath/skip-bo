import dataclasses
import json
import secrets
import sqlite3
import uuid
from configparser import ConfigParser
from typing import ClassVar, Self

import psycopg2

from add_db_functions import add_db_functions


@add_db_functions(db_name='public.user', unique_indices=[("name",)])
@dataclasses.dataclass(order=True)
class User:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    name: str = ""
    token: str = dataclasses.field(default_factory=lambda: secrets.token_hex(16))
    cur: ClassVar[sqlite3.Cursor] = None

    def toJSON(self):
        return json.dumps(self.to_json_dict())

    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "token": self.token,
        }

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return User.from_json_dict(data)

    @staticmethod
    def from_json_dict(data):
        return User(
            uuid.UUID(data["id"]),
            data["name"],
            data["token"],
        )

    @classmethod
    def exists_by_name(cls, name: str) -> bool:
        pass

    @classmethod
    def set_cursor(cls, cur: psycopg2.extensions.cursor):
        pass

    @classmethod
    def all(cls) -> list[Self]:
        pass

    @classmethod
    def get_by_id(cls, user_id: uuid.UUID | str) -> Self:
        pass
    
    def save(self) -> None:
        pass
    
    @classmethod
    def get_by_name(cls, name: str) -> Self:
        pass


def main():
    u = User(
        uuid.uuid4(),
        "Alfredo",
        "secret token",
    )

    # print(u)
    # print(u.toJSON())
    # print(User.from_json(u.toJSON()))
    # print(u == User.from_json(u.toJSON()))
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))

    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS public.user (
            id uuid NOT NULL,
            name text NOT NULL,
            "token" text NOT NULL,
            CONSTRAINT user_pk PRIMARY KEY (id)
            );"""
        )
        cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS user_name_idx ON public.user (name);')
        conn.commit()

        User.set_cursor(cur)

        if User.exists_by_name("Alfredo"):
            u = User.get_by_name("Alfredo")
            u.save()
        else:
            u = User(name="Alfredo")
            # print(u)
            u.save()
            u.save()
        u2 = User.get_by_id(u.id)
        # print(u2)
        # print(u == u2)
        u2 = User.get_by_name("Alfredo")
        print(u2)
        print(u == u2)


if __name__ == "__main__":
    main()
