// ¿Qué tengo en casa?
// Responsable: Manrique

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

// Guarda lo marcado y abre la página con las recetas
function buscarRecetas() {
    const marcados = [];
    for (const casilla of document.querySelectorAll(".casilla input:checked")) {
        marcados.push(casilla.value);
    }

    if (marcados.length === 0) {
        document.getElementById("resultados").innerHTML = '<p class="mensaje-error">Marca al menos un ingrediente.</p>';
        return;
    }

    sessionStorage.setItem("marcados_busqueda", JSON.stringify(marcados));
    window.location.href = "resultados.html";
}

// Con sesión, marca lo que el usuario tiene en su despensa
// Es un botón de dos estados: la segunda vez desmarca lo que había marcado la primera
let marcadosPorDespensa = [];

async function alternarDespensa() {
    const boton = document.getElementById("boton-despensa");

    if (marcadosPorDespensa.length > 0) {
        for (const casilla of marcadosPorDespensa) {
            casilla.checked = false;
        }
        marcadosPorDespensa = [];
        boton.textContent = "Marcar lo de mi despensa";
        contarMarcados();
        return;
    }

    const usuario = usuarioActual();
    try {
        const despensa = await pedirGET("/api/despensa/" + usuario.id);
        for (const ingrediente of despensa) {
            const casilla = document.querySelector('.casilla input[value="' + ingrediente.clave + '"]');
            if (casilla && !casilla.checked) {
                casilla.checked = true;
                marcadosPorDespensa.push(casilla);
            }
        }
        if (marcadosPorDespensa.length > 0) {
            boton.textContent = "Desmarcar lo de mi despensa";
        }
        contarMarcados();
    } catch (error) {
    }
}

// Muestra en el botón cuántos ingredientes hay marcados
function contarMarcados() {
    const total = document.querySelectorAll(".casilla input:checked").length;
    const boton = document.getElementById("boton-buscar");
    boton.textContent = total > 0 ? "Ver qué puedo cocinar · " + total : "Ver qué puedo cocinar";
}

// Si llegaste desde "Escanear", marca los ingredientes encontrados y busca las recetas
function marcarEscaneados() {
    const guardados = sessionStorage.getItem("marcados");
    if (!guardados) {
        return;
    }
    sessionStorage.removeItem("marcados");
    for (const clave of JSON.parse(guardados)) {
        const casilla = document.querySelector('.casilla input[value="' + clave + '"]');
        if (casilla) {
            casilla.checked = true;
        }
    }
    contarMarcados();
    buscarRecetas();
}

mostrarIngredientes().then(marcarEscaneados);
document.getElementById("ingredientes").addEventListener("change", contarMarcados);
if (usuarioActual()) {
    document.getElementById("caja-despensa").classList.remove("oculto");
    document.getElementById("boton-despensa").addEventListener("click", alternarDespensa);
}
document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("boton-buscar").addEventListener("click", buscarRecetas);
