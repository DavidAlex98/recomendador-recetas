// Funciones que usan todas las páginas.
// Responsable: David
//
// En tu página ponlo antes de tu propio .js:
//     <script src="js/api.js"></script>
//     <script src="js/mi-pagina.js"></script>

// Pedir datos a la API
// Ejemplo:  const categorias = await pedirGET("/api/categorias");
async function pedirGET(url) {
    const respuesta = await fetch(url);
    if (!respuesta.ok) {
        throw new Error("Error " + respuesta.status);
    }
    return await respuesta.json();
}

// Mandar datos a la API
// Ejemplo:  await enviarPOST("/api/login", { correo: "a@b.com", contrasena: "123" });
async function enviarPOST(url, datos) {
    const respuesta = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
    });
    if (!respuesta.ok) {
        throw new Error("Error " + respuesta.status);
    }
    return await respuesta.json();
}

// Protege el texto antes de ponerlo en la página con innerHTML,
// para que nadie pueda meter código. Úsalo con datos que vengan de la API.
function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
}
