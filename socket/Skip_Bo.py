import asyncio
import json
import random
import uuid
from collections import defaultdict
from configparser import ConfigParser

import peewee
import websockets
from websockets import serve

from CardCollection import CardCollection
from Game import Game
from GameBuild import GameBuild
from Player import Player
from PlayerDiscard import PlayerDiscard
from User import User

parser = ConfigParser()
parser.read("database.ini")
postgres_args = dict(parser.items("postgresql"))
db = peewee.PostgresqlDatabase(**postgres_args)

db.create_tables([User, Game, Player, PlayerDiscard, GameBuild])

connected = set()
game_id_to_socket = defaultdict(set)

HAND_SIZE = 5
RANK_SIZE = 12


def is_valid_uuid(candidate: str) -> bool:
    try:
        uuid.UUID(candidate)
        return True
    except:
        return False


def create_user(name):
    if User.exists_by_name(name):
        return {"type": "rejection", "message": f"User name {name} already exists!"}
    
    u = User(name=name, display=name)
    u.save(force_insert=True)
    return {"type": "create_user", "user": u.to_json_dict()}


def get_games():
    game_list = []
    for game in Game.select():
        game_json_dict = game.to_json_dict()
        # This call is for the lobby so don't send the actual game state
        del game_json_dict["deck"]
        del game_json_dict["discard"]
        
        # Need to include who is in the game
        player_list = []
        for player in Player.select().where(Player.game == game):
            player_json_dict = player.to_json_dict()
            
            # Already have the game id
            del player_json_dict["game_id"]
            # Don't include the player state
            del player_json_dict["hand"]
            del player_json_dict["stock"]
            del player_json_dict["turn_index"]
            del player_json_dict["took_action"]
            
            player_json_dict["name"] = User.get_by_id(player.user_id).name
            
            player_list.append(player_json_dict)
        
        game_json_dict["players"] = player_list
        game_list.append(game_json_dict)
    return game_list


def get_game_state(player_id: str | uuid.UUID):
    if not Player.exists_by_id(player_id):
        return json.dumps({"type": "rejection", "message": f"{player_id} is not a valid player id!"})
    
    player: Player = Player.get_by_id(player_id)
    game = player.game
    game_json = game.to_json_dict()
    
    game_json["build_piles"] = [gb.to_json_dict() for gb in GameBuild.select().where(GameBuild.game == game)]
    game_json["build_piles"].sort(key=lambda x: x["sort_key"])
    
    del game_json["deck"]
    del game_json["discard"]
    
    player_json = player.to_json_dict()
    player_json["name"] = player.user.name
    
    player_json["stock_size"] = len(player_json["stock"])
    # Only reveal the top stock card
    if len(player_json["stock"]) != 0:
        player_json["stock"] = [player_json["stock"][-1]]
    
    # Get the discard piles and sort them
    player_json["discard_piles"] = [pd.to_json_dict() for pd in
                                    PlayerDiscard.select().where(PlayerDiscard.player == player)]
    player_json["discard_piles"].sort(key=lambda x: x["sort_key"])
    
    players: list[Player] = list(Player.select().where(Player.game == game))
    players.sort(key=lambda p: p.turn_index)
    player_list = []
    for player_mini in players:
        player_mini_json = player_mini.to_json_dict()
        player_mini_json["name"] = player_mini.user.name
        # Get the discard piles and sort them
        player_mini_json["discard_piles"] = [pd.to_json_dict() for pd in
                                             PlayerDiscard.select().where(PlayerDiscard.player == player_mini)]
        player_mini_json["discard_piles"].sort(key=lambda x: x["sort_key"])
        
        del player_mini_json["hand"]
        player_mini_json["stock_size"] = len(player_mini_json["stock"])
        if len(player_mini_json["stock"]) == 0:
            player_mini_json["stock"] = []
        else:
            player_mini_json["stock"] = [player_mini_json["stock"][-1]]
        player_mini_json["name"] = player_mini.user.name
        player_list.append(player_mini_json)
    
    return json.dumps({"type": "get_room", "game": game_json,
                       "players": player_list, "player": player_json})


def replenish_player_hand(player: Player, game: Game):
    while True:
        # Try to make sure the player has five cards in their hand
        while len(player.hand) < HAND_SIZE and game.deck:
            player.hand.append(game.deck.pop())
        
        # This is the easy part
        if len(player.hand) == HAND_SIZE:
            return
        
        # Hopefully, we have some discarded cards, and we can shuffle them and put them into the deck
        if len(game.discard):
            random.shuffle(game.discard)
            game.deck.extend(game.discard)
            game.discard = CardCollection()
        # Crap, we ran out of cards. Just let this player do nothing if they want
        # It's not my fault the creators of this game didn't develop the rules properly
        else:
            player.took_action = True
            return


