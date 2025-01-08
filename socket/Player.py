import dataclasses
import json
import uuid
from configparser import ConfigParser
from typing import Self

import peewee
from peewee import ForeignKeyField, IntegerField, BooleanField, SQL

from BaseModel import CardListField, BaseModel
from CardCollection import CardCollection
from Game import Game
from User import User


@dataclasses.dataclass(order=True, init=False)
class Player(BaseModel):
    game: Game | ForeignKeyField = ForeignKeyField(column_name='game_id', field='id', model=Game)
    user: User | ForeignKeyField = ForeignKeyField(column_name='user_id', field='id', model=User)
    hand: CardCollection | CardListField = CardListField()
    stock: CardCollection | CardListField = CardListField()
    turn_index: int | IntegerField = IntegerField(
        constraints=[SQL("DEFAULT nextval('player_turn_index_seq'::regclass)")])
    took_action: bool | BooleanField = BooleanField(default=False)
    did_discard: bool | BooleanField = BooleanField(default=False)
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "game_id": str(self.game.id),
            "user_id": str(self.user.id),
            "hand": self.hand.to_json_dict(),
            "stock": self.stock.to_json_dict(),
            "turn_index": self.turn_index,
            "took_action": self.took_action,
            "did_discard": self.did_discard,
        }
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Player.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return Player(
            id=uuid.UUID(data["id"]),
            game=Game.get_by_id(data["game_id"]),
            user=User.get_by_id(data["user_id"]),
            hand=CardCollection.from_json_dict(data["hand"]),
            stock=CardCollection.from_json_dict(data["stock"]),
            turn_index=data["turn_index"],
            took_action=data["took_action"],
            did_discard=data["did_discard"],
        )
    
    @classmethod
    def get_by_game_id_user_id(cls, id: uuid.UUID | str, id1: uuid.UUID | str) -> Self:
        pass
    
    @classmethod
    def exists_by_game_id_user_id(cls, id: uuid.UUID | str, id1: uuid.UUID | str) -> bool:
        pass
    
    class Meta:
        table_name = 'player'
        indexes = (
            (('game', 'user'), True),
            (('turn_index', 'game'), True),
        )


def main():
    parser = ConfigParser()
    parser.read("database.ini")
    postgres_args = dict(parser.items("postgresql"))
    db = peewee.PostgresqlDatabase(**postgres_args)
    
    db.create_tables([User, Game, Player])
    
    if User.exists_by_name("Alfredo"):
        alfredo = User.get_by_name("Alfredo")
    else:
        alfredo = User(name="Alfredo")
        alfredo.save(force_insert=True)
    
    if User.exists_by_name("Naly"):
        naly = User.get_by_name("Naly")
    else:
        naly = User(name="Naly")
        naly.save(force_insert=True)
    
    deck = CardCollection()
    discard = CardCollection()
    
    game = Game(deck=deck, discard=discard, host=alfredo.id, current_user_id=naly.id,
                winner=alfredo.id)
    game.save(force_insert=True)
    
    hand = CardCollection()
    stock = CardCollection()
    
    p = Player(game=game, user=alfredo, hand=hand, stock=stock)
    p.save()
    
    if p != Player.from_json(p.to_json()):
        print(f"{p=}")
        print(f"{Player.from_json(p.to_json())}")
        raise Exception(f"JSON conversion isn't valid!")
    
    hand2 = CardCollection()
    
    stock2 = CardCollection()
    
    p2 = Player(game=game, user=naly, hand=hand2, stock=stock2)
    p2.save()
    
    game.delete()
    p.delete()
    p2.delete()


if __name__ == "__main__":
    main()
