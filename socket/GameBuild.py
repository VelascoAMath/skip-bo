import dataclasses
import json
import uuid
from configparser import ConfigParser

import peewee
from peewee import ForeignKeyField, IntegerField, SQL

from BaseModel import BaseModel, CardListField
from Card import Card, Rank, get_num_ranks
from CardCollection import CardCollection
from Game import Game
from User import User


@dataclasses.dataclass(order=True, init=False)
class GameBuild(BaseModel):
    game: Game | ForeignKeyField = ForeignKeyField(column_name='game_id', field='id', model=Game)
    deck: CardCollection | CardListField = CardListField(default=lambda: CardCollection(), null=False)
    sort_key: int | IntegerField = IntegerField(
        constraints=[SQL("DEFAULT nextval('gamebuild_sort_key_seq'::regclass)")], unique=True)
    
    def can_add_card(self, card: Card) -> bool:
        return self.can_add_cards([card])
    
    def can_add_cards(self, card_list: list[Card]) -> bool:
        
        if len(card_list) == 0:
            return True
        
        expected_index = len(self.deck) % len(get_num_ranks())
        
        for card in card_list:
            
            expected_rank = get_num_ranks()[expected_index]
            
            if card.rank is not Rank.WILD and card.rank is not expected_rank:
                return False
            
            expected_index += 1
            expected_index %= len(get_num_ranks())
        
        return True
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "game_id": str(self.game.id),
            "deck": self.deck.to_json_dict(),
            "sort_key": self.sort_key,
        }
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return GameBuild.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return GameBuild(
            id=uuid.UUID(data["id"]),
            game=Game.get_by_id(data["game_id"]),
            deck=CardCollection.from_json_dict(data["deck"]),
            sort_key=data["sort_key"]
        )
    
    class Meta:
        table_name = 'player'


def main():
    parser = ConfigParser()
    parser.read("database.ini")
    postgres_args = dict(parser.items("postgresql"))
    db = peewee.PostgresqlDatabase(**postgres_args)
    db.create_tables([User, Game])
    db.create_tables([GameBuild])
    
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
    game = Game(deck=deck, discard=discard,
                host=alfredo,
                current_user=naly, winner=alfredo)
    game.save(force_insert=True)
    
    bp_id_set = set()
    for _ in range(4):
        bp = GameBuild(game=game, deck=CardCollection())
        bp_id_set.add(bp.id)
        if bp != GameBuild.from_json(bp.to_json()):
            print(bp)
            print(GameBuild.from_json(bp.to_json()))
            raise Exception("JSON conversion is not valid!")
        
        bp.save()
    
    # if Player.exists_by_game_id_user_id(str(game.id), str(alfredo.id)):
    #     p = Player.get_by_game_id_user_id(str(game.id), str(alfredo.id))
    # else:
    #     hand = CardCollection()
    #
    #     stock = CardCollection()
    #
    #     p = Player(game_id=game.id, user_id=alfredo.id, hand=hand, stock=stock)
    #     p.save()
    
    # if Player.exists_by_game_id_user_id(str(game.id), str(naly.id)):
    #     p2 = Player.get_by_game_id_user_id(str(game.id), str(naly.id))
    # else:
    #     hand2 = CardCollection()
    #
    #     stock2 = CardCollection()
    #
    #     p2 = Player(game_id=game.id, user_id=naly.id, hand=hand2, stock=stock2)
    #     p2.save()
    #
    game.delete()


if __name__ == "__main__":
    main()