def process_player_move(message):
    player_id = message["player_id"]
    if not Player.exists_by_id(player_id):
        return {"type": "rejection", "message": f"{player_id} is not a valid id!"}
    player: Player = Player.get_by_id(player_id)
    game = player.game
    
    if game.current_user != player.user:
        return {"type": "rejection", "message": "It's not your turn!"}
    
    match message["type"]:
        case "draw":
            
            player.hand.append(game.deck.pop())
            player.save_and_update_time()
            game.save_and_update_time()
            
            return {"type": "acceptance"}
        
        case "hand_to_build":
            build_id = message["build_id"]
            card_id_list = message["cards"]
            
            if not GameBuild.exists_by_id(build_id):
                return {"type": "rejection", "message": f"{build_id} is not a valid Game Build id!"}
            
            player = Player.get_by_id(player_id)
            bp: GameBuild = GameBuild.get_by_id(build_id)
            
            if player.game != bp.game:
                return {"type": "rejection", "message": f"Build pile {bp.id} not in the game {player.game.id}!"}
            
            hand_id_set = set([str(c.id) for c in player.hand])
            
            if not set(card_id_list) <= hand_id_set:
                return {"type": "rejection",
                        "message": f" {set(card_id_list) - hand_id_set} are not in player {player.id}'s hand {hand_id_set}!"}
            
            submission_card_list = []
            for card_id in card_id_list:
                
                hand_index = -1
                for i, card in enumerate(player.hand):
                    if str(card.id) == card_id:
                        hand_index = i
                        break
                
                submission_card_list.append(player.hand.pop(hand_index))
            
            if not bp.can_add_cards(submission_card_list):
                # Remember to return the submission cards back to the player's hand
                player.hand.extend(submission_card_list)
                return {"type": "rejection",
                        "message": f"Cannot place {submission_card_list} on build pile {bp.id}!"}
            
            bp.deck.extend(submission_card_list)
            
            player.took_action = True
            
            game = player.game
            while len(bp.deck) >= RANK_SIZE:
                game.discard.extend(bp.deck[:RANK_SIZE])
                bp.deck = CardCollection(bp.deck[RANK_SIZE:])
            
            if len(player.hand) == 0:
                replenish_player_hand(player, game)
            
            player.save()
            bp.save()
            game.save()
            return {"type": "acceptance"}
        
        case "hand_to_discard":
            discard_id = message["discard_id"]
            card_id_list = message["cards"]
            
            if not PlayerDiscard.exists_by_id(discard_id):
                return {"type": "rejection", "message": f"{discard_id} is not a valid player discard id!"}
            
            dp: PlayerDiscard = PlayerDiscard.get_by_id(discard_id)
            
            if player != dp.player:
                return {"type": "rejection", "message": f"Discard pile {dp.id} not in the game {player.id}!"}
            
            hand_id_set = set([str(c.id) for c in player.hand])
            
            if not set(card_id_list) <= hand_id_set:
                return {"type": "rejection",
                        "message": f" {set([str(x) for x in card_id_list]) - hand_id_set} are not in player {player.id}'s hand {hand_id_set}!"}
            
            for card_id in card_id_list:
                
                hand_index = -1
                for i, card in enumerate(player.hand):
                    if str(card.id) == card_id:
                        hand_index = i
                        break
                
                dp.deck.append(player.hand.pop(hand_index))
            
            player.took_action = True
            
            game = player.game
            
            if len(player.hand) == 0:
                replenish_player_hand(player, game)
            
            player.save_and_update_time()
            game.save_and_update_time()
            dp.save_and_update_time()
            return {"type": "acceptance"}
        
        case "play_stock":
            build_id = message["build_id"]
            
            if not GameBuild.exists_by_id(build_id):
                return {"type": "rejection", "message": f"{build_id} is not a valid build pile id!"}
            
            bp: GameBuild = GameBuild.get_by_id(build_id)
            
            if bp.game != player.game:
                return {"type": "rejection", "message": f"Build pile {bp.id} not in the game {player.game.id}!"}
            
            if not bp.can_add_card(player.stock[-1]):
                return {"type": "rejection", "message": f"Can't place {player.stock[-1]} on build pile {bp.id}!"}
            
            bp.deck.append(player.stock.pop())
            player.took_action = True
            
            game = player.game
            while len(bp.deck) >= RANK_SIZE:
                game.discard.extend(bp.deck[:RANK_SIZE])
                bp.deck = CardCollection(bp.deck[RANK_SIZE:])
            
            # Player has won
            if len(player.stock) == 0:
                game.winner = player.user
            
            player.save_and_update_time()
            game.save_and_update_time()
            bp.save_and_update_time()
            
            return {"type": "acceptance"}
        
        case "play_discard":
            dp_id = message["discard_id"]
            bp_id = message["build_id"]
            
            if not PlayerDiscard.exists_by_id(dp_id):
                return {"type": "rejection", "message": f"{dp_id} is not a valid player discard id!"}
            
            if not GameBuild.exists_by_id(bp_id):
                return {"type": "rejection", "message": f"{bp_id} is not a valid build pile id!"}
            
            dp: PlayerDiscard = PlayerDiscard.get_by_id(dp_id)
            bp: GameBuild = GameBuild.get_by_id(bp_id)
            
            if not bp.can_add_card(dp.deck[-1]):
                return {"type": "rejection",
                        "message": f"Can't place {dp.deck[-1]} from discard pile {dp.id} on build pile {bp.id}!"}
            
            bp.deck.append(dp.deck.pop())
            player = dp.player
            player.took_action = True
            
            game = player.game
            while len(bp.deck) >= RANK_SIZE:
                game.discard.extend(bp.deck[:RANK_SIZE])
                bp.deck = CardCollection(bp.deck[RANK_SIZE:])
            
            game.save_and_update_time()
            dp.save_and_update_time()
            bp.save_and_update_time()
            player.save_and_update_time()
            
            return {"type": "acceptance"}
        
        case "finish_turn":
            
            if game.current_user != player.user:
                return {"type": "rejection", "message": "It's not your turn!"}
            
            if not player.took_action:
                return {"type": "rejection", "message": "Do something first!"}
            
            players = list(Player.select().where(Player.game == game))
            
            players.sort(key=lambda p: p.turn_index)
            player_index = players.index(player)
            
            player_index = (player_index + 1) % len(players)
            player.took_action = False
            game.current_user_id = players[player_index].user_id
            
            player.save_and_update_time()
            game.save_and_update_time()
            
            player = players[player_index]
            
            replenish_player_hand(player, game)
            
            player.save_and_update_time()
            game.save_and_update_time()
            
            return {"type": "acceptance"}
        
        case _:
            return {"type": "rejection", "message": f"Do not recognize type {message['type']}!"}


