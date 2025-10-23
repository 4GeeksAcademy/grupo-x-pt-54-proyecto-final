import { useState } from "react";

export default function Home() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");

	const handleSubmit = async (e) => {
		e.preventDefault();
		await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/registro`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email, password }),
		});
		alert("Revisa tu correo para verificar la cuenta");
	};

	return (
		<form onSubmit={handleSubmit}>
			<h2>Registro</h2>
			<input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
			<input placeholder="Contraseña" type="password" onChange={(e) => setPassword(e.target.value)} />
			<button type="submit">Registrar</button>
		</form>
	);
}