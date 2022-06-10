import React, { useContext, useState, useEffect } from "react";
import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";
import UploadImage from "./UploadImage";

const Images = () => {
    const [token] = useContext(UserContext);
    const [images, setImages] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [newImages, setNewImages] = useState("is-active");
    const [topImages, setTopImages] = useState("");

    const getImages = async () => {
        setNewImages("is-active");
        setTopImages("");
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/images", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setImages(data);
            setLoaded(true);
        }
    };

    const getTopImages = async () => {
        setTopImages("is-active");
        setNewImages("");
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/images/top", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setImages(data);
            setLoaded(true);
        }
    };

    const imageLike = async (image_id) => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/images/${image_id}/like`, requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        }
        
        if (newImages === "is-active") {
            getImages();
        } else {
            getTopImages();
        }
    }

    const imageCringe = async (image_id) => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch(`/api/images/${image_id}/cringe`, requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        }
        
        if (newImages === "is-active") {
            getImages();
        } else {
            getTopImages();
        }
    }

    useEffect(() => {
        getImages();
    }, []);

    return (
        <>
            <UploadImage updateImagesHandle={getImages} />
            <div className="tabs">
                <ul>
                    <li className={newImages}><a href onClick={() => getImages()}>Новые</a></li>
                    <li className={topImages}><a href onClick={() => getTopImages()}>Топ</a></li>
                </ul>
            </div>
            <ErrorMessage message={errorMsg} />

            {loaded && images ? (
                <p>
                    {

                        images.map((image) => (
                            <article className="media">
                                <div className="media-content">
                                    <small> @{image.owner} </small>
                                    <div className="content">
                                        <img src={image.url} width="650" />
                                    </div>
                                    <div className="buttons">
                                        <button className="button is-small is-primary is-light" onClick={() => imageLike(image.id)}>
                                            👍🏻 {image.likes}
                                        </button>
                                        <button className="button is-small is-warning is-light" onClick={() => imageCringe(image.id)}>
                                            😬 {image.cringe}
                                        </button>
                                    </div>
                                </div>
                            </article>

                        )
                        )}

                </p>
            ) : (
                <button class="button is-loading">Loading</button>
            )}
        </>
    );
};

export default Images;