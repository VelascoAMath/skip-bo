import SkipBoGameLayout from "./SkipBoGameLayout";



export default function Help(){


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
            In the center area of play, right near the DRAW pile, up to four BUILDING piles will be created for all players to use during play.
            In addition, each player will have in front of them a STOCK pile and up to 4 DISCARD piles.
            (See Illustration, below)

            <h3>IMPORTANT NOTE</h3>: BUILDING piles and DISCARD piles are developed through play (indicated by dotted lines, below).
            No cards are in this area at the beginning of the game.
            Also, SKIP-BO cards are wild.
            This is important.
            
            <div>
                <SkipBoGameLayout/>
            </div>

            <h2>FURTHER EXPLAINATION OF CARD PILES</h2>

            <ol>
                <li><h3>Stock Pile</h3> Each player has one STOCK pile, placed face down on his right, with the top card of the pile always turned face-up on top.</li>
                <li><h3>Draw Pile</h3> After the deal, the remaining cards are placed face down in the center of the table to form the DRAW pile.</li>
                <li><h3>Building Pile</h3> During play up to four BUILDING piles can be started. Only a 1 or SKIP-BO card can start a BUILDING pile.
                Each pile is then built up numerically in sequence, 1 through 12.
                Since SKIP-BO cards are wild, they can start a BUILDING pile, and can be played as any other number, too.
                Once a pile of 12 cards has been completed, it is removed, and a new pile is started in its place.</li>
                <li><h3>Discard Pile</h3> During play, each player may build up to four DISCARD piles to the left of their STOCK pile.
                They can build up any number of cards in any order in the DISCARD piles, but may only play the top card.</li>
            </ol>
            
            <h2>HOW TO PLAY</h2>

            Player order is randomly determined.

            Draw 5 cards from the DRAW pile.
            If you have a SKIP-BO card or a number 1 card on top of your STOCK pile or in your hand, you may use it to start a BUILDING pile in the center of the play area.
            You may then continue by playing another card from your STOCK pile onto a BUILDING pile.
            If you play all 5 cards, draw 5 more and continue playing.
            If you can't make a play or just don't want to, end your turn by discarding one of the cards from your hand onto one of your four DISCARD piles.

            On your second and succeeding turns, first draw enough cards to bring your hand back up to 5.
            You may then add to the BUIDLING piles (always in sequential order) by playing the top card from your STOCK pile, DISCARD pile, or from your hand.
            Bur remember, the winner is the one who plays all the cards in their STOCK pile, so it's best to always use the playable cards from that pile first.
            If the DRAW pile is used up, the cards from the completed BUILDING piles are shuffled and become the new DRAW pile.

            <h2>SCORING AND WINNING</h2>

            You may wish to play several games and keep score.
            The winner of each game scores 5 points for each card remaining in his opponents' STOCK piles, plus 25 points for winning the game.
            The first person to collect 500 points wins.

            {/* <h2>PARTNERSHIP</h2>

            All the rules stay the same except the following:

            During your turn, you can play from both your STOCK and DISCARD piles and your partner's.
            However, during your turn, your partner must keep quiet.
            Only the player taking their turn can ask their partner to make a play, i.e., "Partner, player your SKIP-BO as a 4" or "Partner, play your 7."
            Any player guilty of cheating must take 2 cards from the DRAW pile and place them in their STOCK pile wihtout looking at them.
            The game is over when both STOCK piles of one of the partnerships are finished.

            In partnership play, both partners can continue to play from their remaining DISCARD or BUILDING piles even if one of the STOCK piles is finished. */}

            <h2>SET-UP NOTE</h2>

            <ol>
                <li>A player's four DISCARD piles are imaginary until they start them during play.</li>
                <li>The BUILDING piles are imaginary until started by players during the game.</li>
                <li>Remember: The object of the game is to get rid of the cards from your {/*(and your partner's if playing partnerships)*/} STOCK piles</li>
            </ol>

            <h2>SHORT GAME</h2>

            For players wishing to play a short version of SKIP-BO, the dealer deals a STOCK pile of 10 cards to each player.
            All other rules remain the same.

            

        </div>
    )
}