// ¿Qué tengo en casa?
// Responsable: Manrique

// Si no se marcaron, se le pregunta al usuario por ellos
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
            html += '<span class="etiqueta">Usa ' + receta.usados + " de lo que tienes</span>";
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

// Cuadro de "¿Te falta marcar algo?"
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

function agregar(clave) {
    document.querySelector('.casilla input[value="' + clave + '"]').checked = true;
    buscarRecetas();
}

// Con sesión, marca lo que el usuario tiene en su despensa
async function marcarDespensa() {
    const usuario = usuarioActual();
    try {
        const despensa = await pedirGET("/api/despensa/" + usuario.id);
        for (const ingrediente of despensa) {
            const casilla = document.querySelector('.casilla input[value="' + ingrediente.clave + '"]');
            if (casilla) {
                casilla.checked = true;
            }
        }
    } catch (error) {
    }
}

mostrarIngredientes();
if (usuarioActual()) {
    document.getElementById("caja-despensa").classList.remove("oculto");
    document.getElementById("boton-despensa").addEventListener("click", marcarDespensa);
}
document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("boton-buscar").addEventListener("click", buscarRecetas);
