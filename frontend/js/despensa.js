// Mi despensa
// Responsable: Shanda

const usuario = requerirSesion();
let guardados = [];   // claves que el usuario tiene en su despensa

async function cargarDespensa() {
    const lista = await pedirGET("/api/despensa/" + usuario.id);
    guardados = [];
    let html = "";
    for (const ingrediente of lista) {
        guardados.push(ingrediente.clave);
        html += '<button class="etiqueta quitar" onclick="quitar(\'' + escapar(ingrediente.clave) + '\')" title="Quitar">';
        html += escapar(ingrediente.nombre) + " ✕</button>";
    }
    if (html === "") {
        html = '<p class="pendiente">Todavía no tienes nada guardado. Marca ingredientes abajo.</p>';
    }
    document.getElementById("guardados").innerHTML = html;
}

async function mostrarIngredientes() {
    const contenedor = document.getElementById("ingredientes");
    const categorias = await pedirGET("/api/ingredientes");
    let html = "";
    for (const categoria in categorias) {
        html += '<section class="tarjeta">';
        html += '<h3 class="categoria">' + escapar(categoria) + "</h3>";
        for (const ingrediente of categorias[categoria]) {
            const marcado = guardados.includes(ingrediente.clave) ? " checked" : "";
            html += '<label class="casilla">';
            html += '<input type="checkbox" value="' + escapar(ingrediente.clave) + '"' + marcado + "> ";
            html += escapar(ingrediente.nombre);
            html += "</label>";
        }
        html += "</section>";
    }
    contenedor.innerHTML = html;

    for (const casilla of contenedor.querySelectorAll("input")) {
        casilla.addEventListener("change", cambiarCasilla);
    }
}

// Al marcar se guarda; al desmarcar se quita
async function cambiarCasilla(evento) {
    const casilla = evento.target;
    const mensaje = document.getElementById("mensaje");
    mensaje.textContent = "";
    try {
        if (casilla.checked) {
            await enviarPOST("/api/despensa/" + usuario.id, { clave: casilla.value });
        } else {
            await enviarDELETE("/api/despensa/" + usuario.id + "/" + casilla.value);
        }
        await cargarDespensa();
    } catch (error) {
        casilla.checked = !casilla.checked;
        mensaje.textContent = "No se pudo guardar: " + error.message;
    }
}

async function quitar(clave) {
    try {
        await enviarDELETE("/api/despensa/" + usuario.id + "/" + clave);
        const casilla = document.querySelector('.casilla input[value="' + clave + '"]');
        if (casilla) {
            casilla.checked = false;
        }
        await cargarDespensa();
    } catch (error) {
        document.getElementById("mensaje").textContent = "No se pudo quitar: " + error.message;
    }
}

function filtrar() {
    const texto = document.getElementById("buscador").value.toLowerCase();
    for (const casilla of document.querySelectorAll(".casilla")) {
        casilla.style.display = casilla.textContent.toLowerCase().includes(texto) ? "" : "none";
    }
}

async function verRecetas() {
    const resultados = document.getElementById("resultados");
    if (guardados.length === 0) {
        resultados.innerHTML = '<p class="mensaje-error">Primero guarda algún ingrediente.</p>';
        return;
    }
    resultados.innerHTML = "<p>Buscando...</p>";
    try {
        const recetas = await enviarPOST("/api/recomendaciones", { ingredientes: guardados });
        if (recetas.length === 0) {
            resultados.innerHTML = "<p>Con tu despensa todavía no sale ninguna receta. Agrega más ingredientes.</p>";
            return;
        }
        let html = "<h2>Puedes cocinar " + recetas.length + " recetas</h2>";
        for (const receta of recetas.slice(0, 30)) {
            html += '<a class="tarjeta receta" href="receta.html?id=' + escapar(receta.id) + '">';
            html += "<strong>" + escapar(receta.nombre) + "</strong><br>";
            html += '<span class="etiqueta">Usa ' + receta.usados + " de lo que tienes</span>";
            html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
            html += '<span class="etiqueta">' + receta.tiempo_min + " min</span>";
            html += "</a>";
        }
        resultados.innerHTML = html;
    } catch (error) {
        resultados.innerHTML = '<p class="mensaje-error">No se pudo buscar. Revisa que el servidor esté encendido.</p>';
    }
}

async function iniciar() {
    if (!usuario) {
        return;
    }
    try {
        await cargarDespensa();
        await mostrarIngredientes();
    } catch (error) {
        document.getElementById("guardados").innerHTML = '<p class="mensaje-error">No se pudo cargar tu despensa.</p>';
    }
}

iniciar();
document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("boton-cocinar").addEventListener("click", verRecetas);
