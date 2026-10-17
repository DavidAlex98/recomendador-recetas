// Mis recetas favoritas
// Responsable: Cristian
//
// 1. Pide los favoritos a /api/favoritos/{usuario_id}
// 2. Cada uno se puede quitar o mandar al plan de la semana

const usuario = requerirSesion();

const DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"];
const NOMBRES_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

async function mostrarFavoritos() {
    const contenedor = document.getElementById("favoritos");
    try {
        const recetas = await pedirGET("/api/favoritos/" + usuario.id);
        if (recetas.length === 0) {
            contenedor.innerHTML = '<p class="pendiente">Todavía no tienes favoritos. ' +
                'Busca recetas en <a href="checklist.html">¿Qué tengo en casa?</a></p>';
            return;
        }

        let opciones = "";
        for (let i = 0; i < DIAS.length; i++) {
            opciones += '<option value="' + DIAS[i] + '">' + NOMBRES_DIAS[i] + "</option>";
        }

        let html = "";
        for (const receta of recetas) {
            const id = escapar(receta.id);
            html += '<div class="tarjeta">';
            html += '<a class="titulo-receta" href="receta.html?id=' + id + '"><strong>' + escapar(receta.nombre) + "</strong></a><br>";
            html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
            html += '<span class="etiqueta">' + receta.tiempo_min + " min</span>";
            html += '<span class="etiqueta">' + escapar(receta.dificultad) + "</span>";
            html += '<div class="acciones">';
            html += '<select id="dia-' + id + '" class="selector">' + opciones + "</select>";
            html += '<button class="boton boton-chico" onclick="alPlan(\'' + id + '\')">Agregar al plan</button>';
            html += '<button class="boton boton-chico boton-gris" onclick="quitar(\'' + id + '\')">Quitar de favoritos</button>';
            html += "</div></div>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se pudieron cargar tus favoritos.</p>';
    }
}

async function quitar(recetaId) {
    try {
        await enviarDELETE("/api/favoritos/" + usuario.id + "/" + recetaId);
        mostrarFavoritos();
    } catch (error) {
        document.getElementById("mensaje").textContent = "No se pudo quitar: " + error.message;
    }
}

async function alPlan(recetaId) {
    const dia = document.getElementById("dia-" + recetaId).value;
    const mensaje = document.getElementById("mensaje");
    try {
        await enviarPOST("/api/plan/" + usuario.id, { receta_id: recetaId, dia: dia });
        mensaje.className = "mensaje-ok";
        mensaje.innerHTML = 'Agregada al plan. <a href="plan.html">Ver mi plan</a>';
    } catch (error) {
        mensaje.className = "mensaje-error";
        mensaje.textContent = "No se pudo agregar: " + error.message;
    }
}

// Cuando la página termina de cargar
if (usuario) {
    mostrarFavoritos();
}
