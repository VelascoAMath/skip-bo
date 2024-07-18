



export default function inputReducer(state, action) {

    switch(action.type){
        case 'change-input': {

            return {...state, [action.key]: action.value};
        }
        case 'delete-key': {

            let newState = {};

            for(const [key, value] of Object.entries(state)){
                if(key === action.key){
                    continue;
                }
                newState[key] = value;
            }

            return newState;
        }
        default: {
            console.log(state);
            console.log(action);
            return state;
        }
    }
}