import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom';

const Verify = () => {
    const [params] = useSearchParams();
    const token = params.get("token")
    const [msg, setMsg] = useState("");

    const verifyToken = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/verify/${token}`)
            if (!response.ok) throw new Error("Error al verificar el token");

            const body = await response.json();
            setMsg(body.msg);
        } catch (error) {
            console.log(error)
            setMsg(error.message)
        }
    }

    useEffect(() => {
        verifyToken()
    }, [])
    return (
        <h2>{msg} ✅</h2>
    )
}

export default Verify