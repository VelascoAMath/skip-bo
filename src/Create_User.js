import { useEffect, useState } from "react";
import { sendSocket } from "./App";


export default function Create_User({props}) {

    const {state, dispatch, socket} = props;
    const [name, setName] = useState("");

    const submitName = function(){
        setName("");
        if(name !== ""){
            sendSocket({type: "create_user", user_name: name});
        }
    }
    
    return (
        <div>
            <div className="user-list">
               {state?.user_list?.map((user) => {return <div className="user">{user.name}</div>})} 
            </div>
            <div>
                What is your name?
            </div>
            <div>
                <input onInput={(e) => {setName(e.target.value)}} onKeyDown={(e) => {if(e.code === "NumpadEnter" || e.code === "Enter"){submitName()} }} value={name}/>
                <button onClick={submitName}>Submit</button>
            </div>
        </div>
    )

}
