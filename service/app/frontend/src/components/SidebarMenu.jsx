import React, {useState} from "react";
import Posts from "./Posts";
import MyPosts from "./MyPosts";
import Images from "./Images";
const Menu = () => {
    const [numPage, setPage] = useState(0);


    return (
        <>

            <div className="column is-1">
                <ul className="menu-list">
                    <li>
                        <a href onClick={() => setPage(0)}>
                            Посты
                        </a>
                    </li>
                    <li>
                        <a href onClick={() => setPage(1)}>
                            Мэмесы
                        </a>
                    </li>
                    <li>
                        <a href onClick={() => setPage(2)}> 
                            Мои посты
                        </a>
                    </li>
                </ul>
            </div>


            <div className="column is-8">
                {numPage === 0 && (
                    <Posts />
                )}

                {numPage === 1 && (
                    <Images />
                    
                )}

                {numPage === 2 && (
                    <MyPosts />
                )}
            </div> 
        </>
    );
};

export default Menu;