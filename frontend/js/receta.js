// Página de una receta
// Responsable: David

const DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"];
const NOMBRES_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

async function mostrarReceta() {
    const contenedor = document.getElementById("receta");

    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) {
        contenedor.innerHTML = '<p class="mensaje-error">No se indicó qué receta mostrar.</p>';
        return;
    }

    try {
        const receta = await pedirGET("/api/recetas/" + id);

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

        html += '<div id="acciones-usuario"></div>';

        html += '<section class="tarjeta"><h3>Ingredientes</h3><ul>';
        for (const ingrediente of receta.ingredientes) {
            // Nombre, puntos y cantidad a la derecha
            html += '<li class="ingrediente"><span>' + escapar(ingrediente.nombre);
            if (ingrediente.opcional) {
                html += ' <span class="pendiente">(opcional)</span>';
            }
            html += '</span><span class="puntos"></span>';
            if (ingrediente.cantidad) {
                html += "<b>" + Number(ingrediente.cantidad) + " " + escapar(ingrediente.unidad) + "</b>";
            }
            html += "</li>";
        }
        html += "</ul></section>";

        html += '<section class="tarjeta"><h3>Preparación</h3><ol>';
        for (const paso of receta.pasos) {
            html += "<li>" + escapar(paso.instruccion) + "</li>";
        }
        html += "</ol></section>";

        contenedor.innerHTML = html;
        document.title = receta.nombre + " · RecetApp";
        mostrarAcciones(receta.id);
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se encontró la receta.</p>';
    }
}

// Con sesión: favorito, plan y historial
async function mostrarAcciones(recetaId) {
    const usuario = usuarioActual();
    const caja = document.getElementById("acciones-usuario");
    if (!usuario) {
        caja.innerHTML = '<p class="pendiente"><a href="login.html">Inicia sesión</a> para guardar esta receta o agregarla a tu plan.</p>';
        return;
    }

    // Anotar en el historial
    enviarPOST("/api/historial/" + usuario.id + "/" + recetaId).catch(function () {});

    let esFavorita = false;
    try {
        const favoritos = await pedirGET("/api/favoritos/" + usuario.id);
        for (const favorito of favoritos) {
            if (favorito.id === recetaId) {
                esFavorita = true;
            }
        }
    } catch (error) {
    }

    let opciones = "";
    for (let i = 0; i < DIAS.length; i++) {
        opciones += '<option value="' + DIAS[i] + '">' + NOMBRES_DIAS[i] + "</option>";
    }

    let html = '<div class="tarjeta acciones">';
    if (esFavorita) {
        html += '<button id="boton-favorito" class="boton boton-gris">' + ICONOS.favoritos.replace("<svg", '<svg class="lleno"') + " En favoritos (quitar)</button>";
    } else {
        html += '<button id="boton-favorito" class="boton">' + ICONOS.favoritos + " Guardar en favoritos</button>";
    }
    html += '<select id="dia" class="selector">' + opciones + "</select>";
    html += '<button id="boton-plan" class="boton">Agregar al plan</button>';
    html += '<p id="mensaje-accion"></p>';
    html += "</div>";
    caja.innerHTML = html;

    document.getElementById("boton-favorito").addEventListener("click", async function () {
        try {
            if (esFavorita) {
                await enviarDELETE("/api/favoritos/" + usuario.id + "/" + recetaId);
            } else {
                await enviarPOST("/api/favoritos/" + usuario.id + "/" + recetaId);
            }
            mostrarAcciones(recetaId);
        } catch (error) {
            avisar(escapar(error.message), true);
        }
    });

    document.getElementById("boton-plan").addEventListener("click", async function () {
        const dia = document.getElementById("dia").value;
        try {
            await enviarPOST("/api/plan/" + usuario.id, { receta_id: recetaId, dia: dia });
            avisar('Agregada al plan. <a href="plan.html">Ver mi plan</a>', false);
        } catch (error) {
            avisar(escapar(error.message), true);
        }
    });
}

function avisar(html, esError) {
    const mensaje = document.getElementById("mensaje-accion");
    mensaje.className = esError ? "mensaje-error" : "mensaje-ok";
    mensaje.innerHTML = html;
}

mostrarReceta();
