// Panel de administración
// Responsable: Brandon
//
// Solo entra un usuario con rol "admin". Todas las llamadas mandan ?admin_id=
// para que el servidor revise que de verdad sea admin.
//
// 1. Reporte: usuarios, propuestas, recetas populares y por categoría
// 2. Propuestas pendientes: aprobar (y completarla como receta) o rechazar
// 3. Recetas: buscar, crear, editar y borrar
// 4. Bitácora: últimas acciones

const usuario = requerirSesion();
const CLAVE = usuario ? "?admin_id=" + usuario.id : "";
let editando = null;           // id de la receta que se edita, o null si es nueva

// ---------- Reporte ----------

async function mostrarReporte() {
    const caja = document.getElementById("reporte");
    try {
        const datos = await pedirGET("/api/admin/reporte" + CLAVE);

        let html = '<div class="numeros">';
        html += '<div class="numero"><strong>' + datos.total_usuarios + "</strong><span>usuarios</span></div>";
        for (const fila of datos.propuestas_por_estado) {
            html += '<div class="numero"><strong>' + fila.total + "</strong><span>propuestas " + escapar(fila.estado) + "s</span></div>";
        }
        let totalRecetas = 0;
        for (const fila of datos.recetas_por_categoria) {
            totalRecetas = totalRecetas + fila.total;
        }
        html += '<div class="numero"><strong>' + totalRecetas + "</strong><span>recetas</span></div>";
        html += "</div>";

        html += "<h4>Recetas más populares</h4>";
        if (datos.recetas_populares.length === 0) {
            html += '<p class="pendiente">Todavía nadie ha guardado ni visto recetas.</p>';
        } else {
            html += '<table class="tabla"><tr><th>Receta</th><th>Favorita</th><th>Vista</th></tr>';
            for (const receta of datos.recetas_populares) {
                html += '<tr><td><a href="receta.html?id=' + escapar(receta.id) + '">' + escapar(receta.nombre) + "</a></td>";
                html += "<td>" + receta.veces_favorita + "</td><td>" + receta.veces_vista + "</td></tr>";
            }
            html += "</table>";
        }

        html += "<h4>Usuarios</h4>";
        html += '<table class="tabla"><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Despensa</th><th>Favoritos</th><th>Plan</th></tr>';
        for (const persona of datos.usuarios) {
            html += "<tr><td>" + escapar(persona.nombre) + "</td><td>" + escapar(persona.correo) + "</td>";
            html += "<td>" + escapar(persona.rol) + "</td><td>" + persona.en_despensa + "</td>";
            html += "<td>" + persona.favoritos + "</td><td>" + persona.en_plan + "</td></tr>";
        }
        html += "</table>";

        html += "<h4>Recetas por categoría</h4><p>";
        for (const fila of datos.recetas_por_categoria) {
            html += '<span class="etiqueta">' + escapar(fila.categoria) + ": " + fila.total + "</span>";
        }
        html += "</p>";

        caja.innerHTML = html;
    } catch (error) {
        caja.innerHTML = '<p class="mensaje-error">' + escapar(error.message) + "</p>";
    }
}

// ---------- Propuestas ----------

async function mostrarPropuestas() {
    const caja = document.getElementById("propuestas");
    try {
        const propuestas = await pedirGET("/api/admin/propuestas" + CLAVE);
        if (propuestas.length === 0) {
            caja.innerHTML = '<p class="pendiente">No hay propuestas pendientes.</p>';
            return;
        }
        let html = "";
        for (const propuesta of propuestas) {
            html += '<div class="fila-plan">';
            html += "<strong>" + escapar(propuesta.nombre) + "</strong> · de " + escapar(propuesta.usuario);
            if (propuesta.descripcion) {
                html += '<br><span class="pendiente">' + escapar(propuesta.descripcion) + "</span>";
            }
            html += '<div class="acciones">';
            html += '<button class="boton boton-chico" onclick="aprobar(' + propuesta.id + ')">Aprobar</button>';
            html += '<input id="motivo-' + propuesta.id + '" class="selector" type="text" placeholder="Motivo del rechazo">';
            html += '<button class="boton boton-chico boton-gris" onclick="rechazar(' + propuesta.id + ')">Rechazar</button>';
            html += "</div></div>";
        }
        caja.innerHTML = html;
    } catch (error) {
        caja.innerHTML = '<p class="mensaje-error">' + escapar(error.message) + "</p>";
    }
}

// Al aprobar, se abre el formulario con el nombre y la descripción
// para que el admin la complete y la guarde como receta.
async function aprobar(id) {
    try {
        const respuesta = await enviarPUT("/api/admin/propuestas/" + id + "/aprobar" + CLAVE);
        abrirFormulario(null);
        document.getElementById("r-nombre").value = respuesta.nombre;
        document.getElementById("r-descripcion").value = respuesta.descripcion || "";
        avisarReceta("Propuesta aprobada. Completa los ingredientes y pasos y guárdala.", false);
        mostrarPropuestas();
        mostrarReporte();
        mostrarBitacora();
    } catch (error) {
        document.getElementById("propuestas").insertAdjacentHTML("afterbegin", '<p class="mensaje-error">' + escapar(error.message) + "</p>");
    }
}

