// ¿Qué tengo en casa?
// Responsable: Manrique
//
// 1. Muestra los ingredientes con casillas, agrupados por categoría
// 2. El buscador esconde los que no coinciden
// 3. El botón manda los marcados a /api/recomendaciones y muestra las recetas
// 4. Si no marcaste cosas que casi toda casa tiene, te pregunta por ellas

// Cosas que casi siempre hay en casa (se le recuerdan al usuario si no las marcó)
const COMUNES = ["ajo", "cebolla", "tomate", "limon", "huevo", "tortilla_maiz", "frijol_negro", "arroz"];

async function mostrarIngredientes() {
    const contenedor = document.getElementById("ingredientes");
    try {
        const categorias = await pedirGET("/api/ingredientes");
        let html = "";
        for (const categoria in categorias) {
            html += '<section class="tarjeta">';
            html += "<h3 class=\"categoria\">" + escapar(categoria) + "</h3>";
            for (const ingrediente of categorias[categoria]) {
                html += '<label class="casilla">';
                html += '<input type="checkbox" value="' + escapar(ingrediente.clave) + '"> ';
                html += escapar(ingrediente.nombre);
                html += "</label>";
            }
            html += "</section>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.textContent = "No se pudieron cargar los ingredientes.";
        contenedor.className = "mensaje-error";
    }
}

function filtrar() {
    const texto = document.getElementById("buscador").value.toLowerCase();
    const casillas = document.querySelectorAll(".casilla");
    for (const casilla of casillas) {
        if (casilla.textContent.toLowerCase().includes(texto)) {
            casilla.style.display = "";
        } else {
            casilla.style.display = "none";
        }
    }
}

async function buscarRecetas() {
    const resultados = document.getElementById("resultados");

    // Juntar las claves de las casillas marcadas
    const marcados = [];
    const casillas = document.querySelectorAll(".casilla input:checked");
    for (const casilla of casillas) {
        marcados.push(casilla.value);
    }

    if (marcados.length === 0) {
        resultados.innerHTML = '<p class="mensaje-error">Marca al menos un ingrediente.</p>';
        return;
    }

    mostrarSugerencias(marcados);
    resultados.innerHTML = "<p>Buscando...</p>";
    try {
        const recetas = await enviarPOST("/api/recomendaciones", { ingredientes: marcados });

        if (recetas.length === 0) {
            resultados.innerHTML = "<p>Con eso todavía no sale ninguna receta. Prueba marcando más ingredientes.</p>";
            return;
        }

        let html = "<h2>Puedes cocinar " + recetas.length + " recetas</h2>";
        for (const receta of recetas) {
            html += '<a class="tarjeta receta" href="receta.html?id=' + escapar(receta.id) + '">';
            html += "<strong>" + escapar(receta.nombre) + "</strong><br>";
            html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
            html += '<span class="etiqueta">' + receta.tiempo_min + " min</span>";
            html += '<span class="etiqueta">' + escapar(receta.dificultad) + "</span>";
            html += "</a>";
        }
        resultados.innerHTML = html;
    } catch (error) {
        resultados.innerHTML = '<p class="mensaje-error">No se pudo buscar. Revisa que el servidor esté encendido.</p>';
    }
}

// Cuadro de "¿Te falta marcar algo?" con las cosas comunes que no marcó
function mostrarSugerencias(marcados) {
    const cuadro = document.getElementById("sugerencias");
    let botones = "";
    for (const clave of COMUNES) {
        if (!marcados.includes(clave)) {
            const casilla = document.querySelector('.casilla input[value="' + clave + '"]');
            const nombre = casilla.parentElement.textContent.trim();
            botones += '<button class="etiqueta sugerencia" onclick="agregar(\'' + clave + '\')">+ ' + escapar(nombre) + "</button>";
        }
    }

    if (botones === "") {
        cuadro.innerHTML = "";
    } else {
        cuadro.innerHTML = '<div class="tarjeta aviso"><strong>¿Te falta marcar algo?</strong> ' +
            "Casi toda casa tiene esto. Si lo tienes, tócalo y buscamos otra vez:<br>" + botones + "</div>";
    }
}

// Marca la casilla del ingrediente y vuelve a buscar
function agregar(clave) {
    document.querySelector('.casilla input[value="' + clave + '"]').checked = true;
    buscarRecetas();
}

// Cuando la página termina de cargar
mostrarIngredientes();
document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("boton-buscar").addEventListener("click", buscarRecetas);
