




export default function Help({props}){

    const {state, dispatch, socket} = props;

    const h3_style  = {display: "flex", alignItems: "baseline", whiteSpace: "nowrap"};

    return (
        <div className="help">
            <h1>How To Play SKIP-BO</h1>
            
            <div style={h3_style}> <h3>AGES</h3>: 7 and up </div>
            <div style={h3_style}><h3>PLAYERS</h3>: 2 to 6, individually or partnered</div>

            <div></div>

            <div style={h3_style}><h3>OBJECT</h3>: Be the first player to play all the cards in your STOCK pile by playing cards in numerical order, 1 through 12.</div>

            <div></div>

            <div style={h3_style}><h3>YOU SHOULD HAVE</h3>: A deck with 144 cards numbered 1 through 12 plus 18 SKIP-BO cards for a total of 162.</div>

            <div></div>

            <h2>THE OBJECT</h2>

            The first player to use up all the cards in their STOCK pile wins.

            <h2>LET'S START</h2>
            After the deck is shuffled, the order of the players will be randomly selected.
            When there are 2 to 4 players, the virtual dealer deals 30 cards to each player.
            With 5 or more players, 20 cards are dealt.
            The cards are dealt face down and they become your STOCK pile.
            Each player turns the top card of their STOCK pile face up on top of the pile, without looking at any of the other cads in the pile.
            The virtual dealer then places the remainder of the deck face down in the center of the play area to form the DRAW pile (where you'll be able to draw additional cards).

            

            <h2>HOW TO SET UP PLAY</h2>

            <h2>FURTHER EXPLAINATION OF CARD PILES</h2>
            
            <h2>HOW TO PLAY</h2>

            <h2>SCORING AND WINNING</h2>

            <h2>PARTNERSHIP</h2>

            <h2>SET-UP NOTE</h2>

            <h2>SHORT GAME</h2>

        </div>
    )
}