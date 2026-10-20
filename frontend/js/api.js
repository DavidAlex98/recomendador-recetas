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

    // En el celular solo se ve la marca y quién eres; el resto va en la barra de abajo y en el menú
    // (los enlaces con la clase "enlace-menu" se esconden en pantallas pequeñas)
    let html = '<a class="marca" href="index.html">RecetApp</a>';
    html += '<a class="enlace-menu" href="checklist.html">¿Qué tengo en casa?</a>';

    if (usuario) {
        html += '<a class="enlace-menu" href="despensa.html">Mi despensa</a>';
        html += '<a class="enlace-menu" href="favoritos.html">Favoritos</a>';
        html += '<a class="enlace-menu" href="plan.html">Plan semanal</a>';
        html += '<a class="enlace-menu" href="proponer.html">Proponer receta</a>';
        if (usuario.rol === "admin") {
            html += '<a class="enlace-menu" href="admin.html">Admin</a>';
        }
        html += '<a class="saludo" href="cuenta.html">Hola, ' + escapar(usuario.nombre) + "</a>";
        html += '<a class="enlace-menu" href="#" id="cerrar-sesion">Cerrar sesión</a>';
    } else {
        html += '<a href="login.html">Iniciar sesión</a>';
        html += '<a class="enlace-menu" href="registro.html">Registrarse</a>';
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
        if (enlace.getAttribute("href") === pagina && !enlace.classList.contains("marca") && !enlace.classList.contains("saludo")) {
            enlace.classList.add("activo");
        }
    }

    armarPestanas(usuario, pagina);
}

// Barra de abajo y menú (se ven solo en el celular)

// Íconos sencillos dibujados con líneas
const ICONOS = {
    inicio: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11.5 12 5l8 6.5V19a1 1 0 0 1-1 1h-4v-5H9v5H5a1 1 0 0 1-1-1z"/></svg>',
    casa: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/></svg>',
    favoritos: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.600-7 10-7 10z"/></svg>',
    menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 7h14M5 12h14M5 17h14"/></svg>',
    camara: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="3"/><circle cx="12" cy="13.5" r="3.5"/><path d="M9 7l1.200-2h3.600L15 7"/></svg>',
};

// Arma la barra de abajo con 4 opciones y el menú con todos los enlaces
function armarPestanas(usuario, pagina) {
    // Qué pestaña se ve activa en cada página
    let activa = "menu";
    if (pagina === "index.html") {
        activa = "inicio";
    } else if (pagina === "checklist.html" || pagina === "receta.html" || pagina === "recetas.html") {
        activa = "casa";
    } else if (pagina === "favoritos.html") {
        activa = "favoritos";
    } else if (pagina === "escanear.html") {
        activa = "escanear";
    }

    const opciones = [
        ["inicio", "Inicio", "index.html"],
        ["casa", "¿Qué tengo?", "checklist.html"],
        ["favoritos", "Favoritos", usuario ? "favoritos.html" : "login.html"],
    ];
    let barraAbajo = "";
    for (const [clave, texto, enlace] of opciones) {
        // El botón de escanear va en el centro, entre las dos primeras y las dos últimas
        if (clave === "favoritos") {
            barraAbajo += '<a class="pestana escanear' + (activa === "escanear" ? " activa" : "") + '" href="escanear.html">';
            barraAbajo += '<span class="boton-escanear">' + ICONOS.camara + "</span><span>Escanear</span></a>";
        }
        barraAbajo += '<a class="pestana' + (clave === activa ? " activa" : "") + '" href="' + enlace + '">';
        barraAbajo += ICONOS[clave] + "<span>" + texto + "</span></a>";
    }
    barraAbajo += '<button type="button" id="abrir-menu" class="pestana' + (activa === "menu" ? " activa" : "") + '">';
    barraAbajo += ICONOS.menu + "<span>Menú</span></button>";

    const pestanas = document.createElement("nav");
    pestanas.className = "pestanas";
    pestanas.setAttribute("aria-label", "Navegación");
    pestanas.innerHTML = barraAbajo;

    // Menú con todos los enlaces (se abre con el botón "Menú")
    const enlaces = [["Inicio", "index.html"], ["¿Qué tengo en casa?", "checklist.html"]];
    if (usuario) {
        enlaces.push(["Mi despensa", "despensa.html"], ["Favoritos", "favoritos.html"]);
        enlaces.push(["Plan semanal", "plan.html"], ["Proponer receta", "proponer.html"]);
        if (usuario.rol === "admin") {
            enlaces.push(["Admin", "admin.html"]);
        }
    } else {
        enlaces.push(["Iniciar sesión", "login.html"], ["Registrarse", "registro.html"]);
    }
    let lista = "";
    for (const [texto, enlace] of enlaces) {
        lista += '<a href="' + enlace + '"' + (enlace === pagina ? ' class="actual"' : "") + ">" + texto + "</a>";
    }
    if (usuario) {
        lista += '<p class="menu-sesion">Sesión iniciada</p>';
        lista += '<a href="cuenta.html" class="menu-nombre">Hola, ' + escapar(usuario.nombre) + "</a>";
        lista += '<a href="#" id="cerrar-sesion-menu" class="menu-salir">Cerrar sesión</a>';
    }
    const menu = document.createElement("div");
    menu.className = "menu-hoja";
    menu.innerHTML = '<div class="menu-cabecera"><span class="marca">RecetApp</span>' +
        '<button type="button" id="cerrar-menu" aria-label="Cerrar menú"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div><nav>' + lista + "</nav>";

    document.body.appendChild(menu);
    document.body.appendChild(pestanas);

    // Con el menú abierto, la pestaña "Menú" se ve marcada; al cerrar vuelve la que estaba
    const botonMenu = document.getElementById("abrir-menu");
    const pestanaAnterior = pestanas.querySelector(".pestana.activa");
    function abrir() {
        menu.classList.add("abierto");
        document.body.classList.add("menu-abierto");
        for (const pestana of pestanas.querySelectorAll(".pestana")) {
            pestana.classList.toggle("activa", pestana === botonMenu);
        }
    }
    function cerrar() {
        menu.classList.remove("abierto");
        document.body.classList.remove("menu-abierto");
        for (const pestana of pestanas.querySelectorAll(".pestana")) {
            pestana.classList.toggle("activa", pestana === pestanaAnterior);
        }
    }
    document.getElementById("abrir-menu").addEventListener("click", abrir);
    document.getElementById("cerrar-menu").addEventListener("click", cerrar);
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrar();
        }
    });
    const salir = document.getElementById("cerrar-sesion-menu");
    if (salir) {
        salir.addEventListener("click", function (evento) {
            evento.preventDefault();
            cerrarSesion();
        });
    }
}

armarBarra();
