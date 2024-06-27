import { useReducer, useState } from 'react';
import './App.css';
import inputReducer from './InputReducer';
import { Link, Route, Switch } from 'wouter';
import Create_User from './Create_User';
import Login from './Login';
import Lobby from './Lobby';



const socket = new WebSocket("ws://localhost:8002");

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
        // setRoom(data["game"]);
        // setPlayerList(data["players"]);
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
        <div></div>

      </div>
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
      <Route path="/login">
        <Login props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/lobby">
        <Lobby props={{state, dispatch, socket}}/>
      </Route>
    </div>
  )
    
}

export default App;
