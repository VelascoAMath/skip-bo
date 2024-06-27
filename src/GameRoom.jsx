import { useParams } from "wouter";
import { sendSocket } from "./App";
import { useEffect, useState } from "react";
import Login from "./Login";




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

const cardToDiv = function(card) {

    return <div className={'card ' + (card.rank === 'W' ? 'wild' : '' )} style={{backgroundColor: rankToColor(card.color)}}> {card.rank} </div>
}


function cardCollectionDiv(cardList) {
    return (
      <div className='card-collection'>{cardList.map((card, idx) => {
        return cardToDiv(card);
      })}</div>  
    );
  }






export default function GameRoom({props}) {

    const params = useParams();
    const game_id = params.id;
    const [selectedCards, setselectedCards] = useState([]);
    const [selectedBuild, setSelectedBuild] = useState(null);
    const [selectedDiscard, setSelectedDiscard] = useState(null);

    const {state, dispatch, socket} = props;

    
    // Update our game id
    useEffect(() => {
        if(state?.game_id != game_id){
            dispatch({type: "change-input", key: "game_id", value: game_id});
        }
    })


    const game = state.game;
    const players = state.players;
    const player = state.player;

    
    if(game === null || game === undefined){
        return <div>Getting Game Information</div>
    }
    if(players === null || players === undefined){
        return <div>Getting Game Information</div>
    }
    
    if(state.user_id === null || state.user_id === undefined){
        return <div>Must Log In</div>
    }
    
    const isMyTurn = game.current_user_id === player.user_id;

    return (
        <div>
            {/* <Login props={{state, dispatch, socket}}/> */}
            <div>
                <h3>Players</h3>
                <div className="players-in-room-view">
                    {players.map((player) => {
                        
                        const borderColor = (player.user_id === game.current_user_id) ? "green": "orange";
                        return (
                            <div className="player-view" style={{borderColor: borderColor}}>
                                <div className="lay-horizontally" style={{justifyContent: "space-between", alignItems: "baseline", paddingLeft: "1%", paddingRight: "1%"}}>
                                    <h4>{player.name}</h4>
                                    <div>{cardToDiv(player.stock[0])}</div>
                                    <div>{player.stock_size} in stock</div>
                                </div>
                                <div className="build-piles">
                                    {player.discard_piles.map((dp) => {
                                        return (
                                            <div>
                                                <div className="discard-pile">{cardCollectionDiv(dp.deck)}</div>
                                            </div>
                                    );
                                    })}
                                </div>
                            </div>
                        );

                    })}
                </div>
            </div>
            <div>
                <h3>Build Piles</h3>
                <div className="build-piles">
                {game.build_piles.map((bp) => {
                    return <div onClick={() => {if(bp.id === selectedBuild){setSelectedBuild(null)} else{setSelectedBuild(bp.id)} }} className={"discard-pile" + (bp.id === selectedBuild ? " selected": "") }>{cardCollectionDiv(bp.deck)}</div>;
                })}
                </div>
            </div>
            <div className="hand" style={{justifyContent: "space-around"}}>
                <div>
                    <h3>Hand</h3>
                    <div className="lay-horizontally" style={{justifyContent: "center"}}>
                    <div className='card-collection'>
                            {player.hand.filter((card) => (!(selectedCards.includes(card)))).map((card) => {
                                return <div onClick={() => {setselectedCards([...selectedCards, card])}} className={'card ' + (card.rank === 'W' ? 'wild' : '' )} style={{backgroundColor: rankToColor(card.color)}}> {card.rank} </div>
                            })}
                        </div>
                    </div>
                    <button onClick={() => {sendSocket({type: "sort_hand", player_id: player.id}); setselectedCards([]); }}>Sort</button>
                    {isMyTurn && player.took_action  && <button onClick={() => {sendSocket({type: "finish_turn", player_id: player.id}); setselectedCards([]); }}>Finish Turn</button>}
                </div>
                <div>
                    <h3>Stock ({player.stock_size})</h3>
                    {(player.stock.length > 0) && cardToDiv(player.stock[0])}
                    {(player.stock.length > 0) && (selectedBuild !== null) && <button onClick={() => {sendSocket({type: "play_stock", player_id: player.id, build_id: selectedBuild})}}>Play Stock</button>}
                </div>
                <div>
                    <h3>Selected</h3>
                    <div className='card-collection'>
                        {selectedCards.map((card) => {
                            return <div onClick={() => {setselectedCards(selectedCards.filter((c) => c.id !== card.id))}} className={'card ' + (card.rank === 'W' ? 'wild' : '' )} style={{backgroundColor: rankToColor(card.color)}}> {card.rank} </div>
                        })}
                    </div>
                    {(selectedCards.length > 0) && (selectedDiscard !== null) && <button onClick={() => {sendSocket({type: "hand_to_discard", player_id: player.id, discard_id: selectedDiscard, cards: selectedCards.map((c) => c.id) }); setselectedCards([]); }}>To Discard</button>}
                    {(selectedCards.length > 0) && (selectedBuild !== null) && <button onClick={() => {sendSocket({type: "hand_to_build", player_id: player.id, build_id: selectedBuild, cards: selectedCards.map((c) => c.id) }); setselectedCards([]); }}>To Build</button>}
                </div>
            </div>
            <div>
                <h3>Discard Piles</h3>
                <div className="build-piles">
                    {player.discard_piles.map((dp) => {
                        return (
                            <div className={"discard-pile" + (dp.id === selectedDiscard ? " selected": "")} onClick={() => {if(dp.id === selectedDiscard){ setSelectedDiscard(null) }else{setSelectedDiscard(dp.id)} }}>
                                {cardCollectionDiv(dp.deck)}
                                {(dp.deck.length > 0) && (selectedBuild !== null) && <button onClick={() => {sendSocket({type: "play_discard", discard_id: dp.id, build_id: selectedBuild})}}>Play Discard</button>}
                            </div>
                    );
                    })}
                </div>
            </div>
        </div>
    )


}