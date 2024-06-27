import { useReducer, useState } from 'react';
import './App.css';
import inputReducer from './InputReducer';
import { Link, Route, Switch } from 'wouter';
import Create_User from './Create_User';



const socket = new WebSocket("ws://localhost:8002");

export function sendSocket(message){
  socket.send(JSON.stringify(message));
}




function App() {
  const [gameList, setGameList] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [userName, setUserName] = useState("");
  const [room, setRoom] = useState(null);
  const [playerList, setPlayerList] = useState(null);
  const [socketClosed, setSocketClosed] = useState(false);
  
  
  const [state, dispatch] = useReducer(inputReducer, {});
    
  if (socketClosed){
    return <div>Socket closed</div>
  }

  // Connection opened
  socket.onopen = () => {
    sendSocket({"type": "get_users"});
    sendSocket({"type": "get_games"});
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
    <div style={{display: "flex", flexDirection: "column", rowGap: "20px", textAlign: "center"}}>
      <Route path="/">
        <h1>
          <Link href='/user'>Create User</Link>
        </h1>
        <h1>
          <Link href='/login'>Log In</Link>
        </h1>
        <h1>
          <Link href='/lobby'>Go To Lobby</Link>
        </h1>
      </Route>

      <Route path="/user">
        <Create_User props={{state, dispatch, socket}}/>
      </Route>
    </div>
  )
    
}

export default App;
