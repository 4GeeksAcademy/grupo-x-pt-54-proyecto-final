import React, { useState } from 'react'
import { useSearchParams } from 'react-router-dom';

const Reset = () => {
    const [params] = useSearchParams();
    const token = params.get("token")
    const [password, setPassword] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/reset/${token}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password: password }),
        });
        alert("Contraseña actualizada");
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Restablecer Contraseña</h2>
            <input type="password" placeholder="Nueva contraseña" onChange={(e) => setPassword(e.target.value)} />
            <button type="submit">Actualizar</button>
        </form>
    );
}

export default Reset