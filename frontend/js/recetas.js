// Buscar recetas
// Responsable: Brandon
//
// 1. Muestra las categorías de recetas como pestañas
// 2. Pide a /api/recetas?buscar=...&categoria=... las recetas (máximo 50)
// 3. Busca otra vez cuando el usuario escribe o cambia de categoría

// Las categorías de recetas.json (las recetas no tienen un endpoint para listarlas)
const CATEGORIAS = [
    "Recados y guisos", "Fiestas y temporada", "Ensaladas y guarniciones", "Rápidas y fáciles",
    "Antojitos y comida de calle", "Sopas y caldos", "Mariscos y costa", "Tamales y masas",
    "Desayunos", "Postres y dulces", "Carnes y asados", "Salsas y recados", "Bebidas y atoles",
    "Panaderia", "Frijoles y guarniciones",
];

let categoriaActual = "";
let esperando = null;

// Dibuja las pestañas: "Todas" y una por categoría
function mostrarFiltros() {
    let html = '<button type="button" class="filtro activo" data-categoria="">Todas</button>';
    for (const categoria of CATEGORIAS) {
        html += '<button type="button" class="filtro" data-categoria="' + escapar(categoria) + '">' + escapar(categoria) + "</button>";
    }
    const caja = document.getElementById("filtros");
    caja.innerHTML = html;
    for (const boton of caja.querySelectorAll(".filtro")) {
        boton.addEventListener("click", function () {
            categoriaActual = boton.dataset.categoria;
            for (const otro of caja.querySelectorAll(".filtro")) {
                otro.classList.toggle("activo", otro === boton);
            }
            buscarRecetas();
        });
    }
}

async function buscarRecetas() {
    const resultados = document.getElementById("resultados");
    const texto = document.getElementById("buscador").value.trim();
    const url = "/api/recetas?buscar=" + encodeURIComponent(texto) + "&categoria=" + encodeURIComponent(categoriaActual);
    try {
        const recetas = await pedirGET(url);
        if (recetas.length === 0) {
            resultados.innerHTML = '<p class="pendiente">No hay recetas con ese nombre.</p>';
            return;
        }
        let html = "";
        for (const receta of recetas) {
            html += '<a class="tarjeta receta" href="receta.html?id=' + escapar(receta.id) + '">';
            html += "<strong>" + escapar(receta.nombre) + "</strong><br>";
            html += '<span class="etiqueta">' + escapar(receta.categoria) + "</span>";
            html += '<span class="etiqueta">' + receta.tiempo_min + " min</span>";
            html += '<span class="etiqueta">' + escapar(receta.dificultad) + "</span>";
            html += "</a>";
        }
        resultados.innerHTML = html;
    } catch (error) {
        resultados.innerHTML = '<p class="mensaje-error">No se pudieron cargar las recetas. Revisa que el servidor esté encendido.</p>';
    }
}

mostrarFiltros();
buscarRecetas();

// Espera un momento después de escribir para no buscar con cada letra
document.getElementById("buscador").addEventListener("input", function () {
    clearTimeout(esperando);
    esperando = setTimeout(buscarRecetas, 300);
});
