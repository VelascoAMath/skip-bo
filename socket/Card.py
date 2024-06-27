import dataclasses
import json
import random
import re
import uuid
from enum import Enum


@dataclasses.dataclass(frozen=True)
class Rank(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    WILD = 13
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __hash__(self):
        return self.value
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        match self.name:
            case "ONE":
                return "1"
            case "TWO":
                return "2"
            case "THREE":
                return "3"
            case "FOUR":
                return "4"
            case "FIVE":
                return "5"
            case "SIX":
                return "6"
            case "SEVEN":
                return "7"
            case "EIGHT":
                return "8"
            case "NINE":
                return "9"
            case "TEN":
                return "10"
            case "ELEVEN":
                return "11"
            case "TWELVE":
                return "12"
            case "WILD":
                return "W"
            case "JACK":
                return "J"
            case "QUEEN":
                return "Q"
            case "KING":
                return "K"
            case _:
                return self.name
    
    @staticmethod
    def fromJSON(data):
        match data:
            case "1":
                return Rank.ONE
            case "2":
                return Rank.TWO
            case "3":
                return Rank.THREE
            case "4":
                return Rank.FOUR
            case "5":
                return Rank.FIVE
            case "6":
                return Rank.SIX
            case "7":
                return Rank.SEVEN
            case "8":
                return Rank.EIGHT
            case "9":
                return Rank.NINE
            case "10":
                return Rank.TEN
            case "11":
                return Rank.ELEVEN
            case "12":
                return Rank.TWELVE
            case "W":
                return Rank.WILD
            
            case _:
                raise Exception(f"{data} is not a valid rank!")


def get_num_ranks() -> list[Rank]:
    return [Rank.fromJSON(str(i)) for i in range(1, len(Rank))]


@dataclasses.dataclass(frozen=True)
class Color(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    WILD = 4
    
    def __hash__(self):
        return self.value
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        match self.name:
            case "RED":
                return "R"
            case "BLUE":
                return "B"
            case "GREEN":
                return "G"
            case "YELLOW":
                return "Y"
            case "WILD":
                return "W"
            case _:
                return self.name
    
    @staticmethod
    def fromJSON(data):
        match data:
            case "R":
                return Color.RED
            case "G":
                return Color.GREEN
            case "Y":
                return Color.YELLOW
            case "B":
                return Color.BLUE
            case "W":
                return Color.WILD
            case _:
                raise Exception(f"{data} is not a valid color!")


@dataclasses.dataclass(frozen=True)
class Card:
    color: Color = dataclasses.field(default_factory=lambda: Color.WILD)
    rank: Rank = dataclasses.field(default_factory=lambda: Rank.WILD)
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    
    def __post_init__(self):
        if self.color is Color.WILD and self.rank is not Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )
        
        if self.color is not Color.WILD and self.rank is Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )
    
    @staticmethod
    def getNewDeck():
        deck = []
        for color in Color:
            if color is Color.WILD:
                continue
            for rank in Rank:
                if rank is Rank.WILD:
                    continue
                deck.append(Card(color, rank))
                deck.append(Card(color, rank))
                deck.append(Card(color, rank))
        
        for _ in range(18):
            deck.append(Card(Color.WILD, Rank.WILD))
        return deck
    
    def __lt__(self, other):
        if isinstance(other, Card):
            return (self.color.value, self.rank.value) < (other.color.value, other.rank.value)
        else:
            raise Exception(f"'<' not supported between instances of 'Card' and '{type(other)}'")
    
    def __hash__(self):
        return self.rank.value * len(Rank) + self.color.value
    
    def __str__(self):
        if self.color is Color.WILD and self.rank is Rank.WILD:
            return "W"
        
        return f"{self.color}{self.rank}"
    
    def toJSON(self):
        return json.dumps(self.toJSONDict())
    
    def toJSONDict(self) -> dict:
        return {"color": str(self.color), "rank": str(self.rank), "id": str(self.id)}
    
    @staticmethod
    def fromJSON(data: str):
        data = json.loads(data)
        
        return Card.fromJSONDict(data)
    
    @staticmethod
    def fromJSONDict(data: dict):
        return Card(Color.fromJSON(data["color"]), Rank.fromJSON(data["rank"]), uuid.UUID(data["id"]))
    
    @staticmethod
    def from_string(data):
        # Cards like R9, G8, B2, etc.
        m = re.fullmatch("([RGYB])([0-9])", data)
        if m:
            return Card(Color.fromJSON(m.group(1)), Rank.fromJSON(m.group(2)))
        
        # Cards with rank 10
        m = re.fullmatch("([RGYB])(1[012])", data)
        if m:
            return Card(Color.fromJSON(m.group(1)), Rank.fromJSON(m.group(2)))
        
        match data:
            case "W":
                return Card(Color.WILD, Rank.WILD)
            case "_":
                raise Exception(f"{data} is not a valid card!")


def main():
    for rank in Rank:
        for color in Color:
            if rank is Rank.WILD and color is not Color.WILD:
                continue
            if color is Color.WILD and rank is not Rank.WILD:
                continue
            c = Card(color, rank)
            print(c)
            print(c.toJSON())
            print(Card.fromJSON(c.toJSON()))
            print(c == Card.fromJSON(c.toJSON()))
            print(Card.from_string(str(c)))
            print()
    
    deck = Card.getNewDeck()
    random.shuffle(deck)
    print([str(x) for x in deck])
    deck.sort(key=lambda x: x.color.value)
    print([str(x) for x in deck])


if __name__ == "__main__":
    main()