async function rechazar(id) {
    const motivo = document.getElementById("motivo-" + id).value;
    try {
        await enviarPUT("/api/admin/propuestas/" + id + "/rechazar" + CLAVE, { motivo: motivo });
        mostrarPropuestas();
        mostrarReporte();
        mostrarBitacora();
    } catch (error) {
        document.getElementById("motivo-" + id).placeholder = error.message;
    }
}

// ---------- Recetas: buscar, borrar ----------

async function buscarRecetas() {
    const texto = document.getElementById("buscar-receta").value.trim();
    const caja = document.getElementById("lista-recetas");
    if (texto.length < 2) {
        caja.innerHTML = "";
        return;
    }
    try {
        const recetas = await pedirGET("/api/recetas?buscar=" + encodeURIComponent(texto));
        let html = "";
        for (const receta of recetas.slice(0, 15)) {
            const id = escapar(receta.id);
            html += '<div class="fila-plan">';
            html += '<a href="receta.html?id=' + id + '">' + escapar(receta.nombre) + "</a> ";
            html += '<span class="etiqueta">' + id + "</span>";
            html += '<span class="acciones" id="acciones-' + id + '">';
            html += '<button class="boton boton-chico" onclick="editar(\'' + id + '\')">Editar</button>';
            html += '<button class="boton boton-chico boton-gris" onclick="pedirBorrar(\'' + id + '\')">Borrar</button>';
            html += "</span></div>";
        }
        caja.innerHTML = html || '<p class="pendiente">No hay recetas con ese nombre.</p>';
    } catch (error) {
        caja.innerHTML = '<p class="mensaje-error">' + escapar(error.message) + "</p>";
    }
}

// Borrar pide confirmar con un segundo botón
function pedirBorrar(id) {
    document.getElementById("acciones-" + id).innerHTML =
        '¿Seguro? <button class="boton boton-chico boton-peligro" onclick="borrar(\'' + id + '\')">Sí, borrar</button>' +
        '<button class="boton boton-chico boton-gris" onclick="buscarRecetas()">No</button>';
}

async function borrar(id) {
    try {
        await enviarDELETE("/api/admin/recetas/" + id + CLAVE);
        buscarRecetas();
        mostrarReporte();
        mostrarBitacora();
    } catch (error) {
        document.getElementById("acciones-" + id).textContent = error.message;
    }
}

// ---------- Recetas: formulario ----------

function filaIngrediente(ingrediente) {
    const fila = document.createElement("div");
    fila.className = "fila-ingrediente";
    fila.innerHTML =
        '<input class="selector i-clave" list="catalogo" placeholder="Ingrediente (ej. tomate)" required>' +
        '<input class="selector i-cantidad" type="number" step="any" min="0" placeholder="Cantidad">' +
        '<input class="selector i-unidad" type="text" placeholder="Unidad (ej. libra)">' +
        '<label><input class="i-opcional" type="checkbox"> opcional</label>' +
        '<button type="button" class="boton boton-chico boton-gris">✕</button>';
    if (ingrediente) {
        fila.querySelector(".i-clave").value = ingrediente.clave;
        fila.querySelector(".i-cantidad").value = ingrediente.cantidad === null ? "" : Number(ingrediente.cantidad);
        fila.querySelector(".i-unidad").value = ingrediente.unidad || "";
        fila.querySelector(".i-opcional").checked = ingrediente.opcional;
    }
    fila.querySelector("button").addEventListener("click", function () {
        fila.remove();
    });
    document.getElementById("r-ingredientes").appendChild(fila);
}

function abrirFormulario(receta) {
    editando = receta ? receta.id : null;
    document.getElementById("titulo-formulario").textContent = receta ? "Editar " + receta.id : "Nueva receta";
    document.getElementById("formulario-receta").reset();
    document.getElementById("r-ingredientes").innerHTML = "";
    avisarReceta("", false);

    if (receta) {
        document.getElementById("r-nombre").value = receta.nombre;
        document.getElementById("r-categoria").value = receta.categoria;
        document.getElementById("r-descripcion").value = receta.descripcion || "";
        document.getElementById("r-dificultad").value = receta.dificultad;
        document.getElementById("r-tiempo").value = receta.tiempo_min;
        document.getElementById("r-porciones").value = receta.porciones;
        document.getElementById("r-vegetariano").checked = receta.vegetariano;
        document.getElementById("r-vegano").checked = receta.vegano;
        document.getElementById("r-sin-gluten").checked = receta.sin_gluten;
        for (const ingrediente of receta.ingredientes) {
            filaIngrediente(ingrediente);
        }
        const pasos = [];
        for (const paso of receta.pasos) {
            pasos.push(paso.instruccion);
        }
        document.getElementById("r-pasos").value = pasos.join("\n");
    } else {
        filaIngrediente(null);
    }

    const caja = document.getElementById("caja-formulario");
    caja.classList.remove("oculto");
    caja.scrollIntoView({ behavior: "smooth" });
}

