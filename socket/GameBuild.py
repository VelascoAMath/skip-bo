import dataclasses
import json
import uuid
from configparser import ConfigParser
from typing import ClassVar, Self

import psycopg2

from Card import Card, Rank, get_num_ranks
from CardCollection import CardCollection
from Game import Game
from Player import Player
from User import User
from add_db_functions import add_db_functions


@add_db_functions(db_name='public.gamebuild', plural_foreign=[('game_id', 'game', Game)], serial_set=set(['sort_key']))
@dataclasses.dataclass(order=True)
class GameBuild:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    game_id: uuid.UUID = None
    deck: CardCollection = dataclasses.field(default_factory=CardCollection)
    
    sort_key: int = 0
    
    cur: ClassVar[psycopg2.extensions.cursor] = None
    
    def can_add_card(self, card: Card) -> bool:
        return self.can_add_cards([card])
    
    def can_add_cards(self, card_list: list[Card]) -> bool:
        
        if len(card_list) == 0:
            return True
        
        expected_rank = get_num_ranks()[len(self.deck)]
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
            "game_id": str(self.game_id),
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
            game_id=uuid.UUID(data["game_id"]),
            deck=CardCollection.from_json_dict(data["deck"]),
            sort_key=data["sort_key"]
        )
    
    @classmethod
    def set_cursor(cls, cur: psycopg2.extensions.cursor) -> None:
        pass
    
    @classmethod
    def get_by_id(cls, build_id: str | uuid.UUID) -> Self:
        pass
    
    @classmethod
    def all_where_game_id(cls, id: str | uuid.UUID) -> list[Self]:
        pass
    
    def save(self) -> None:
        pass


def main():
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.gamebuild (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            deck json NOT NULL,
            sort_key serial NOT NULL,
            CONSTRAINT gamebuild_pk PRIMARY KEY (id),
            CONSTRAINT gamebuild_game_fk FOREIGN KEY (game_id) REFERENCES public.game(id) ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS gamebuild_sort_key_idx ON public.gamebuild (sort_key);
        """)
        conn.commit()
        
        User.set_cursor(cur)
        Game.set_cursor(cur)
        Player.set_cursor(cur)
        GameBuild.set_cursor(cur)
        
        if User.exists_by_name("Alfredo"):
            alfredo = User.get_by_name("Alfredo")
        else:
            alfredo = User(name="Alfredo")
            alfredo.save()
        
        if User.exists_by_name("Naly"):
            naly = User.get_by_name("Naly")
        else:
            naly = User(name="Naly")
            naly.save()
        
        deck = CardCollection()
        discard = CardCollection()
        game = Game(id=uuid.UUID('3e53d560-c0d1-4871-809e-19a087210f43'), deck=deck, discard=discard,
                    owner=alfredo.id,
                    current_user_id=naly.id, winner=alfredo.id)
        game.save()
        
        bp_id_set = set()
        for _ in range(4):
            bp = GameBuild(game_id=game.id, deck=CardCollection())
            bp_id_set.add(bp.id)
            if bp != GameBuild.from_json(bp.to_json()):
                print(bp)
                print(GameBuild.from_json(bp.to_json()))
                raise Exception("JSON conversion is not valid!")
            
            bp.save()
            conn.commit()
            
            if bp.get_game() != game:
                print(game)
                print(bp.get_game())
                raise Exception("Foreign key retrieval operation failed!")
        
        print(GameBuild.all_where_game_id(game.id))
        
        if bp_id_set != set(bp.id for bp in GameBuild.all_where_game_id(game.id)):
            raise Exception("all_where_game_id doesn't return the correct build piles!")
        
        conn.commit()
        if Player.exists_by_game_id_user_id(str(game.id), str(alfredo.id)):
            p = Player.get_by_game_id_user_id(str(game.id), str(alfredo.id))
        else:
            hand = CardCollection()
            
            stock = CardCollection()
            
            p = Player(game_id=game.id, user_id=alfredo.id, hand=hand, stock=stock)
            p.save()
        
        if Player.exists_by_game_id_user_id(str(game.id), str(naly.id)):
            p2 = Player.get_by_game_id_user_id(str(game.id), str(naly.id))
        else:
            hand2 = CardCollection()
            
            stock2 = CardCollection()
            
            p2 = Player(game_id=game.id, user_id=naly.id, hand=hand2, stock=stock2)
            p2.save()
        
        conn.commit()
        
        print(dir(GameBuild))
        game.delete()
        
        conn.commit()


if __name__ == "__main__":
    main()
