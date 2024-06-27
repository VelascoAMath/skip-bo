






export default function Login({props}){
    
    const {state, dispatch, socket} = props;



    return (
        <>
            <h1>Select your login information</h1>
            <div className="user-list">
                {state?.user_list?.map((user) => {
                    return <button key={user.id} style={{margin: "10px", fontSize: "xx-large"}} onClick={() => {
                        dispatch({type: "change-input", key: "user_id", value: user.id});
                        dispatch({type: "change-input", key: "user_name", value: user.name});
                        dispatch({type: "change-input", key: "user_token", value: user.token});
                        localStorage.setItem("user_id", user.id);
                        localStorage.setItem("user_name", user.name);
                        localStorage.setItem("user_token", user.token);

                        // Delete everything associated with the game
                        dispatch({type: "delete-key", key: "game"});
                        dispatch({type: "delete-key", key: "players"});
                        dispatch({type: "delete-key", key: "player"});
                        localStorage.removeItem("game");
                        localStorage.removeItem("players");
                        localStorage.removeItem("player");

                        }}>
                        {user.name}
                    </button>})} 
            </div>
        </>
    )
}