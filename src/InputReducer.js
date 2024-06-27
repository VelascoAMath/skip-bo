



export default function inputReducer(state, action) {

    switch(action.type){
        case 'change-input': {

            return {...state, [action.key]: action.value};
        }
        default: {
            console.log(state);
            console.log(action);
            return state;
        }
    }
}