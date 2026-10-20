// Lista de compras
// Responsable: Brandon
//
// Todavía no hay un endpoint para esto, así que la lista se arma en el navegador con lo que ya existe:
//   - las recetas planificadas de tu plan   GET /api/plan/{usuario_id}
//   - los ingredientes de cada receta       GET /api/recetas/{id}
//   - lo que ya tienes en la despensa       GET /api/despensa/{usuario_id}
// El estado (generada, comprada o cerrada) y lo que marcaste se guardan en este navegador.

const usuario = requerirSesion();
const ESTADOS = [["generada", "Generada"], ["comprada", "Comprada"], ["cerrada", "Cerrada"]];

let guardado = { estado: "generada", marcados: [] };
let pestana = "generada";
let faltantes = [];   // [{ receta, items: [{ clave, nombre, texto }] }]

function leerGuardado() {
    try {
        const datos = JSON.parse(localStorage.getItem("lista-" + usuario.id));
        if (datos && datos.estado) {
            guardado = datos;
        }
    } catch (e) {
        // no había nada guardado
    }
    pestana = guardado.estado;
}

function guardar() {
    localStorage.setItem("lista-" + usuario.id, JSON.stringify(guardado));
}

// Busca lo que falta para cocinar las recetas planificadas
async function armarLista() {
    const plan = await pedirGET("/api/plan/" + usuario.id);
    const despensa = await pedirGET("/api/despensa/" + usuario.id);
    const tengo = despensa.map(function (ingrediente) {
        return ingrediente.clave;
    });

    faltantes = [];
    for (const item of plan) {
        if (item.estado !== "planificado") {
            continue;
        }
        const receta = await pedirGET("/api/recetas/" + item.receta_id);
        const items = [];
        for (const ingrediente of receta.ingredientes) {
            if (ingrediente.opcional || tengo.includes(ingrediente.clave)) {
                continue;
            }
            let texto = "";
            if (ingrediente.cantidad) {
                texto = Number(ingrediente.cantidad) + " " + ingrediente.unidad;
            }
            items.push({ clave: ingrediente.clave, nombre: ingrediente.nombre, texto: texto });
        }
        if (items.length > 0) {
            faltantes.push({ receta: receta.nombre, items: items });
        }
    }
}

function dibujarPestanas() {
    let html = "";
    for (const estado of ESTADOS) {
        html += '<button type="button" class="filtro' + (estado[0] === pestana ? " activo" : "") + '" data-estado="' + estado[0] + '">' + estado[1] + "</button>";
    }
    const caja = document.getElementById("estados");
    caja.innerHTML = html;
    for (const boton of caja.querySelectorAll(".filtro")) {
        boton.addEventListener("click", function () {
            pestana = boton.dataset.estado;
            dibujar();
        });
    }
}

function dibujar() {
    dibujarPestanas();
    const caja = document.getElementById("lista");

    // Otra pestaña distinta del estado actual de la lista
    if (pestana !== guardado.estado) {
        caja.innerHTML = '<p class="pendiente">No hay una lista ' + pestana + ".</p>";
        return;
    }
    if (faltantes.length === 0) {
        caja.innerHTML = '<p class="pendiente">No te falta nada. Agrega recetas a tu <a href="plan.html">plan de la semana</a> para armar tu lista.</p>';
        return;
    }

    let html = "";
    for (const grupo of faltantes) {
        html += '<p class="sobretitulo para">Para: ' + escapar(grupo.receta) + "</p>";
        for (const item of grupo.items) {
            const marcado = guardado.marcados.includes(item.clave) ? " checked" : "";
            html += '<label class="item-compra"><input type="checkbox" value="' + escapar(item.clave) + '"' + marcado + "> ";
            html += "<span>" + escapar(item.nombre) + "</span>";
            html += '<span class="cantidad">' + escapar(item.texto) + "</span></label>";
        }
    }
    html += '<div class="botones-lista">';
    if (guardado.estado === "generada") {
        html += '<button type="button" id="boton-comprada" class="boton">Marcar como comprada</button>';
        html += '<button type="button" id="boton-cerrar" class="boton boton-contorno">Cerrar lista</button>';
    } else if (guardado.estado === "comprada") {
        html += '<button type="button" id="boton-cerrar" class="boton">Cerrar lista</button>';
    } else {
        html += '<button type="button" id="boton-nueva" class="boton">Armar una lista nueva</button>';
    }
    html += "</div>";
    caja.innerHTML = html;

    for (const casilla of caja.querySelectorAll(".item-compra input")) {
        casilla.addEventListener("change", function () {
            guardado.marcados = [];
            for (const marcada of caja.querySelectorAll(".item-compra input:checked")) {
                guardado.marcados.push(marcada.value);
            }
            guardar();
        });
    }
    const comprada = document.getElementById("boton-comprada");
    if (comprada) {
        comprada.addEventListener("click", function () {
            guardado.estado = "comprada";
            guardado.marcados = [];
            for (const grupo of faltantes) {
                for (const item of grupo.items) {
                    guardado.marcados.push(item.clave);
                }
            }
            pestana = "comprada";
            guardar();
            dibujar();
        });
    }
    const cerrar = document.getElementById("boton-cerrar");
    if (cerrar) {
        cerrar.addEventListener("click", function () {
            guardado.estado = "cerrada";
            pestana = "cerrada";
            guardar();
            dibujar();
        });
    }
    const nueva = document.getElementById("boton-nueva");
    if (nueva) {
        nueva.addEventListener("click", function () {
            guardado = { estado: "generada", marcados: [] };
            pestana = "generada";
            guardar();
            dibujar();
        });
    }
}

async function iniciar() {
    leerGuardado();
    try {
        await armarLista();
        dibujar();
    } catch (error) {
        document.getElementById("lista").innerHTML = '<p class="mensaje-error">No se pudo armar tu lista. Revisa que el servidor esté encendido.</p>';
    }
}

if (usuario) {
    iniciar();
}
