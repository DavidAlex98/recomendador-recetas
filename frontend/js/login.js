// Iniciar sesión
// Responsable: Brandon

document.getElementById("formulario").addEventListener("submit", async function (evento) {
    evento.preventDefault();
    const mensaje = document.getElementById("mensaje");
    mensaje.textContent = "";

    try {
        const usuario = await enviarPOST("/api/login", {
            correo: document.getElementById("correo").value,
            contrasena: document.getElementById("contrasena").value,
        });
        localStorage.setItem("usuario", JSON.stringify(usuario));
        window.location.href = "index.html";
    } catch (error) {
        if (error.status === 401) {
            mensaje.textContent = "Correo o contraseña incorrectos.";
        } else {
            mensaje.textContent = "No se pudo conectar con el servidor.";
        }
    }
});
