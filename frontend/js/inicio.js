// Página de inicio
// Responsable: David

async function mostrarEstado() {
    const parrafo = document.getElementById("estado");
    try {
        const estado = await pedirGET("/api/estado");
        if (estado.base_de_datos === "conectada") {
            parrafo.textContent = "Base de datos conectada: " + estado.total_recetas + " recetas disponibles.";
        } else {
            parrafo.textContent = "La base de datos no está conectada. Revisa PostgreSQL y tu archivo .env.";
            parrafo.className = "mensaje-error";
        }
    } catch (error) {
        parrafo.textContent = "No se pudo conectar con el servidor.";
        parrafo.className = "mensaje-error";
    }
}

async function mostrarCategorias() {
    const contenedor = document.getElementById("categorias");
    try {
        const categorias = await pedirGET("/api/categorias");
        let html = "";
        for (const categoria of categorias) {
            html += '<span class="etiqueta">' + escapar(categoria) + "</span>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.textContent = "No se pudieron cargar las categorías.";
        contenedor.className = "mensaje-error";
    }
}

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

mostrarEstado();
mostrarCategorias();
mostrarHistorial();
