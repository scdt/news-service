import React, {useState, useContext} from "react";
import { UserContext } from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";
const UploadImage = ({updateImagesHandle}) => {
    const [token] = useContext(UserContext);
    const [selectedImage, setSelectedImage] = useState(null);
    const [errorMsg, setErrorMsg] = useState("");

    const fileChangeHandler = (e) => {
        setSelectedImage(e.target.files[0]);
        console.log(e.target.files[0]);
    }

    const uploadImage = async () => {
        const formData = new FormData();
        formData.append(
            'file',
            selectedImage,
            selectedImage.name
        );
    

        const requestOption = {
            method: "POST",
            headers: {
                Authorization: "Bearer " + token
            },
            body: formData
        };

        console.log(requestOption);

        const response = await fetch("/api/images/", requestOption);
        console.log(response.text);

        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            updateImagesHandle();
        }
    }

    return (
        <div className="columns">
            <div className="column">
                <div className="file is-info">
                    <label className="file-label">
                        <input 
                            className="file-input"
                            type="file" 
                            placeholder="Выбрать файл"
                            name="image"
                            accept=".jpg"
                            onChange={fileChangeHandler}
                        />
                        <span class="file-cta">
                            <span class="file-icon">
                                <i class="fas fa-upload"></i>
                            </span>
                            <span class="file-label">
                                {selectedImage ? (
                                    selectedImage.name
                                ) : (
                                    "Выберите мэмчик"
                                )}
                            </span>
                        </span>
                    </label>
                </div>
            </div>
            <div className="column is-11">
                <button className="button is-primary is-1" onClick={uploadImage}>Загрузить</button>
            </div>
            <ErrorMessage message={errorMsg}/>
        </div>
    )
}

export default UploadImage;