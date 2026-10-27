// Página de inicio
// Responsable: David

// Con sesión: las últimas recetas que vio
async function mostrarHistorial() {
    const usuario = usuarioActual();
    if (!usuario) {
        return;
    }
    try {
        const recetas = await pedirGET("/api/historial/" + usuario.id);
        if (recetas.length === 0) {
            return;
        }
        let html = "";
        for (const receta of recetas) {
            html += '<a class="etiqueta" href="receta.html?id=' + escapar(receta.id) + '">' + escapar(receta.nombre) + "</a>";
        }
        document.getElementById("historial").innerHTML = html;
        document.getElementById("caja-historial").classList.remove("oculto");
    } catch (error) {
    }
}

mostrarHistorial();
