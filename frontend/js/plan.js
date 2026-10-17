// Plan semanal
// Responsable: Cristian
//
// 1. Pide el plan a /api/plan/{usuario_id}
// 2. Lo muestra por día, de lunes a domingo
// 3. Cada receta se puede marcar como cocinada u omitida, o quitar

const usuario = requerirSesion();

const DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"];
const NOMBRES_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

async function mostrarPlan() {
    const contenedor = document.getElementById("plan");
    try {
        const plan = await pedirGET("/api/plan/" + usuario.id);

        let html = "";
        for (let i = 0; i < DIAS.length; i++) {
            html += '<section class="tarjeta dia">';
            html += "<h3>" + NOMBRES_DIAS[i] + "</h3>";

            let hay = false;
            for (const item of plan) {
                if (item.dia !== DIAS[i]) {
                    continue;
                }
                hay = true;
                html += '<div class="fila-plan estado-' + escapar(item.estado) + '">';
                html += '<a href="receta.html?id=' + escapar(item.receta_id) + '">' + escapar(item.nombre) + "</a> ";
                html += '<span class="etiqueta">' + escapar(item.estado) + "</span>";
                html += '<span class="acciones">';
                if (item.estado === "planificado") {
                    html += '<button class="boton boton-chico" onclick="cambiarEstado(' + item.id + ', \'cocinado\')">Cocinado</button>';
                    html += '<button class="boton boton-chico boton-gris" onclick="cambiarEstado(' + item.id + ', \'omitido\')">Omitir</button>';
                }
                html += '<button class="boton boton-chico boton-gris" onclick="quitar(' + item.id + ')">Quitar</button>';
                html += "</span></div>";
            }
            if (!hay) {
                html += '<p class="pendiente">Nada planeado.</p>';
            }
            html += "</section>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se pudo cargar tu plan.</p>';
    }
}

async function cambiarEstado(id, estado) {
    try {
        await enviarPUT("/api/plan/" + id + "/estado", { estado: estado });
        mostrarPlan();
    } catch (error) {
        document.getElementById("mensaje").textContent = error.message;
    }
}

async function quitar(id) {
    try {
        await enviarDELETE("/api/plan/" + id);
        mostrarPlan();
    } catch (error) {
        document.getElementById("mensaje").textContent = error.message;
    }
}

// Cuando la página termina de cargar
if (usuario) {
    mostrarPlan();
}
