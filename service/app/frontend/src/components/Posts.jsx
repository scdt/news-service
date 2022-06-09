import React, { useContext, useState, useEffect } from "react";
import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";
import PostCreateModal from "./PostCreateModal";

const Posts = () => {
    const [token] = useContext(UserContext);
    const [posts, setPosts] = useState(null);
    const [errorMsg, setErrorMsg] = useState("");
    const [loaded, setLoaded] = useState(false);
    const [activeCreatePost, setActiveCreatePost] = useState(false);
    const [newPosts, setNewPosts] = useState("is-active");
    const [topPosts, setTopPosts] = useState("");
    const [sendReport, setSendReport] = useState("");

    function sleep(time) {
        return new Promise((resolve) => setTimeout(resolve, time))
    }

    const getPosts = async () => {
        setTopPosts("");
        setNewPosts("is-active");
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/posts", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setPosts(data);
            setLoaded(true);
        }
    };

    const getTopPosts = async () => {
        setNewPosts("");
        setTopPosts("is-active");
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/posts/top", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setPosts(data);
        }
    };

    const postLike = async (post_id) => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/posts/${post_id}/like`, requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        }

        if (newPosts === "is-active") {
            getPosts();
        } else {
            getTopPosts();
        }
    }

    const postReport = async (post_id) => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/posts/${post_id}/report`, requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            setSendReport("отправлено");
            await sleep(1000);
            setSendReport("");
        }
    }

    const postCringe = async (post_id) => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/posts/${post_id}/cringe`, requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        }

        if (newPosts === "is-active") {
            getPosts();
        } else {
            getTopPosts();
        }
    }

    const handleModal = () => {
        setActiveCreatePost(!activeCreatePost);
        getPosts();
    };

    useEffect(() => {
        getPosts();
    }, []);



    return (
        <>
            <PostCreateModal
                active={activeCreatePost}
                handleModal={handleModal}
                token={token}
            />
            <button className="button md-5 is-primary" onClick={() => setActiveCreatePost(true)}>
                Написать мнение
            </button>
            <br />
            <ErrorMessage message={errorMsg} />
            <div className="tabs">
                <ul>
                    <li className={newPosts}><a href onClick={() => getPosts()}>Новые</a></li>
                    <li className={topPosts}><a href onClick={() => getTopPosts()}>Топ</a></li>
                </ul>
            </div>
            <h2 className="has-text-danger-dark">{sendReport}</h2>
            {loaded && posts ? (
                <p>
                    {
                        posts.map((post) => (

                            <article className="media">

                                <div className="media-content">
                                    <div className="content">
                                        <p>
                                            <strong>{post.title}</strong>
                                            <small> @{post.owner_username} </small>
                                            <button className="button is-small is-danger is-light"
                                                onClick={() => postReport(post.id)}>
                                                настучать
                                            </button>
                                            <br />
                                            {post.content}
                                        </p>
                                        <div className="buttons">
                                            <button className="button is-small is-primary is-light" onClick={() => postLike(post.id)}>
                                                👍🏻 {post.likes}
                                            </button>
                                            <button className="button is-small is-warning is-light" onClick={() => postCringe(post.id)}>
                                                😬 {post.cringe}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </article>
                        ))}

                </p>
            ) : (
                <button class="button is-loading">Loading</button>
            )}
        </>
    );
};

export default Posts;