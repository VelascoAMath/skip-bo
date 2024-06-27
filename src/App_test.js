// This is only for testing purposes
import { useReducer, useState } from 'react';
import './App.css';
import inputReducer from './InputReducer';



const socket = new WebSocket("ws://localhost:8002");

// Connection opened
socket.onopen = () => {
  socket.send(JSON.stringify({"type": "get_users"}));
  socket.send(JSON.stringify({"type": "get_games"}));
}


function sendSocket(message){
  socket.send(JSON.stringify(message));
}


function rankToColor(rank){
  switch(rank){
    case 'R':
      return 'red';
    case 'B':
      return 'blue';
    case 'G':
      return 'green';
    case 'Y':
      return 'yellow';
    default:
      return 'black';
  }
}

function cardCollectionDiv(cardList) {
  return (
    <div className='card-collection'>{cardList.map((card, idx) => {

      return <div className={'card ' + (card.rank === 'W' ? 'wild' : '' )} style={{backgroundColor: rankToColor(card.color)}}> {card.rank} </div>
    })}</div>  
  );
}


function cardCollectionSelectionDiv(cardList, selectedCards, setSelectedCards, player_id) {
  return (
    <div className='card-collection'>
      {cardList.map((card, idx) => {
      
      const isSelected = selectedCards[player_id]?.includes(card.id);
      const onClick = function(){
        if (!(player_id in selectedCards)){
          setSelectedCards({...selectedCards, [player_id]: [card.id]})
        }
        else if (isSelected){
          setSelectedCards({...selectedCards, [player_id]: selectedCards[player_id].filter((c_id) => c_id !== card.id)});
        } else {
          setSelectedCards({...selectedCards, [player_id]: [...selectedCards[player_id], card.id] });
        }
      };
      const cardClass = 'card ' + (card.rank === 'W' ? 'wild ' : ' ' ) + (isSelected ? 'selected' : '' )
      return <div onClick={onClick} className={cardClass} style={{backgroundColor: rankToColor(card.color)}}>{card.rank} </div>
    })}</div>  
  );
}

function getRoomDiv(room, playerList, selectedCards, setSelectedCards, selectedDiscardPile, setSelectedDiscardPile, selectedBuildPile, setSelectedBuildPile){
  if(room === null || playerList === null){
    return <div></div>
  }

  return (
    <div>
      <h2>Room {room.id}</h2>
    

      <div>
        
        <h4>Deck</h4>
        {cardCollectionDiv(room.deck)}
        <h4>Discard</h4>
        {cardCollectionDiv(room.discard)}
        
        <div className="build-piles">
          <h4>Build Piles</h4>
          {room.build_piles.map((build_pile, idx) => {

            const onClick = function() {
              if(build_pile.id === selectedBuildPile){
                setSelectedBuildPile(null);
              } else {
                setSelectedBuildPile(build_pile.id);
              }
            }

            return <div className={'discard-pile ' + (build_pile.id === selectedBuildPile ? "selected" : "") } onClick={onClick}>
            Build Pile {idx + 1} {cardCollectionDiv(build_pile.deck)}
            </div>
          })}
        </div>

      </div>
      

      <div>
          <h2>Player List</h2>
          
          {JSON.stringify(room.current_user_id)}
          <div>
            {playerList.map((player, idx) => {
              return (
                <>
                <h3>Player {player.turn_index+1} {player.name} {JSON.stringify(player.user_id == room.current_user_id)} </h3>
                
                <button onClick={() => {sendSocket({type: "sort_hand", player_id: player.id})}}>Sort</button>
                {/* <button onClick={() => {sendSocket({type: "draw", player_id: player.id})}}>Draw</button> */}
                
                {selectedBuildPile && selectedCards[player.id] && (selectedCards[player.id].length > 0) &&
                <button onClick={() => {sendSocket({type: "hand_to_build", player_id: player.id, build_id: selectedBuildPile, cards: selectedCards[player.id]}); setSelectedBuildPile(null); setSelectedCards({...selectedCards, [player.id]: []})}}>Place In Build</button>}
                
                {selectedDiscardPile[player.id] && (selectedDiscardPile[player.id].length > 0) && selectedCards[player.id] && (selectedCards[player.id].length > 0) &&
                <button onClick={() => {sendSocket({type: "hand_to_discard", player_id: player.id, discard_id: selectedDiscardPile[player.id], cards: selectedCards[player.id]}); setSelectedDiscardPile({...selectedDiscardPile, [player.id] : null}); setSelectedCards({...selectedCards, [player.id]: []})}}>Place In Discard</button>}
                
                {selectedBuildPile &&
                <button onClick={() => {sendSocket({type: "play_stock", player_id: player.id, build_id: selectedBuildPile}); setSelectedBuildPile(null); setSelectedCards({...selectedCards, [player.id]: []}) }} >Play Stock</button>}

                {player.took_action &&
                <button onClick={() => {sendSocket({type: "finish_turn", player_id: player.id})} }>Finish Turn</button>}

                <h4>Hand</h4>
                {cardCollectionSelectionDiv(player.hand, selectedCards, setSelectedCards, player.id)}
                <hr/>
                <div className="discard-piles">
                  <h4>Player Discard Piles</h4>

                  {player.discard_piles.map((discard, idx) => {

                    const onClick = function() {
                      if (player.id in selectedDiscardPile){
                        if(selectedDiscardPile[player.id] === discard.id){
                          setSelectedDiscardPile({...selectedDiscardPile, [player.id]: null});
                        } else {
                          setSelectedDiscardPile({...selectedDiscardPile, [player.id] : discard.id});
                        }
                      } else {
                        setSelectedDiscardPile({...selectedDiscardPile, [player.id] : discard.id});
                      }
                    }

                   return <div className={'discard-pile ' + (discard.id === selectedDiscardPile[player.id] ? "selected" : "") } onClick={onClick}>
                    <div>Discard Pile {idx + 1}</div>
                    {cardCollectionDiv(discard.deck)}
                    {selectedDiscardPile[player.id] && (selectedDiscardPile[player.id] === discard.id) && selectedBuildPile && (discard.deck.length > 0) &&
                    <button onClick={() => {sendSocket({type: "play_discard", build_id: selectedBuildPile, discard_id: discard.id})  } }>Play Discard</button>}
                    </div>
                  })}
                </div>
                
                <hr/>
                <h4>Stock</h4>
                {cardCollectionDiv(player.stock)}
                </>
              );
            })}
          </div>

      </div>


    </div>
  )

}




