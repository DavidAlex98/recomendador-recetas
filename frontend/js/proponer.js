// Proponer una receta
// Responsable: Brandon

const usuario = requerirSesion();

async function mostrarPropuestas() {
    const contenedor = document.getElementById("propuestas");
    try {
        const propuestas = await pedirGET("/api/propuestas/" + usuario.id);
        if (propuestas.length === 0) {
            contenedor.innerHTML = '<p class="pendiente">Todavía no has propuesto recetas.</p>';
            return;
        }
        let html = "";
        for (const propuesta of propuestas) {
            html += '<div class="tarjeta">';
            html += "<strong>" + escapar(propuesta.nombre) + "</strong> ";
            html += '<span class="etiqueta estado-' + escapar(propuesta.estado) + '">' + escapar(propuesta.estado) + "</span>";
            if (propuesta.descripcion) {
                html += "<p>" + escapar(propuesta.descripcion) + "</p>";
            }
            if (propuesta.motivo_rechazo) {
                html += '<p class="mensaje-error">Motivo: ' + escapar(propuesta.motivo_rechazo) + "</p>";
            }
            html += "</div>";
        }
        contenedor.innerHTML = html;
    } catch (error) {
        contenedor.innerHTML = '<p class="mensaje-error">No se pudieron cargar tus propuestas.</p>';
    }
}

document.getElementById("formulario").addEventListener("submit", async function (evento) {
    evento.preventDefault();
    const mensaje = document.getElementById("mensaje");
    try {
        await enviarPOST("/api/propuestas/" + usuario.id, {
            nombre: document.getElementById("nombre").value,
            descripcion: document.getElementById("descripcion").value,
        });
        mensaje.className = "mensaje-ok";
        mensaje.textContent = "¡Gracias! Tu propuesta quedó pendiente de revisión.";
        evento.target.reset();
        mostrarPropuestas();
    } catch (error) {
        mensaje.className = "mensaje-error";
        mensaje.textContent = error.message;
    }
});

if (usuario) {
    mostrarPropuestas();
}
