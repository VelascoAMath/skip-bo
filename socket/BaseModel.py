import datetime
import uuid
from configparser import ConfigParser

import peewee

parser = ConfigParser()
# Use this one when testing
# parser.read('database_test.ini')
parser.read("database.ini")
postgres_args = dict(parser.items("postgresql"))
db = peewee.PostgresqlDatabase(**postgres_args)


class BaseModel(peewee.Model):
    id: uuid.UUID | peewee.UUIDField = peewee.UUIDField(primary_key=True, default=lambda: uuid.uuid4())
    created_at: datetime.datetime | peewee.DateTimeField(null=False, default=lambda: datetime.datetime.now())
    updated_at: datetime.datetime | peewee.DateTimeField(null=False, default=lambda: datetime.datetime.now())
    
    def update_time(self):
        self.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
    
    def save_and_update_time(self, force_insert=False, *args, **kwargs):
        self.update_time()
        self.save(force_insert=force_insert, *args, **kwargs)
    
    class Meta:
        database = db


