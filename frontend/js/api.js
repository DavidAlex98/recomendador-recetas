// Funciones que usan todas las páginas
// Responsable: David

// Hablar con la API

// Si la petición sale mal, lanza un error con el mensaje del servidor
async function pedir(url, opciones) {
    const respuesta = await fetch(url, opciones);
    if (!respuesta.ok) {
        let mensaje = "Error " + respuesta.status;
        try {
            const datos = await respuesta.json();
            if (typeof datos.detail === "string") {
                mensaje = datos.detail;
            }
        } catch (e) {
            // la respuesta no traía mensaje
        }
        const error = new Error(mensaje);
        error.status = respuesta.status;
        throw error;
    }
    return await respuesta.json();
}

// Ejemplo:  const categorias = await pedirGET("/api/categorias");
async function pedirGET(url) {
    return await pedir(url);
}

// Ejemplo:  await enviarPOST("/api/login", { correo: "a@b.com", contrasena: "123" });
async function enviarPOST(url, datos) {
    return await pedir(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos || {}),
    });
}

// Ejemplo:  await enviarPUT("/api/plan/3/estado", { estado: "cocinado" });
async function enviarPUT(url, datos) {
    return await pedir(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos || {}),
    });
}

// Ejemplo:  await enviarDELETE("/api/favoritos/1/gt-0001");
async function enviarDELETE(url) {
    return await pedir(url, { method: "DELETE" });
}

// Protege el texto antes de ponerlo con innerHTML (evita que metan código)
function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
}

// Sesión

// Usuario con sesión {id, nombre, rol}, o null
function usuarioActual() {
    try {
        return JSON.parse(localStorage.getItem("usuario"));
    } catch (e) {
        return null;
    }
}

// Si la página necesita sesión y no hay, manda al login
function requerirSesion() {
    const usuario = usuarioActual();
    if (!usuario) {
        window.location.href = "login.html";
    }
    return usuario;
}

function cerrarSesion() {
    localStorage.removeItem("usuario");
    window.location.href = "index.html";
}

// Barra de arriba

// Arma la barra de arriba según si hay sesión
function armarBarra() {
    const barra = document.querySelector(".barra");
    if (!barra) {
        return;
    }
    const usuario = usuarioActual();

    let html = '<a class="marca" href="index.html">RecetApp</a>';
    html += '<a href="checklist.html">¿Qué tengo en casa?</a>';

    if (usuario) {
        html += '<a href="despensa.html">Mi despensa</a>';
        html += '<a href="favoritos.html">Favoritos</a>';
        html += '<a href="plan.html">Plan semanal</a>';
        html += '<a href="proponer.html">Proponer receta</a>';
        if (usuario.rol === "admin") {
            html += '<a href="admin.html">Admin</a>';
        }
        html += '<span class="saludo">Hola, ' + escapar(usuario.nombre) + "</span>";
        html += '<a href="#" id="cerrar-sesion">Cerrar sesión</a>';
    } else {
        html += '<a href="login.html">Iniciar sesión</a>';
        html += '<a href="registro.html">Registrarse</a>';
    }

    barra.innerHTML = html;

    const botonSalir = document.getElementById("cerrar-sesion");
    if (botonSalir) {
        botonSalir.addEventListener("click", function (evento) {
            evento.preventDefault();
            cerrarSesion();
        });
    }

    const pagina = window.location.pathname.split("/").pop() || "index.html";
    for (const enlace of barra.querySelectorAll("a")) {
        if (enlace.getAttribute("href") === pagina && !enlace.classList.contains("marca")) {
            enlace.classList.add("activo");
        }
    }
}

armarBarra();
