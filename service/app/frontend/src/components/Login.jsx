import React, { useState, useContext } from "react";

import ErrorMessage from "./ErrorMessage";
import { UserContext } from "../context/UserContext";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const [active, setActive] = useState(false);
    const [, setToken] = useContext(UserContext);

    const submitLogin = async () => {
        const requestOption = {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: JSON.stringify(
                `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`
            )
        };
        const response = await fetch("/api/token", requestOption);
        const data = await response.json();

        if (!response.ok) {
            setErrorMsg(data.detail);
        } else {
            setToken(data.access_token);
        }

    };

    const handleSubmit = (e) => {
        e.preventDefault();
        submitLogin();
    }

    const handleClick = () => {
        setActive(!active);
    }

    const modalState = active ? "is-active" : "";

    return (

        <>
        <button className="button is-link" onClick={handleClick}>Войти</button>
        <div className={`modal ${modalState}`}>
            <div className="modal-background" onClick={handleClick}></div>
            <div className="modal-card">
                <header className="modal-card-head has-background-link-light">
                    <h1 className="modal-card-title">
                        Войти
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
                
                <footer className="modal-card-foot has-background-link-light">
                    <button className="button is-primary" onClick={handleSubmit}>
                        Войти
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

export default Login;