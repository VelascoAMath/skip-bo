import json

from Card import Card


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


def main():
    deck = CardCollection(Card.getNewDeck())

    print(deck)
    print(deck == CardCollection.from_json(deck.to_json()))


# print(CardCollection.exists(deck.id))

# print(deck.all())

# print(CardCollection.get_by_id(deck.id))


# print(deck)
#
# print(deck == from_json(deck.toJSON()))


if __name__ == '__main__':
    main()
