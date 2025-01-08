import dataclasses
import json
import random
import uuid
from configparser import ConfigParser

import peewee

from BaseModel import BaseModel, CardListField
from Card import Card
from CardCollection import CardCollection
from User import User


@dataclasses.dataclass(order=True, init=False)
class Game(BaseModel):
    # Reference CardCollection
    deck: CardCollection | CardListField = CardListField(null=False, default=lambda: CardCollection())
    discard: CardCollection | CardListField = CardListField(null=False, default=lambda: CardCollection())
    # Reference User
    current_user: User | peewee.ForeignKeyField = peewee.ForeignKeyField(
        column_name="current_user", field="id", model=User
    )
    
    # The player who originally created the game
    host: User | peewee.ForeignKeyField = peewee.ForeignKeyField(backref='user_host_set', column_name='host',
                                                                 field='id', model=User)
    
    # If the game has started
    in_progress: bool | peewee.BooleanField = peewee.BooleanField(null=False, default=False)
    # References User
    winner: User | peewee.ForeignKeyField = peewee.ForeignKeyField(backref='user_winner_set', column_name='winner',
                                                                   field='id', model=User, null=True)
    
    def to_json_dict(self):
        result = {
            "id": str(self.id),
            "deck": self.deck.to_json_dict(),
            "discard": self.discard.to_json_dict(),
            "in_progress": self.in_progress,
        }
        if self.current_user is not None:
            result["current_user_id"] = str(self.current_user.id)
        if self.host is not None:
            result["host"] = str(self.host.id)
        if self.winner is not None:
            result["winner"] = str(self.winner.id)
        
        return result
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Game.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return Game(id=uuid.UUID(data["id"]), deck=CardCollection.from_json_dict(data["deck"]),
                    discard=CardCollection.from_json_dict(data["discard"]),
                    current_user_id=User.get_by_id(data["current_user_id"]),
                    host=User.get_by_id(data["host"]), in_progress=data["in_progress"],
                    winner=User.get_by_id(data["winner"]) if "winner" in data is not None else None)


def main():
    parser = ConfigParser()
    parser.read("database.ini")
    postgres_args = dict(parser.items("postgresql"))
    db = peewee.PostgresqlDatabase(**postgres_args)
    db.create_tables([Game, User])
    
    deck = CardCollection(Card.getNewDeck())
    
    random.seed(0)
    random.shuffle(deck)
    deck.sort()
    
    discard = CardCollection([deck.pop(0) for _ in range(12)])
    
    if User.exists_by_name("Alfredo"):
        alfredo = User.get_by_name("Alfredo")
    else:
        alfredo = User(name="Alfredo")
        alfredo.save(force_insert=True)
    
    g = Game(deck=deck, discard=discard, host=alfredo, current_user=alfredo, in_progress=True)
    g.save(force_insert=True)
    h = Game.from_json(g.toJSON())
    print(g == h)
    
    if User.exists_by_name("Naly"):
        naly = User.get_by_name("Naly")
    else:
        naly = User(name="Naly")
        naly.save(force_insert=True)
    
    print(alfredo)
    print(naly)
    g = Game(id=uuid.uuid4(), deck=deck, discard=discard, current_user_id=naly.id, host=alfredo.id,
             in_progress=True, winner=None)
    
    print(g)
    g.save()
    
    print(g == Game.from_json(g.toJSON()))
    
    # p1 = Player(game_id=g.id, user_id=alfredo.id, hand=CardCollection(), stock=CardCollection(), turn_index=0)
    # p2 = Player(game_id=g.id, user_id=naly.id, hand=CardCollection(), stock=CardCollection(), turn_index=1)
    # p1.save()
    # p2.save()
    
    g.delete()
    # p1.delete()
    # p2.delete()


if __name__ == "__main__":
    main()
