// Página de inicio. EJEMPLO para las demás páginas.
// Responsable: David
//
// Siempre es lo mismo: pedir datos a la API y mostrarlos en la página.

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

// Cuando la página termina de cargar
mostrarEstado();
mostrarCategorias();
