import { useReducer, useState } from 'react';
import './App.css';
import inputReducer from './InputReducer';
import { Link, Route } from 'wouter';
import CreateUser from './CreateUser';
import Login from './Login';
import Lobby from './Lobby';
import GameRoom from './GameRoom';
import Help from './Help';
import URL from './URL';



const socket = new WebSocket(URL);

export function sendSocket(message){
  socket.send(JSON.stringify(message));
}


const initState = {
  user_id: localStorage.getItem("user_id"),
  user_name: localStorage.getItem("user_name"),
  user_token: localStorage.getItem("user_token"),
}


function App() {
  const [socketClosed, setSocketClosed] = useState(false);
  
  
  const [state, dispatch] = useReducer(inputReducer, initState);

  if (socketClosed){
    return <div>Socket closed</div>
  }

  // Connection opened
  socket.onopen = () => {
    sendSocket({"type": "get_users"});
    sendSocket({"type": "get_games"});
  }


  // Update the room if it's outdated or not 
  if(socket.readyState === socket.OPEN){
    
    if(state.game_id){
      if(state["user_id"] === undefined || state["game_id"] === undefined || state["game"] === undefined || state["players"] === undefined){
        sendSocket({type: "get_room", game_id: state.game_id, user_id: state["user_id"]});
      } else if(state["user_id"] === null || state["game_id"] === null || state["game"] === null || state["players"] === null){
        sendSocket({type: "get_room", game_id: state.game_id, user_id: state["user_id"]});
      }
    }
  }
  
  // Listen for messages
  socket.onmessage = (event) => {
    // console.log("Message from server ", event.data);
    const data = JSON.parse(event.data);
    console.log(data);
    switch (data["type"]){
      case 'get_users':
        dispatch({type: "change-input", key: "user_list", value: data["users"]});
        break;
        case 'get_games':
          dispatch({type: "change-input", key: "games", value: data["games"]});
        break;
      case 'create_user':
        socket.send(JSON.stringify({"type": "get_users"}));
        const user = data["user"];
        dispatch({type: "change-input", key: "user_id", value: user.id});
        dispatch({type: "change-input", key: "user_name", value: user.name});
        dispatch({type: "change-input", key: "user_token", value: user.token});
        localStorage.setItem("user_id", user.id);
        localStorage.setItem("user_name", user.name);
        localStorage.setItem("user_token", user.token);
        break;
      case 'delete_game':
        sendSocket({"type": "get_games"});
        break;
      case 'get_room':
        // See if we're getting someone else's data
        if(state.player && state?.player.game_id !== data.player.game_id) {
          sendSocket({type: "get_room", game_id: state.player.game_id, user_id: state.player.user_id});
        } else if (state.player && state?.player.user_id !== data.player.user_id) {
          sendSocket({type: "get_room", game_id: state.player.game_id, user_id: state.player.user_id});
        } 
        else {
          dispatch({type: "change-input", key: "game", value: data.game});
          dispatch({type: "change-input", key: "players", value: data.players});
          dispatch({type: "change-input", key: "player", value: data.player});
        }
        break;
      case 'acceptance':
        break;
      case 'rejection':
        alert(data["message"]);
        break;
      default:
        console.log(data);
        console.log("Unrecognized!");

    }
  }


  // Connection closed
  socket.onclose = () => {setSocketClosed(true)}

  return (
    <div style={{display: "flex", flexDirection: "column", rowGap: "20px", textAlign: "center"}}>
      <div style={{display: "flex", justifyContent: "space-around", backgroundColor: "white", color: "purple"}}>
        {state?.user_name && <div>{state?.user_name}</div>}
        {!(state?.user_name) && <div style={{color: "red"}}>Guest</div>}
        <Link href="/">Home</Link>
        <Link href="/help">Help</Link>

      </div>
      <Route path="/">
      <div className="home">
        <h1>
          <Link href='/user'>Create User</Link>
        </h1>
        <h1>
          <Link href='/login'>Log In</Link>
        </h1>
        <h1>
          <Link href='/lobby'>Go To Lobby</Link>
        </h1>
      </div>
      </Route>

      <Route path="/user">
        <CreateUser props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/login">
        <Login props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/lobby">
        <Lobby props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/game/:id">
        <GameRoom props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/help">
        <Help props={{state, dispatch, socket}}/>
      </Route>
    </div>
  )
    
}

export default App;
