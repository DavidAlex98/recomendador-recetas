// Crear cuenta
// Responsable: Rubí
//
// 1. Revisa que las dos contraseñas sean iguales
// 2. Manda los datos a /api/registro
// 3. Si sale bien, inicia sesión de una vez y manda al inicio

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
        // El servidor dice qué pasó, por ejemplo "El correo ya está registrado"
        mensaje.textContent = error.message;
    }
});
