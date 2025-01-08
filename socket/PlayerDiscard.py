import dataclasses
import json
import uuid
from configparser import ConfigParser

import peewee
from peewee import ForeignKeyField, IntegerField, SQL

from BaseModel import CardListField, BaseModel
from CardCollection import CardCollection
from Game import Game
from Player import Player
from User import User


@dataclasses.dataclass(order=True, init=False)
class PlayerDiscard(BaseModel):
    player: Player | ForeignKeyField = ForeignKeyField(column_name='player_id', field='id', model=Player)
    deck: CardCollection | CardListField = CardListField()
    sort_key: int | IntegerField = IntegerField(
        constraints=[SQL("DEFAULT nextval('playerdiscard_sort_key_seq'::regclass)")], unique=True)
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "player_id": str(self.player.id),
            "deck": self.deck.to_json_dict(),
            "sort_key": self.sort_key
        }
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return PlayerDiscard.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return PlayerDiscard(
            id=uuid.UUID(data["id"]),
            player=Player.get_by_id(data["player_id"]),
            deck=CardCollection.from_json_dict(data["deck"]),
            sort_key=data["sort_key"],
        )
    
    class Meta:
        table_name = 'playerdiscard'


def main():
    parser = ConfigParser()
    parser.read("database.ini")
    postgres_args = dict(parser.items("postgresql"))
    db = peewee.PostgresqlDatabase(**postgres_args)
    
    db.create_tables([User, Game, Player, PlayerDiscard])
    
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
    
    game = Game(deck=deck, discard=discard, host=alfredo.id, current_user_id=naly.id
                , winner=alfredo.id)
    game.save(force_insert=True)
    
    hand = CardCollection()
    stock = CardCollection()
    
    p = Player(game_id=game.id, user_id=alfredo.id, hand=hand, stock=stock)
    p.save(force_insert=True)
    
    hand2 = CardCollection()
    stock2 = CardCollection()
    
    p2 = Player(game_id=game.id, user_id=naly.id, hand=hand2, stock=stock2)
    p2.save()
    
    for _ in range(4):
        player_discard = CardCollection()
        pd = PlayerDiscard(deck=player_discard, player_id=p.id)
        if pd != PlayerDiscard.from_json(pd.to_json()):
            print(pd)
            print(PlayerDiscard.from_json(pd.to_json()))
            raise Exception("JSON conversion is not valid!")
        pd.save()
        
        player_discard2 = CardCollection()
        pd = PlayerDiscard(deck=player_discard2, player_id=p2.id)
        pd.save()
    
    print(p2)
    p.delete()
    p2.delete()
    game.delete()


if __name__ == "__main__":
    main()
