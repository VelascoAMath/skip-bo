from Card import Color, Rank, Card
from GameBuild import GameBuild


def test_can_add_card():
    gb = GameBuild()
    
    for color in Color:
        if color is Color.WILD:
            continue
        assert gb.can_add_card(Card(color=color, rank=Rank.ONE))
        assert gb.can_add_card(Card(color=Color.WILD, rank=Rank.WILD))
        assert not gb.can_add_card(Card(color=color, rank=Rank.TWO))
    
    gb.deck.append(Card(color=Color.RED, rank=Rank.ONE))
    gb.deck.append(Card(color=Color.RED, rank=Rank.TWO))
    gb.deck.append(Card(color=Color.WILD, rank=Rank.WILD))
    
    for color in Color:
        if color is Color.WILD:
            continue
        assert gb.can_add_card(Card(color=color, rank=Rank.FOUR))
        assert gb.can_add_card(Card(color=Color.WILD, rank=Rank.WILD))
        assert not gb.can_add_card(Card(color=color, rank=Rank.FIVE))
        assert not gb.can_add_card(Card(color=color, rank=Rank.THREE))
    
    gb.deck.append(Card(color=Color.WILD, rank=Rank.WILD))
    gb.deck.append(Card(color=Color.RED, rank=Rank.FIVE))
    gb.deck.append(Card(color=Color.BLUE, rank=Rank.SIX))
    
    for color in Color:
        if color is Color.WILD:
            continue
        assert gb.can_add_card(Card(color=color, rank=Rank.SEVEN))
        assert gb.can_add_card(Card(color=Color.WILD, rank=Rank.WILD))
        assert not gb.can_add_card(Card(color=color, rank=Rank.SIX))
        assert not gb.can_add_card(Card(color=color, rank=Rank.EIGHT))
    
    gb.deck.append(Card(color=Color.WILD, rank=Rank.WILD))
    gb.deck.append(Card(color=Color.RED, rank=Rank.EIGHT))
    gb.deck.append(Card(color=Color.BLUE, rank=Rank.NINE))
    gb.deck.append(Card(color=Color.WILD, rank=Rank.WILD))
    gb.deck.append(Card(color=Color.RED, rank=Rank.ELEVEN))
    assert gb.can_add_cards(Card(color=Color.YELLOW, rank=Rank.TWELVE))

    gb.deck.append(Card(color=Color.BLUE, rank=Rank.TWELVE))
    
    for color in Color:
        if color is Color.WILD:
            continue
        assert gb.can_add_card(Card(color=color, rank=Rank.ONE))
        assert gb.can_add_card(Card(color=Color.WILD, rank=Rank.WILD))
        assert not gb.can_add_card(Card(color=color, rank=Rank.TWO))
        assert not gb.can_add_card(Card(color=color, rank=Rank.TWELVE))
    
    gb.deck.pop()
    gb.deck.append(Card(color=Color.WILD, rank=Rank.WILD))
    
    for color in Color:
        if color is Color.WILD:
            continue
        assert gb.can_add_card(Card(color=color, rank=Rank.ONE))
        assert gb.can_add_card(Card(color=Color.WILD, rank=Rank.WILD))
        assert not gb.can_add_card(Card(color=color, rank=Rank.TWO))
        assert not gb.can_add_card(Card(color=color, rank=Rank.TWELVE))


def test_can_add_cards():
    gb = GameBuild()
    
    assert gb.can_add_cards([Card.from_string(x) for x in ["R1", "R2", "R3"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "R2", "R3"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "W", "W"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["W", "R3", "R4"]])
    
    for card in [Card.from_string(x) for x in "R1".split(" ")]:
        gb.deck.append(card)
    
    assert gb.can_add_cards([Card.from_string(x) for x in ["R2", "R3", "R4"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "R3", "R4"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "W", "W"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["W", "R5", "R6"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["R4", "R5", "R6"]])
    
    for card in [Card.from_string(x) for x in "R2 W".split(" ")]:
        gb.deck.append(card)
    
    assert gb.can_add_cards([Card.from_string(x) for x in ["R4", "R5", "R6"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "R5", "R6"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "W", "W"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["W", "R6", "R7"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["R5", "R6", "R8"]])
    
    for card in [Card.from_string(x) for x in "W W W W W W B10 Y11".split(" ")]:
        gb.deck.append(card)
    
    assert gb.can_add_cards([Card.from_string(x) for x in ["R12", "R1", "R2"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "R1", "R2"]])
    assert gb.can_add_cards([Card.from_string(x) for x in ["W", "W", "W"]])
    assert not gb.can_add_cards([Card.from_string(x) for x in ["W", "R3", "R4"]])
