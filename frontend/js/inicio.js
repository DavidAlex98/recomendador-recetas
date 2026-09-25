// =====================================================================
// Página de inicio. ARCHIVO DE EJEMPLO (David)
// Muestra el patrón que usan todas las páginas:
//   1. pedir datos a la API
//   2. mostrarlos en la página
//   3. si algo falla, mostrar un mensaje claro
// =====================================================================

async function mostrarEstado() {
    const parrafo = document.getElementById("estado");
    try {
        const estado = await pedirGET("/api/estado");
        if (estado.base_de_datos === "conectada") {
            parrafo.textContent = `Base de datos conectada: ${estado.total_recetas} recetas disponibles.`;
        } else {
            parrafo.textContent = "La base de datos no está conectada. Revisa que MySQL esté encendido y tu archivo .env.";
            parrafo.className = "mensaje-error";
        }
    } catch (error) {
        parrafo.textContent = `No se pudo consultar el servidor: ${error.message}`;
        parrafo.className = "mensaje-error";
    }
}

async function mostrarCategorias() {
    const contenedor = document.getElementById("categorias");
    try {
        const categorias = await pedirGET("/api/categorias");
        // escapar() protege el texto antes de meterlo en el HTML
        contenedor.innerHTML = categorias
            .map(categoria => `<span class="etiqueta">${escapar(categoria)}</span>`)
            .join("");
    } catch (error) {
        contenedor.textContent = `No se pudieron cargar las categorías: ${error.message}`;
        contenedor.className = "mensaje-error";
    }
}

// Se ejecuta cuando la página termina de cargar
document.addEventListener("DOMContentLoaded", () => {
    mostrarEstado();
    mostrarCategorias();
});