async function editar(id) {
    try {
        abrirFormulario(await pedirGET("/api/recetas/" + id));
    } catch (error) {
        document.getElementById("lista-recetas").innerHTML = '<p class="mensaje-error">' + escapar(error.message) + "</p>";
    }
}

function avisarReceta(texto, esError) {
    const mensaje = document.getElementById("mensaje-receta");
    mensaje.className = esError ? "mensaje-error" : "mensaje-ok";
    mensaje.textContent = texto;
}

async function guardarReceta(evento) {
    evento.preventDefault();

    const ingredientes = [];
    for (const fila of document.querySelectorAll(".fila-ingrediente")) {
        const cantidad = fila.querySelector(".i-cantidad").value;
        ingredientes.push({
            clave: fila.querySelector(".i-clave").value.trim(),
            cantidad: cantidad === "" ? null : Number(cantidad),
            unidad: fila.querySelector(".i-unidad").value.trim(),
            opcional: fila.querySelector(".i-opcional").checked,
        });
    }

    const datos = {
        nombre: document.getElementById("r-nombre").value,
        categoria: document.getElementById("r-categoria").value,
        descripcion: document.getElementById("r-descripcion").value,
        dificultad: document.getElementById("r-dificultad").value,
        tiempo_min: Number(document.getElementById("r-tiempo").value),
        porciones: Number(document.getElementById("r-porciones").value),
        vegetariano: document.getElementById("r-vegetariano").checked,
        vegano: document.getElementById("r-vegano").checked,
        sin_gluten: document.getElementById("r-sin-gluten").checked,
        ingredientes: ingredientes,
        pasos: document.getElementById("r-pasos").value.split("\n"),
    };

    try {
        let respuesta;
        if (editando) {
            respuesta = await enviarPUT("/api/admin/recetas/" + editando + CLAVE, datos);
        } else {
            respuesta = await enviarPOST("/api/admin/recetas" + CLAVE, datos);
        }
        editando = respuesta.id;
        document.getElementById("titulo-formulario").textContent = "Editar " + respuesta.id;
        avisarReceta(respuesta.mensaje + " (" + respuesta.id + ").", false);
        mostrarReporte();
        mostrarBitacora();
    } catch (error) {
        avisarReceta(error.message, true);
    }
}

// ---------- Bitácora ----------

async function mostrarBitacora() {
    const caja = document.getElementById("bitacora");
    try {
        const filas = await pedirGET("/api/admin/bitacora" + CLAVE);
        if (filas.length === 0) {
            caja.innerHTML = '<p class="pendiente">Sin acciones todavía.</p>';
            return;
        }
        let html = '<table class="tabla"><tr><th>Fecha</th><th>Usuario</th><th>Acción</th></tr>';
        for (const fila of filas) {
            const fecha = new Date(fila.fecha).toLocaleString("es-GT");
            html += "<tr><td>" + escapar(fecha) + "</td><td>" + escapar(fila.usuario || "—") + "</td><td>" + escapar(fila.accion) + "</td></tr>";
        }
        html += "</table>";
        caja.innerHTML = html;
    } catch (error) {
        caja.innerHTML = '<p class="mensaje-error">' + escapar(error.message) + "</p>";
    }
}

// ---------- Inicio ----------

async function cargarListas() {
    // Categorías para el selector
    const categorias = await pedirGET("/api/admin/categorias" + CLAVE);
    let opciones = "";
    for (const categoria of categorias) {
        opciones += '<option value="' + escapar(categoria) + '">' + escapar(categoria) + "</option>";
    }
    document.getElementById("r-categoria").innerHTML = opciones;

    // Catálogo completo para sugerir claves de ingredientes
    const grupos = await pedirGET("/api/ingredientes?todos=true");
    let lista = "";
    for (const grupo in grupos) {
        for (const ingrediente of grupos[grupo]) {
            lista += '<option value="' + escapar(ingrediente.clave) + '">' + escapar(ingrediente.nombre) + "</option>";
        }
    }
    document.getElementById("catalogo").innerHTML = lista;
}

async function iniciar() {
    if (!usuario) {
        return;
    }
    if (usuario.rol !== "admin") {
        document.getElementById("aviso-admin").textContent = "Esta página es solo para administradores.";
        document.getElementById("panel").classList.add("oculto");
        return;
    }
    mostrarReporte();
    mostrarPropuestas();
    mostrarBitacora();
    try {
        await cargarListas();
    } catch (error) {
        avisarReceta("No se pudieron cargar las categorías o ingredientes.", true);
    }
}

let espera = null;
document.getElementById("buscar-receta").addEventListener("input", function () {
    clearTimeout(espera);
    espera = setTimeout(buscarRecetas, 300);
});
document.getElementById("boton-nueva").addEventListener("click", function () {
    abrirFormulario(null);
});
document.getElementById("boton-ingrediente").addEventListener("click", function () {
    filaIngrediente(null);
});
document.getElementById("boton-cancelar").addEventListener("click", function () {
    document.getElementById("caja-formulario").classList.add("oculto");
});
document.getElementById("formulario-receta").addEventListener("submit", guardarReceta);

iniciar();
