// Mi cuenta
// Responsable: Brandon
//
// Muestra quién eres (los datos salen de la sesión) y las páginas de tu cuenta.

const usuario = requerirSesion();

if (usuario) {
    document.getElementById("avatar").textContent = usuario.nombre.charAt(0).toUpperCase();
    document.getElementById("nombre").textContent = usuario.nombre;
    document.getElementById("rol").textContent = "Rol: " + usuario.rol;

    const opciones = [
        ["Mis recetas favoritas", "favoritos.html"],
        ["Plan de la semana", "plan.html"],
        ["Mi despensa", "despensa.html"],
        ["Lo último que viste", "historial.html"],
        ["Buscar recetas", "recetas.html"],
        ["Proponer receta", "proponer.html"],
    ];
    if (usuario.rol === "admin") {
        opciones.push(["Panel de administración", "admin.html"]);
    }

    let html = "";
    for (const opcion of opciones) {
        html += '<a href="' + opcion[1] + '"><span>' + escapar(opcion[0]) + '</span><span class="flecha">›</span></a>';
    }
    html += '<a href="#" id="salir" class="salir"><span>Cerrar sesión</span></a>';
    document.getElementById("opciones").innerHTML = html;

    document.getElementById("salir").addEventListener("click", function (evento) {
        evento.preventDefault();
        cerrarSesion();
    });
}
