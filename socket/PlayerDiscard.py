import dataclasses
import json
import uuid
from configparser import ConfigParser
from typing import ClassVar, Self

import psycopg2.extensions

from CardCollection import CardCollection
from Game import Game
from Player import Player
from User import User
from add_db_functions import add_db_functions


@add_db_functions(db_name='public.playerdiscard', plural_foreign=[('player_id', 'player', Player)], serial_set={
    'sort_key'})
@dataclasses.dataclass(order=True)
class PlayerDiscard:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    player_id: uuid.UUID = None
    deck: CardCollection = dataclasses.field(default_factory=CardCollection)
    sort_key: int = 0
    
    cur: ClassVar[psycopg2.extensions.cursor] = None
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "player_id": str(self.player_id),
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
            player_id=uuid.UUID(data["player_id"]),
            deck=CardCollection.from_json_dict(data["deck"]),
            sort_key=data["sort_key"],
        )
    
    @classmethod
    def all_where_player_id(cls, id:str | uuid.UUID) -> list[Self]:
        pass
    
    @classmethod
    def set_cursor(cls, cur: psycopg2.extensions.cursor) -> None:
        pass

    def save(self) -> None:
        pass
    
    @classmethod
    def get_by_id(cls, discard_id: str | uuid.UUID) -> Self:
        pass


def main():
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.playerdiscard (
            id uuid NOT NULL,
            player_id uuid NOT NULL,
            deck json NOT NULL,
            sort_key serial NOT NULL,
            CONSTRAINT playerdiscard_pk PRIMARY KEY (id),
            CONSTRAINT playerdiscard_player_fk FOREIGN KEY (player_id) REFERENCES public.player(id) ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS playerdiscard_sort_key_idx ON public.playerdiscard (sort_key);
        """)
        conn.commit()
        
        User.set_cursor(cur)
        Game.set_cursor(cur)
        Player.set_cursor(cur)
        PlayerDiscard.set_cursor(cur)
        
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
        
        game = Game(deck=deck, discard=discard, owner=alfredo.id, current_user_id=naly.id
                    , winner=alfredo.id)
        game.save()
        
        hand = CardCollection()
        stock = CardCollection()
        
        conn.commit()
        
        p = Player(game_id=game.id, user_id=alfredo.id, hand=hand, stock=stock)
        p.save()
        
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
        
        conn.commit()
        
        print(p2)
        print(p2 == pd.get_player())
        print(pd.get_player())
        print(PlayerDiscard.all_where_player_id(p2.id))
        p.delete()
        p2.delete()
        game.delete()
        conn.commit()


if __name__ == "__main__":
    main()
