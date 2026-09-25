// =====================================================================
// Funciones compartidas por todas las páginas.
// Responsable: David
//
// Inclúyelo en tu página ANTES de tu propio archivo .js:
//     <script src="js/api.js"></script>
//     <script src="js/mi-pagina.js"></script>
// =====================================================================

// Pide datos a la API con GET.
// Ejemplo:  const recetas = await pedirGET("/api/recetas?buscar=pepian");
async function pedirGET(url) {
    const respuesta = await fetch(url);
    return leerRespuesta(respuesta);
}

// Envía datos a la API con POST (en formato JSON).
// Ejemplo:  await enviarPOST("/api/validar-ingredientes", { ingredientes: ["cebolla"] });
async function enviarPOST(url, datos) {
    const respuesta = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
    });
    return leerRespuesta(respuesta);
}

// Convierte la respuesta en datos. Si la API respondió con error, lanza
// un Error con el mensaje que mandó FastAPI (el "detail" del HTTPException).
async function leerRespuesta(respuesta) {
    const datos = await respuesta.json().catch(() => null);
    if (!respuesta.ok) {
        const mensaje = datos && datos.detail ? datos.detail : `Error ${respuesta.status}`;
        throw new Error(typeof mensaje === "string" ? mensaje : JSON.stringify(mensaje));
    }
    return datos;
}

// Protege el texto antes de meterlo en innerHTML.
// Úsalo SIEMPRE con datos que vengan de la API o del usuario, así un texto
// como "<script>..." se muestra como texto y no se ejecuta.
// Ejemplo:  tarjeta.innerHTML = `<h3>${escapar(receta.nombre)}</h3>`;
function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = texto ?? "";
    return div.innerHTML;
}