async def process_messages(websocket: websockets.legacy.server.WebSocketServerProtocol):
    connected.add(websocket)
    
    # while True:
    async for message in websocket:
        print()
        print(connected)
        print(message)
        
        message = json.loads(message)
        
        match message["type"]:
            
            case "create_user":
                await websocket.send(json.dumps(create_user(message["user_name"])))
            
            case "get_users":
                await websocket.send(
                    json.dumps({"type": "get_users", "users": [user.to_json_dict() for user in User.select()]}))
            case "get_games":
                game_list = get_games()
                await websocket.send(json.dumps({"type": "get_games", "games": game_list}))
            case "create_game":
                user = User.get_by_id(message["user_id"])
                
                game = Game(host=user.id, current_user_id=user.id)
                game.save(force_insert=True)
                player = Player(game_id=game.id, user_id=user.id)
                player.save(force_insert=True)
                await websocket.send(
                    json.dumps({"type": "create_game", "game": game.to_json_dict(), "player": player.to_json_dict()}))
                game_list = get_games()
                websockets.broadcast(connected, json.dumps({"type": "get_games", "games": game_list}))
            
            case "delete_game":
                user_id = message["user_id"]
                game_id = message["game_id"]
                
                if not User.exists_by_id(user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{user_id} is not a valid user id!"}))
                    continue
                if not Game.exists_by_id(game_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"}))
                    continue
                
                user: User = User.get_by_id(user_id)
                game: Game = Game.get_by_id(game_id)
                
                if game.host != user:
                    await websocket.send(json.dumps({"type": "rejection",
                                                     "message": f"You can't delete game {game.id} since you are not "
                                                                f"the host!"}))
                    continue
                
                Player.delete().where(Player.game == game).execute()
                game.delete_instance()
                
                game_list = get_games()
                await websocket.send(json.dumps({"type": "delete_game"}))
                websockets.broadcast(connected, json.dumps({"type": "get_games", "games": game_list}))
            
            case "join_game":
                user_id = message["user_id"]
                game_id = message["game_id"]
                
                if not User.exists_by_id(user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{user_id} is not a valid user id!"}))
                    continue
                
                if not Game.exists_by_id(game_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"}))
                    continue
                
                if Player.exists_by_game_id_user_id(game_id, user_id):
                    await websocket.send(json.dumps({"type": "rejection", "message": "Already in the game!"}))
                else:
                    user = User.get_by_id(user_id)
                    game = Game.get_by_id(game_id)
                    player = Player(game=game, user=user)
                    player.save(force_insert=True)
                    await websocket.send(
                        json.dumps(
                            {"type": "create_game", "game": game.to_json_dict(), "player": player.to_json_dict()}))
                    websockets.broadcast(connected, json.dumps({"type": "get_games", "games": get_games()}))
            case "unjoin_game":
                user_id = message["user_id"]
                game_id = message["game_id"]
                
                if not User.exists_by_id(user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{user_id} is not a valid user id!"}))
                    continue
                
                if not Game.exists_by_id(game_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"}))
                    continue
                
                if not Player.exists_by_game_id_user_id(game_id, user_id):
                    await websocket.send(json.dumps({"type": "rejection", "message": "Not in this game!"}))
                else:
                    player = Player.get_by_game_id_user_id(game_id, user_id)
                    player.delete()
                    await websocket.send(
                        json.dumps(
                            {"type": "acceptance"}))
                    websockets.broadcast(connected, json.dumps({"type": "get_games", "games": get_games()}))
            case "start_game":
                game_id = message["game_id"]
                user_id = message["user_id"]
                
                if not User.exists_by_id(user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{user_id} is not a valid user id!"}))
                    continue
                
                if not Game.exists_by_id(game_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"}))
                    continue
                
                game = Game.get_by_id(game_id)
                user = User.get_by_id(user_id)
                
                if game.host != user:
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"You are not the host of {game.id}!"}))
                    continue
                if game.in_progress:
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game.id} already in progress!"}))
                    continue
                else:
                    players: list[Player] = list(Player.select().where(Player.game == game))
                    
                    if len(players) > 6:
                        await websocket.send(json.dumps({"type": "rejection",
                                                         "message": f"Too many players in game room {game.id}! "
                                                                    f"There should be at most"
                                                                    f"6 but there are {len(players)} instead!"}))
                    elif len(players) < 2:
                        await websocket.send(json.dumps({"type": "rejection",
                                                         "message": f"Too many few in game room {game.id}! "
                                                                    f"There should be at least 2"
                                                                    f"but there are {len(players)} instead!"}))
                    else:
                        
                        # Create the new deck of cards
                        deck = CardCollection.getNewDeck()
                        random.shuffle(deck)
                        
                        random.shuffle(players)
                        for i, player in enumerate(players):
                            player.turn_index = i
                            
                            # Game rules state that each player gets 30 cards when there are 2-4 players
                            # or 20 cards when there are 5-6 players
                            if len(players) <= 4:
                                while len(player.stock) < 30:
                                    player.stock.append(deck.pop())
                            else:
                                while len(player.stock) < 20:
                                    player.stock.append(deck.pop())
                            player.save_and_update_time()
                            
                            # Create the discard piles
                            for _ in range(4):
                                dp = PlayerDiscard(player_id=player.id)
                                dp.save(force_insert=True)
                        
                        # Save the deck, first player to go, and mark that it's in progress
                        game.deck = CardCollection(deck)
                        game.current_user = players[0].user
                        
                        replenish_player_hand(players[0], game)
                        players[0].save()
                        game.in_progress = True
                        
                        # Create the build piles
                        
                        for _ in range(4):
                            bp = GameBuild(game_id=game.id)
                            bp.save(force_insert=True)
                        
                        game.save_and_update_time()
                        await websocket.send(json.dumps({"type": "start_game", "game_id": str(game.id)}))
                        websockets.broadcast(connected, json.dumps({"type": "get_games", "games": get_games()}))
            case "get_room":
                game_id = message["game_id"]
                user_id = message["user_id"]
                
                if not User.exists_by_id(user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{user_id} is not a valid user id!"}))
                    continue
                
                if not Game.exists_by_id(game_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"}))
                    continue
                
                if not Player.exists_by_game_id_user_id(game_id, user_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"Game {game_id} and user {user_id} do not "
                                                                    f"correspond to a player!"}))
                    continue
                
                player = Player.get_by_game_id_user_id(game_id, user_id)
                
                game_id_to_socket[player.id].add(websocket)
                
                await websocket.send(get_game_state(player.id))
            
            case "sort_hand":
                player_id = message["player_id"]

                if not Player.exists_by_id(player_id):
                    await websocket.send(
                        json.dumps({"type": "rejection", "message": f"{player_id} is not a valid player id!"}))
                    continue
                player = Player.get_by_id(player_id)
                player.hand.sort(key=lambda c: c.rank.value)
                player.save()
                await websocket.send(get_game_state(player.id))
            case _:
                await websocket.send(json.dumps(process_player_move(message=message)))
                for player_id, sockets in game_id_to_socket.items():
                    websockets.broadcast(sockets, get_game_state(player_id))
    
    connected.remove(websocket)


async def start_server():
    async with serve(process_messages, "", 8002):
        await asyncio.Future()  # run forever


def main():
    message = {}
    u = None
    while True:
        user_input = input()
        
        match user_input:
            case "u":
                name = input("What's your name?")
                message = create_user(name)
            case "login":
                name = input("What's your name? ")
                if User.exists_by_name(name):
                    u = User.get_by_name(name)
                    message = {"type": "login", "user": u.to_json_dict()}
                else:
                    u = None
                    message = {"type": "rejection", "message": "Not a valid player!"}
            case "cg":
                if u is not None:
                    g = Game(id=uuid.UUID('a5ba4c0c-19cf-4dde-b9d4-b2431794efa1'), host=u.id, current_user_id=u.id)
                    g.save()
                    p = Player(user_id=u.id, game_id=g.id)
                    p.save()
                    message = {"type": "create_game", "game": g.to_json_dict()}
                else:
                    message = {"type": "rejection", "message": "Need to login first!"}
            case "jg":
                if u is None:
                    message = {"type": "rejection", "message": "Need to login first!"}
                else:
                    # pprint.pprint(list(Game.select()))
                    id = input("Enter the game id: ").strip()
                    if is_valid_uuid(id):
                        g = Game.get_by_id(id)
                        
                        print(dir(Player))
                        if Player.exists_by_game_id_user_id(g.id, u.id):
                            message = {"type": "rejection", "message": "Already joined this game!"}
                        else:
                            p = Player(user_id=u.id, game_id=g.id)
                            p.save()
                            message = {"type": "join_game", "game": g.to_json_dict()}
                    else:
                        message = {"type": "rejection", "message": f"{id} is not a valid uuid!"}
            
            case "sg":
                if u is None:
                    message = {"type": "rejection", "message": "Need to login first!"}
                else:
                    # pprint.pprint(list(Game.select()))
                    id = input("Enter the game id: ").strip()
                    if is_valid_uuid(id):
                        g = Game.get_by_id(id)
                        
                        if g.in_progress:
                            message = {"type": "rejection", "message": f"{g.id} already in progress!"}
                        else:
                            print(dir(Player))
                            players = list(Player.select().where(Player.game == g))
                            
                            if len(players) > 6:
                                message = {"type": "rejection",
                                           "message": f"Too many players in game room {g.id}! There should be at most "
                                                      f"6 but there are {len(players)} instead!"}
                            elif len(players) < 2:
                                message = {"type": "rejection",
                                           "message": f"Too many few in game room {g.id}! There should be at least 2 "
                                                      f"but there are {len(players)} instead!"}
                            else:
                                
                                # Create the new deck of cards
                                deck = CardCollection.getNewDeck()
                                
                                print(f"{len(deck)=}")
                                
                                random.shuffle(players)
                                for i, player in enumerate(players):
                                    player.turn_index = i
                                    
                                    # Game rules state that each player gets 30 cards when there are 2-4 players
                                    # or 20 cards when there are 5-6 players
                                    if len(players) <= 4:
                                        while len(player.stock) < 30:
                                            player.stock.append(deck.pop())
                                    else:
                                        while len(player.stock) < 20:
                                            player.stock.append(deck.pop())
                                    player.save()
                                    
                                    # Create the discard piles for the player
                                    for _ in range(4):
                                        dp = PlayerDiscard(player_id=player.id)
                                        dp.save()
                                
                                # Save the deck, first player to go, and mark that it's in progress
                                g.deck = CardCollection(deck)
                                g.current_user_id = players[0].user_id
                                g.in_progress = True
                                
                                print(players)
                                g.save()
                                
                                # Create build piles
                                bp_list = []
                                for _ in range(4):
                                    bp = GameBuild(game_id=g.id)
                                    bp_list.append(bp.to_json_dict())
                                    bp.save()
                                
                                message = {"type": "start_game", "game": g.to_json_dict() | {"build_piles": bp_list},
                                           "players": [player.to_json_dict() for player in players]}
                    
                    else:
                        message = {"type": "rejection", "message": f"{id} is not a valid uuid!"}
            
            case "q":
                return
            case _:
                pass
        print(u, message)


if __name__ == '__main__':
    # main()
    asyncio.run(start_server())
