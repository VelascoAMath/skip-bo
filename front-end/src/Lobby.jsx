import { useState } from "react";
import { sendSocket } from "./App";
import { useLocation } from "wouter";








const starFill = function(){
    return <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">
    <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
  </svg>;
}



export default function Lobby({props}) {

    const {state} = props;
    const [selectedGame, setSelectedGame] = useState(null);
    const [, setLocation] = useLocation();
    
    if(state["user_name"] === null || state["user_id"] === null || state["user_token"] === null){
        return <div>Must Log In</div>
    }

    const tryToDelete = function() {
        if(selectedGame.in_progress){
            if(window.confirm("Are you sure you want to delete this game? It's already in progress")){
                sendSocket({type: "delete_game", user_id: state.user_id, game_id: selectedGame.id});
                setSelectedGame(null);
            }
        } else {
            sendSocket({type: "delete_game", user_id: state.user_id, game_id: selectedGame.id});
            setSelectedGame(null);
        }
    }

    return (
        <div>
            <div style={{display: "flex", justifyContent: "space-between"}}>
                <button onClick={() => {sendSocket({type: "create_game", user_id: state["user_id"]})}}>Create Game</button>
                {selectedGame?.host === state.user_id && <button onClick={tryToDelete}>DELETE GAME</button>}
            </div>
            <div className="game-list">
                {state["games"]?.map((game) => {

                    const players = game.players;
                    const host = players.filter((player) => player.user_id === game.host)[0];
                    const others = players.filter((player) => player.user_id !== game.host);

                    const inGame = players.filter((player) => player.user_id === state.user_id).length > 0;
                    const isHost = game.host === state.user_id;
                    const inProgress = game.in_progress;


                    const getButton = function() {

                        if(isHost && inGame && others.length > 0){
                            const onClick = function(){
                                if(!inProgress){
                                    sendSocket({type: "start_game", game_id: game.id, user_id: state.user_id});
                                }
                                setLocation("/game/" + game.id);

                            }
                            return <button onClick={onClick}>Play</button>
                        }
                        if(!isHost && inGame && inProgress){
                            return <button onClick={() => { setLocation("/game/" + game.id)}}>Play</button>
                        }

                        if(!isHost && inGame && !inProgress){
                            return <button onClick={() => {sendSocket({type: "unjoin_game", user_id: state.user_id, game_id: game.id})}}>Unjoin</button>
                        }
                        if(!isHost && !inGame && !inProgress){
                            return <button onClick={() => {sendSocket({type: "join_game", user_id: state.user_id, game_id: game.id})}}>Join</button>
                        }

                        return null;
                    }

                    // No point of displaying this game since you can't join
                    if (getButton() === null && !isHost){
                        return null;
                    }

                    let gameClass = "game";
                    if(game.id === selectedGame?.id){
                        gameClass += " selected";
                    }

                    return <div key={game.id} onClick={() => {if(game.host === state.user_id){if(game === selectedGame){setSelectedGame(null)}else{setSelectedGame(game)}}}} className={gameClass}>
                        <div> {inProgress && starFill()} Host: {host.name}</div>
                        <hr/>
                        {others.map((player) => {
                            return <div key={player.id}>{player.name}</div>
                        })}
                        <hr/>
                        {getButton()}
                    </div>
                })}
            </div>
        </div>
    )
}