function App() {
  const [userList, setUserList] = useState([]);
  const [gameList, setGameList] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [userName, setUserName] = useState("");
  const [room, setRoom] = useState(null);
  const [playerList, setPlayerList] = useState(null);
  const [socketClosed, setSocketClosed] = useState(false);
  const [selectedCards, setSelectedCards] = useState({});
  const [selectedDiscardPile, setSelectedDiscardPile] = useState({});
  const [selectedBuildPile, setSelectedBuildPile] = useState(null);

  
  const [state, dispatch] = useReducer(inputReducer, {});

  if (socketClosed){
    return <div>Socket closed</div>
  }

  // Listen for messages
  socket.onmessage = (event) => {
    // console.log("Message from server ", event.data);
    const data = JSON.parse(event.data);
    console.log(data);
    switch (data["type"]){
      case 'get_users':
        setUserList(data["users"]);
        break;
      case 'get_games':
        setGameList(data["games"]);
        break;
      case 'create_user':
        socket.send(JSON.stringify({"type": "get_users"}));
        break;
      case 'get_room':
        setRoom(data["game"]);
        setPlayerList(data["players"]);
        break;
      case 'rejection':
        alert(data["message"]);
        break;
      default:
        console.log("Unrecognized!");

    }
  }


  // Connection closed
  socket.onclose = () => {setSocketClosed(true)}
  
  return (
    <>
    <div>
      <h2>User List</h2>
      <div> {userList.map(user => <button key={user.id} onClick={() => {dispatch({type: "change-input", key: "user", value: user})}}>{user.name}</button>)} </div>
      <input value={userName} onInput={(e) => (setUserName(e.target.value))} onKeyDown={(e) => {if(e.code === 'Enter' || e.code === 'NumpadEnter') { setUserName(""); socket.send(JSON.stringify({type: "create_user", user_name: userName})) } }}/>
      <button onClick={() => {setUserName(""); socket.send(JSON.stringify({type: "create_user", user_name: userName}))}}>Create User</button>
    </div>

    {state.user && <div>
      <h2>Game Actions</h2>
      <div> <button onClick={() => {socket.send(JSON.stringify({type: "create_game", user_id: state.user.id}))}} >Create Game</button> </div>
      <button onClick={() => {socket.send(JSON.stringify({type: "join_game", user_id: state.user.id, game_id: selectedGame}))}} >Join Game</button>
      <button onClick={() => {socket.send(JSON.stringify({type: "start_game", user_id: state.user.id, game_id: selectedGame}))}} >Start Game</button>
      <button onClick={() => {socket.send(JSON.stringify({type: "get_room", game_id: selectedGame}))}}>Get Room</button>
    </div>}

    <div>
      <h2>Game List</h2>
      <div className='game-list'>
        {gameList.map((game, idx) => 
          <div className={(game.id === selectedGame) ? 'game selected': 'game'} key={game.id} onClick={() => { if(game.id === selectedGame){setSelectedGame(null)} else {setSelectedGame(game.id)}}}>
            <div>
              Game {idx + 1}
            </div>
            <hr/>
            {game.players.filter((player) => player.user_id === game.owner).map((player) => 
              <div key={player.id}>
                {player.name}
              </div>
            )}
            <hr/>
            {game.players.filter((player) => player.user_id !== game.owner).map((player) => 
              <div key={player.id}>
                {player.name}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
    <div>
      <h2>Global State</h2>
      <div>{JSON.stringify(state)}</div>
    </div>

    {getRoomDiv(room, playerList, selectedCards, setSelectedCards, selectedDiscardPile, setSelectedDiscardPile, selectedBuildPile, setSelectedBuildPile)}

    
    </>
  );
}

export default App;
