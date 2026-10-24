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

// Sin tildes, mayúsculas ni símbolos: "Limón", "limon" y "LIMÓN!" se consideran iguales
const SIN_TILDE = { "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u" };

function simplificar(texto) {
    texto = texto.toLowerCase();
    let resultado = "";
    let huboEspacio = false;
    for (let i = 0; i < texto.length; i++) {
        let letra = texto[i];
        if (SIN_TILDE[letra]) {
            letra = SIN_TILDE[letra];
        }
        const esLetra = letra >= "a" && letra <= "z";
        const esNumero = letra >= "0" && letra <= "9";
        const esN = letra === "ñ";
        if (esLetra || esNumero || esN) {
            resultado = resultado + letra;
            huboEspacio = false;
        } else if (!huboEspacio) {
            resultado = resultado + " ";
            huboEspacio = true;
        }
    }
    return resultado.trim();
}

function filtrar() {
    const texto = simplificar(document.getElementById("buscador").value);
    const casillas = document.querySelectorAll(".casilla");
    for (const casilla of casillas) {
        if (simplificar(casilla.textContent).includes(texto)) {
            casilla.style.display = "";
        } else {
            casilla.style.display = "none";
        }
    }

    // Se esconden las categorías sin coincidencias, así el ingrediente queda justo debajo del buscador
    for (const seccion of document.querySelectorAll("#ingredientes section")) {
        let hayCoincidencias = false;
        for (const casilla of seccion.querySelectorAll(".casilla")) {
            if (casilla.style.display !== "none") {
                hayCoincidencias = true;
            }
        }
        if (hayCoincidencias) {
            seccion.style.display = "";
        } else {
            seccion.style.display = "none";
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
    if (total > 0) {
        boton.textContent = "Ver qué puedo cocinar · " + total;
    } else {
        boton.textContent = "Ver qué puedo cocinar";
    }
    mostrarSugerencias();
}

// Cuadro de "¿Te falta marcar algo?" con los ingredientes comunes que no están marcados
function mostrarSugerencias() {
    const cuadro = document.getElementById("sugerencias");
    let botones = "";
    for (const clave of COMUNES) {
        const casilla = document.querySelector('.casilla input[value="' + clave + '"]');
        if (casilla && !casilla.checked) {
            const nombre = casilla.parentElement.textContent.trim();
            botones += '<button type="button" class="etiqueta sugerencia" onclick="agregar(\'' + clave + '\')">+ ' + escapar(nombre) + "</button>";
        }
    }

    if (botones === "") {
        cuadro.innerHTML = "";
    } else {
        cuadro.innerHTML = '<div class="tarjeta aviso"><strong>¿Te falta marcar algo?</strong> ' +
            "Casi toda casa tiene esto. Si lo tienes, tócalo:<br>" + botones + "</div>";
    }
}

function agregar(clave) {
    document.querySelector('.casilla input[value="' + clave + '"]').checked = true;
    contarMarcados();
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

mostrarIngredientes().then(function () {
    contarMarcados();
    marcarEscaneados();
});
document.getElementById("ingredientes").addEventListener("change", contarMarcados);
if (usuarioActual()) {
    document.getElementById("caja-despensa").classList.remove("oculto");
    document.getElementById("boton-despensa").addEventListener("click", alternarDespensa);
}
document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("boton-buscar").addEventListener("click", buscarRecetas);
