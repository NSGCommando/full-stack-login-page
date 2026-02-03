function TextInput({label, id, ...inputParams}) //Take label separately and collect all other params into a rest parameter
{
    return(
        <div>
            <label htmlFor={id}>{label}</label>
            {/*destructure the rest parameter to get all parameters (type, value, onChange) */}
            <input id={id} {...inputParams}/>
        </div>
    );
}

export default TextInput