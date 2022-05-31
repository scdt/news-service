import React, { useState } from "react";
import ErrorMessage from "./ErrorMessage";

const PostCreateModal = ({ active, handleModal, token }) => {
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [privatePost, setPrivatePost] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const modalState = active ? "is-active" : "";

    const cleanFormData = () => {
        setTitle("");
        setContent("");
    }

    const handleCreatePost = async (e) => {
        e.preventDefault();
        const requestOption = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify({
                title: title,
                content: content,
                private: privatePost
            })
        }

        const response = await fetch("/api/posts", requestOption);
        if (!response.ok) {
            setErrorMsg("Something went wrong");
        } else {
            cleanFormData();
            handleModal();
        }
    }

    const handleCheckBox = () => {
        setPrivatePost(!privatePost);
    }

    return (
        <>
            <ErrorMessage message={errorMsg} />
            <div className={`modal ${modalState}`}>
                <div className="modal-background" onClick={handleModal}></div>
                <div className="modal-card">
                    <header className="modal-card-head has-background-primary-light">
                        <h1 className="modal-card-title">
                            Создать пост
                        </h1>
                    </header>
                    <section className="modal-card-body">
                        <form>
                            <div className="field">
                                <label className="label">Название</label>
                                <div className="control">
                                    <input
                                        type="text"
                                        placeholder="Введите название"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        className="input"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="field">
                                <label className="label">Содержание</label>
                                <div className="control">
                                    <input
                                        type="text"
                                        placeholder="Ваше мнение?"
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        className="input"
                                        required
                                    />
                                </div>
                            </div>

                            <label className="checkbox">
                                <input type="checkbox" onClick={handleCheckBox} /> 🔒 </label>
                        </form>

                    </section>
                    <footer className="modal-card-foot has-background-primary-light">
                        <button className="button is-primary" onClick={handleCreatePost}>
                            Отправить
                        </button>
                        <button className="button" onClick={handleModal}>
                            Закрыть
                        </button>
                    </footer>
                </div>
            </div>
        </>
    );
};
export default PostCreateModal;