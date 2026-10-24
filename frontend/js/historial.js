// Lo último que viste
// Responsable: Brandon
//
// Pide a /api/historial/{usuario_id} las últimas recetas que abrió el usuario.

const usuario = requerirSesion();

async function mostrarHistorial() {
    const contenedor = document.getElementById("historial");
    try {
        const recetas = await pedirGET("/api/historial/" + usuario.id);
        if (recetas.length === 0) {
            contenedor.innerHTML = '<p class="pendiente">Todavía no has visto recetas. ' +
                'Busca recetas en <a href="checklist.html">¿Qué tengo en casa?</a></p>';
            return;
        }
        let html = "";
        for (const receta of recetas) {
            const fecha = new Date(receta.visto_en).toLocaleDateString("es-GT", { day: "numeric", month: "short" });
            html += '<a class="tarjeta receta" href="receta.html?id=' + escapar(receta.id) + '">';
            html += "<strong>" + escapar(receta.nombre) + "</strong><br>";
            html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
            html += '<span class="etiqueta">visto el ' + escapar(fecha) + "</span>";
            html += "</a>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se pudo cargar tu historial.</p>';
    }
}

if (usuario) {
    mostrarHistorial();
}
