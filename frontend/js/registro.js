// Crear cuenta
// Responsable: Rubí

document.getElementById("formulario").addEventListener("submit", async function (evento) {
    evento.preventDefault();
    const mensaje = document.getElementById("mensaje");
    mensaje.textContent = "";

    const nombre = document.getElementById("nombre").value;
    const correo = document.getElementById("correo").value;
    const contrasena = document.getElementById("contrasena").value;

    if (contrasena !== document.getElementById("confirmar").value) {
        mensaje.textContent = "Las contraseñas no son iguales.";
        return;
    }

    try {
        await enviarPOST("/api/registro", { nombre: nombre, correo: correo, contrasena: contrasena });
        const usuario = await enviarPOST("/api/login", { correo: correo, contrasena: contrasena });
        localStorage.setItem("usuario", JSON.stringify(usuario));
        window.location.href = "index.html";
    } catch (error) {
        mensaje.textContent = error.message;
    }
});
