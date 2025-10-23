import React, { useState } from 'react'

const Forgot = () => {
    const [email, setEmail] = useState("");

    const handleSubmit = async () => {

        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/forgot`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email })
            });
            if (!response.ok) throw new Error("Error al tratar de recuperar contraseña.");

            alert("Revisa tu correo para recuperar tu contraseña.");

        } catch (error) {
            console.log(error)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <h2>Recuperar Contraseña</h2>
            <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
            <button type="submit">Enviar</button>
        </form>
    );
}

export default Forgot