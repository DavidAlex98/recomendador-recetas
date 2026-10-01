// Página de una receta
// Responsable: David
//
// 1. Lee el id de la dirección, por ejemplo receta.html?id=gt-0001
// 2. Pide la receta a /api/recetas/{id}
// 3. Muestra los datos, los ingredientes y los pasos

async function mostrarReceta() {
    const contenedor = document.getElementById("receta");

    // Leer el id que viene en la dirección
    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) {
        contenedor.innerHTML = '<p class="mensaje-error">No se indicó qué receta mostrar.</p>';
        return;
    }

    try {
        const receta = await pedirGET("/api/recetas/" + id);

        // Título y datos
        let html = "<h1>" + escapar(receta.nombre) + "</h1>";
        html += "<p>" + escapar(receta.descripcion) + "</p>";
        html += '<p>';
        html += '<span class="etiqueta">' + receta.tiempo_min + " min</span>";
        html += '<span class="etiqueta">' + escapar(receta.dificultad) + "</span>";
        html += '<span class="etiqueta">' + receta.porciones + " porciones</span>";
        html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
        if (receta.vegetariano) {
            html += '<span class="etiqueta">vegetariana</span>';
        }
        html += "</p>";

        // Ingredientes
        html += '<section class="tarjeta"><h3>Ingredientes</h3><ul>';
        for (const ingrediente of receta.ingredientes) {
            html += "<li>";
            html += escapar(ingrediente.nombre);
            if (ingrediente.cantidad) {
                html += " · " + Number(ingrediente.cantidad) + " " + escapar(ingrediente.unidad);
            }
            if (ingrediente.opcional) {
                html += ' <span class="pendiente">(opcional)</span>';
            }
            html += "</li>";
        }
        html += "</ul></section>";

        // Pasos
        html += '<section class="tarjeta"><h3>Preparación</h3><ol>';
        for (const paso of receta.pasos) {
            html += "<li>" + escapar(paso.instruccion) + "</li>";
        }
        html += "</ol></section>";

        contenedor.innerHTML = html;
        document.title = receta.nombre + " · RecetApp";
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se encontró la receta.</p>';
    }
}

// Cuando la página termina de cargar
mostrarReceta();
