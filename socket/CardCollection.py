import json
import random
from typing import Self

from Card import Card, Color, Rank


class CardCollection(list):
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return [x.toJSONDict() for x in self]
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return CardCollection.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return CardCollection([Card.fromJSONDict(card) for card in data])
    
    @staticmethod
    def getNewDeck() -> Self:
        deck = CardCollection()
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


def main():
    deck = CardCollection(CardCollection.getNewDeck())
    
    print(deck)
    print(deck == CardCollection.from_json(deck.to_json()))
    
    random.shuffle(deck)
    print([str(x) for x in deck])
    deck.sort(key=lambda x: x.color.value)
    print([str(x) for x in deck])


# print(CardCollection.exists(deck.id))

# print(deck.all())

# print(CardCollection.get_by_id(deck.id))


# print(deck)
#
# print(deck == from_json(deck.toJSON()))


if __name__ == '__main__':
    main()
