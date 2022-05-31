import React, { useContext, useState, useEffect } from "react";
import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";
import UploadImage from "./UploadImage";

const Images = () => {
    const [token] = useContext(UserContext);
    const [images, setImages] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const getImages = async () => {
        const requestOption = {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            }
        }

        const response = await fetch("/api/images/", requestOption);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            const data = await response.json();
            setImages(data);
            setLoaded(true);
        }
    };

    useEffect(() => {
        getImages();
    }, []);

    return (
        <>
            <UploadImage updateImagesHandle={getImages} />
            <ErrorMessage message={errorMsg} />
            {loaded && images ? (
                <p>
                    {
                        images.map((image) => (
                            <article className="media">
                                <div className="media-content">
                                    <div className="content">
                                        <img src={image.url} width="600" />
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

export default Images;