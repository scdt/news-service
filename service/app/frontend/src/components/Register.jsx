import React, {useContext, useState} from "react";

import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [realname, setRealname] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const [active, setActive] = useState(false);

    const [, setToken] = useContext(UserContext);

    const submitRegistration = async () => {
        const requestOption = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username: username, password: password, realname: realname})
        };

        const response = await fetch("/api/users", requestOption);
        const data = await response.json();

        if (!response.ok) {
            setErrorMsg(data.detail);
        } else {
            setToken(data.access_token);
        }
    };

    const handleClick = () => {
        setActive(!active);
    }

    const handleSubmit = (e) => {
        e.preventDefault();
        submitRegistration();
    };  

    const modalState = active ? "is-active" : "";
    return (

        <>
        <button className="button is-primary" onClick={handleClick}>Регистрация</button>
        <div className={`modal ${modalState}`}>
            <div className="modal-background" onClick={handleClick}></div>
            <div className="modal-card">
                <header className="modal-card-head has-background-primary-light">
                    <h1 className="modal-card-title">
                        Регистрация
                    </h1>
                </header>
                <section className="modal-card-body">
                    <form>
                        <div className="field">
                            <label className="label">Имя пользователя</label>
                            <div className="control">
                                <input 
                                    type="text" 
                                    placeholder="Введите имя пользователя" 
                                    value={username}
                                    onChange = {(e) => setUsername(e.target.value)}
                                    className="input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="field">
                            <label className="label">Реальное имя</label>
                            <div className="control">
                                <input 
                                    type="text" 
                                    placeholder="Ваше реальное имя?" 
                                    value={realname}
                                    onChange = {(e) => setRealname(e.target.value)}
                                    className="input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="field">
                                <label className="label">Пароль</label>
                                <div className="control">
                                    <input 
                                        type="password" 
                                        placeholder="Введите ваш пароль" 
                                        value={password} 
                                        onChange={ (e) => setPassword(e.target.value)}
                                        className="input"
                                        required
                                    />
                                </div>
                            </div>
                    </form>
                    <ErrorMessage message={errorMsg}/>
                </section>
                
                <footer className="modal-card-foot has-background-primary-light">
                    <button className="button is-primary" onClick={handleSubmit}>
                        Вступить
                    </button>
                    <button className="button" onClick={handleClick}>
                        Закрыть
                    </button>
                    
                </footer>
            </div>
        </div>
        </>
    )
}

export default Register;