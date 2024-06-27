import dataclasses
import json
import random
import uuid
from configparser import ConfigParser
from typing import ClassVar, Self

import psycopg2.extensions

from Card import Card
from CardCollection import CardCollection
from User import User
from add_db_functions import add_db_functions


@add_db_functions(db_name='public.game')
@dataclasses.dataclass(order=True)
class Game:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    # Reference CardCollection
    deck: CardCollection = dataclasses.field(default_factory=CardCollection)
    discard: CardCollection = dataclasses.field(default_factory=CardCollection)
    # Reference User
    current_user_id: uuid.UUID = None
    # The player who originally created the game
    owner: uuid.UUID = None
    # If the game has started
    in_progress: bool = False
    # References User
    winner: uuid.UUID | None = None
    cur: ClassVar[psycopg2.extensions.cursor] = None
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "deck": self.deck.to_json_dict(),
            "discard": self.discard.to_json_dict(),
            "current_user_id": str(self.current_user_id),
            "owner": str(self.owner),
            "in_progress": self.in_progress,
            "winner": str(self.winner) if self.winner is not None else None,
        }
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Game.fromJSONDict(data)
    
    @staticmethod
    def from_json_dict(data):
        return Game(id=uuid.UUID(data["id"]), deck=CardCollection.from_json_dict(data["deck"]),
                    discard=CardCollection.from_json_dict(data["discard"]),
                    current_user_id=uuid.UUID(data["current_user_id"]),
                    owner=uuid.UUID(data["owner"]), in_progress=data["in_progress"],
                    winner=uuid.UUID(data["winner"]) if data["winner"] is not None else None)
    
    @classmethod
    def get_by_id(cls, id: str|uuid.UUID) -> Self:
        pass

    @classmethod
    def all(cls) -> list[Self]:
        pass
    
    @classmethod
    def set_cursor(cls, cur:psycopg2.extensions.cursor) -> None:
        pass
    
    def save(self) -> None:
        pass

    def delete(self) -> None:
        pass


def main():
    deck = CardCollection(Card.getNewDeck())
    
    random.seed(0)
    random.shuffle(deck)
    deck.sort()
    
    discard = CardCollection([deck.pop(0) for _ in range(12)])
    
    g = Game(id=uuid.uuid4(), deck=deck, discard=discard, current_user_id=uuid.uuid4(),
             owner=uuid.uuid4(), in_progress=True, winner=uuid.uuid4())
    h = Game.fromJSON(g.toJSON())
    print(g == h)
    
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.game (
        id uuid NOT NULL,
        deck json NOT NULL,
        discard json NOT NULL,
        current_user_id uuid NOT NULL,
        "owner" uuid NOT NULL,
        in_progress bool DEFAULT FALSE NOT NULL,
        winner uuid NULL,
        CONSTRAINT game_pk PRIMARY KEY (id),
        CONSTRAINT game_user_current_fk FOREIGN KEY (current_user_id) REFERENCES public."user"(id) ON DELETE CASCADE,
        CONSTRAINT game_user_owner_fk FOREIGN KEY ("owner") REFERENCES public."user"(id) ON DELETE CASCADE,
        CONSTRAINT game_user_winner_fk FOREIGN KEY (winner) REFERENCES public."user"(id)
        );
        """)
        
        Game.set_cursor(cur)
        User.set_cursor(cur)
        
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
        
        print(alfredo)
        print(naly)
        g = Game(id=uuid.uuid4(), deck=deck, discard=discard, current_user_id=naly.id, owner=alfredo.id,
                 in_progress=True, winner=None)
        
        print(g)
        g.save()
        conn.commit()
        print(dir(g))
        
        # p1 = Player(game_id=g.id, user_id=alfredo.id, hand=CardCollection(), stock=CardCollection(), turn_index=0)
        # p2 = Player(game_id=g.id, user_id=naly.id, hand=CardCollection(), stock=CardCollection(), turn_index=1)
        # p1.save()
        # p2.save()
        
        g.delete()
        # p1.delete()
        # p2.delete()
        conn.commit()


if __name__ == "__main__":
    main()
