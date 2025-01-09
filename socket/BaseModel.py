import datetime
import uuid
from configparser import ConfigParser

import peewee

from CardCollection import CardCollection

parser = ConfigParser()
# Use this one when testing
# parser.read('database_test.ini')
parser.read("database.ini")
postgres_args = dict(parser.items("postgresql"))
db = peewee.PostgresqlDatabase(**postgres_args)

# Create sequence for player turns
db.execute_sql(
    """
create sequence if not exists gamebuild_sort_key_seq AS integer;
create sequence if not exists player_turn_index_seq AS integer;
create sequence if not exists playerdiscard_sort_key_seq AS integer;
"""
)


class CardListField(peewee.Field):
    field_type = "json"
    
    def db_value(self, value: CardCollection) -> str:
        return value.to_json()
    
    def python_value(self, value: list[dict[str:str]]) -> CardCollection:
        return CardCollection.from_json_dict(value)


class BaseModel(peewee.Model):
    id: uuid.UUID | peewee.UUIDField = peewee.UUIDField(primary_key=True, default=lambda: uuid.uuid4())
    created_at: datetime.datetime | peewee.DateTimeField(null=False, default=lambda: datetime.datetime.now())
    updated_at: datetime.datetime | peewee.DateTimeField(null=False, default=lambda: datetime.datetime.now())
    
    @classmethod
    def exists_by_id(cls, id: uuid.UUID | str) -> bool:
        return cls.get_or_none(cls.id == id) is not None
    
    def update_time(self):
        self.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
    
    def save_and_update_time(self, force_insert=False, *args, **kwargs):
        self.update_time()
        self.save(force_insert=force_insert, *args, **kwargs)
    
    class Meta:
        database = db
