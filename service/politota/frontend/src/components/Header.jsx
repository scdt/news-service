import React, { useContext } from "react";

import { UserContext } from "../context/UserContext";
import Login from "./Login";
import Register from "./Register";

const Header = ({ title }) => {
    const [token, setToken] = useContext(UserContext);

    const handleLogout = () => {
        setToken(null);
    }

    return (
        <div className="headers">
            <nav className="navbar has-shadow">
                <div class="navbar-brand">
                    <h1 className="title">
                        <a href="/" className="navbar-item has-text-centered m6">
                            {title}
                        </a>
                    </h1>
                </div>
                <div className="navbar-end">
                    <div className="navbar-item">
                        <div className="buttons">

                            {token ?
                                <>
                                    <button className="button is-danger" onClick={handleLogout}>
                                        Выйти
                                    </button>
                                </>
                                :
                                <>
                                    <Register />
                                    <Login />
                                </>
                            }
                        </div>
                    </div>
                </div>
            </nav>
        </div>
    )
}

export default Header;