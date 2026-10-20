// Recetas que se pueden cocinar con lo marcado en ¿Qué tengo en casa?
// Responsable: Brandon
//
// 1. Lee los ingredientes que checklist.js dejó en sessionStorage ("marcados_busqueda")
// 2. Los manda a POST /api/recomendaciones
// 3. Muestra las recetas y baja hasta ellas

function leerMarcados() {
    try {
        return JSON.parse(sessionStorage.getItem("marcados_busqueda")) || [];
    } catch (error) {
        return [];
    }
}

async function mostrarResultados() {
    const resultados = document.getElementById("resultados");
    const marcados = leerMarcados();

    if (marcados.length === 0) {
        resultados.innerHTML = '<p class="mensaje-error">No marcaste ingredientes. <a href="checklist.html">Elegir ingredientes</a></p>';
        return;
    }

    let etiquetas = "";
    for (const clave of marcados) {
        etiquetas += '<span class="etiqueta">' + escapar(clave.replace(/_/g, " ")) + "</span>";
    }
    document.getElementById("marcados").innerHTML = '<p class="sobretitulo">Con tus ingredientes</p>' + etiquetas;

    try {
        const recetas = await enviarPOST("/api/recomendaciones", { ingredientes: marcados });

        if (recetas.length === 0) {
            resultados.innerHTML = '<p>Con eso todavía no sale ninguna receta. <a href="checklist.html">Prueba marcando más ingredientes</a>.</p>';
            return;
        }

        let html = '<section class="carta"><h2 class="carta-titulo">La carta de hoy</h2>';
        html += '<p class="carta-subtitulo">' + recetas.length + (recetas.length === 1 ? " platillo" : " platillos") + "</p>";
        for (const receta of recetas) {
            html += '<a class="plato" href="receta.html?id=' + escapar(receta.id) + '">';
            html += '<span class="plato-linea"><span class="plato-nombre">' + escapar(receta.nombre) + "</span>";
            html += '<span class="plato-relleno"></span>';
            html += '<span class="plato-tiempo">' + receta.tiempo_min + " min</span></span>";
            html += '<span class="plato-detalle">' + escapar(receta.categoria) + " · " + escapar(receta.dificultad);
            html += " · usa " + receta.usados + " de lo que tienes</span>";
            html += "</a>";
        }
        html += "</section>";
        resultados.innerHTML = html;
        resultados.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        resultados.innerHTML = '<p class="mensaje-error">No se pudo buscar. Revisa que el servidor esté encendido.</p>';
    }
}

mostrarResultados();
