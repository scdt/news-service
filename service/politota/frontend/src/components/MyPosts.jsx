import React, { useContext, useState, useEffect } from "react";
import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";

const MyPosts = () => {
    const [token] = useContext(UserContext);
    const [posts, setPosts] = useState(null);
    const [errorMsg, setErrorMsg] = useState("");

    const handleDelete = async (post_id) => {
        const requestOption = {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/posts/${post_id}`, requestOption);

        if (!response.ok) {
            setErrorMsg("Что-то пошло не так при удалении поста");
        } else {
            getMyPosts();
        }
    };

    const getMyPosts = async () => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/posts/my", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setPosts(data);
        }
    };

    useEffect(() => {
        getMyPosts();
    }, []);

    return (
        <>
            <ErrorMessage message={errorMsg} />

            {posts ? (
                <p>
                    {
                        posts.map((post) => (
                            <article className="media">
                                <div className="media-content">
                                    <div className="content">
                                        <p>
                                            <strong>{post.title} </strong>
                                            <button
                                                className="button is-small is-danger is-light"
                                                onClick={() => handleDelete(post.id)}>
                                                удалить
                                            </button>
                                            <br />
                                            {post.content}
                                        </p>
                                    </div>
                                </div>
                            </article>
                        ))}

                </p>
            ) : (
                <>
                    <button class="button is-loading">Loading</button>
                </>
            )}
        </>
    );
};

export default MyPosts;