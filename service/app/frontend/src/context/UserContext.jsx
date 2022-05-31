import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext();

export const UserProvider = (props) => {
    const [token, setToken] = useState(localStorage.getItem("token"));

    useEffect(() => {
        const fetchUser = async () => {
            const requestOption = {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token
                }
            };
            const response = await fetch("/api/users/me", requestOption);

            if (!response.ok) {
                setToken(null);
            }
            localStorage.setItem("token", token);

        };

        fetchUser();

    }, [token]);

    return (
        <UserContext.Provider value={[token, setToken]}>
            {props.children}
        </UserContext.Provider>
    )
};