import React, {useState, useEffect, useContext} from "react";
import Header from "./components/Header";
import Menu from "./components/SidebarMenu";
import { UserContext } from "./context/UserContext";

const App = () => {

  const [message, setMessage] = useState("");
  const [token] = useContext(UserContext); 

  const getWelcomeMessage = async () => {
    const requestOption = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const response = await fetch("/api", requestOption);
    const data = await response.json();
    
    if (!response.ok) {
      console.log("someone brocked");
    } else {
      setMessage(data.Messages);
    }
  };

  useEffect(() => {
   getWelcomeMessage();
  }, []);

  return (
    <>
   <Header title={message} />

      <div className="columns m-5 ">
        {!token ? (
            <div className="column">
              <p>Вы не имеете право на просмотр</p>
            </div>
          ) : (
            <>
              <Menu />
            </>
          )}
      </div>
   </>
  );
}

export default App;
