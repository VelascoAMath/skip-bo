import dataclasses
import json
import pprint
import uuid
from configparser import ConfigParser
from typing import ClassVar, Self

import psycopg2

from CardCollection import CardCollection
from Game import Game
from User import User
from add_db_functions import add_db_functions


@add_db_functions(db_name='public.player', unique_indices=[('game_id', 'user_id')],
                  plural_foreign=[('game_id', 'games', Game), ('user_id', 'users', User)],
                  serial_set={'turn_index'})
@dataclasses.dataclass(order=True)
class Player:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    game_id: uuid.UUID = None
    user_id: uuid.UUID = None
    hand: CardCollection = dataclasses.field(default_factory=CardCollection)
    stock: CardCollection = dataclasses.field(default_factory=CardCollection)
    # Does this player go first, second, etc
    turn_index: int = -1
    took_action: bool = False
    did_discard: bool = False
    
    cur: ClassVar[psycopg2.extensions.cursor] = None
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "game_id": str(self.game_id),
            "user_id": str(self.user_id),
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
            game_id=uuid.UUID(data["game_id"]),
            user_id=uuid.UUID(data["user_id"]),
            hand=CardCollection.from_json_dict(data["hand"]),
            stock=CardCollection.from_json_dict(data["stock"]),
            turn_index=data["turn_index"],
            took_action=data["took_action"],
            did_discard=data["did_discard"],
        )
    
    @classmethod
    def get_by_game_id_user_id(cls, id: uuid.UUID|str, id1: uuid.UUID|str) -> Self:
        pass
    
    @classmethod
    def exists_by_game_id_user_id(cls, id: uuid.UUID|str, id1: uuid.UUID|str) -> bool:
        pass

    @classmethod
    def all_where_game_id(cls, id: uuid.UUID | str) -> list[Self]:
        pass
    
    @classmethod
    def set_cursor(cls, cur: psycopg2.extensions.cursor) -> None:
        pass
    
    def save(self) -> None:
        pass
    
    @classmethod
    def get_by_id(cls, player_id: str | uuid.UUID) -> Self:
        pass


def main():
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.player (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            user_id uuid NOT NULL,
            hand json NOT NULL,
            stock json NOT NULL,
            turn_index serial NOT NULL,
            took_action boolean DEFAULT false NOT NULL,
            did_discard bool DEFAULT false NOT NULL,
            CONSTRAINT player_pk PRIMARY KEY (id),
            CONSTRAINT player_game_fk FOREIGN KEY (game_id) REFERENCES public.game(id) ON DELETE CASCADE,
            CONSTRAINT player_user_fk FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS player_game_id_idx ON public.player (game_id,user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS player_turn_index_idx ON public.player (turn_index,game_id);
        CREATE INDEX IF NOT EXISTS player_game_id_idx ON public.player (game_id);
        CREATE INDEX IF NOT EXISTS player_user_id_idx ON public.player (user_id);
        """)
        conn.commit()
        
        User.set_cursor(cur)
        Game.set_cursor(cur)
        Player.set_cursor(cur)
        
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
        
        game = Game(deck=deck, discard=discard, owner=alfredo.id, current_user_id=naly.id,
                    winner=alfredo.id)
        game.save()
        
        hand = CardCollection()
        stock = CardCollection()
        
        conn.commit()
        
        p = Player(game_id=game.id, user_id=alfredo.id, hand=hand, stock=stock)
        p.save()
        
        if p != Player.from_json(p.to_json()):
            print(f"{p=}")
            print(f"{Player.from_json(p.to_json())}")
            raise Exception(f"JSON conversion isn't valid!")
        
        hand2 = CardCollection()
        
        stock2 = CardCollection()
        
        p2 = Player(game_id=game.id, user_id=naly.id, hand=hand2, stock=stock2)
        p2.save()

        pprint.pprint(Player.get_games(game.id))
        pprint.pprint(Player.get_users(alfredo.id))

        game.delete()
        p.delete()
        p2.delete()
        
        conn.commit()


if __name__ == "__main__":
    main()
