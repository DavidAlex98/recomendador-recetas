document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll("input[type='checkbox']");
    const contenedor = document.getElementById("contenedor-recetas");

    async function buscarRecetas() {
        // Obtener los valores de los checkboxes que estén marcados
        const seleccionados = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        if (seleccionados.length === 0) {
            contenedor.innerHTML = "<p>Selecciona al menos un ingrediente.</p>";
            return;
        }

        // Construir los parámetros para enviarlos a FastAPI
        const params = new URLSearchParams();
        seleccionados.forEach(ing => params.append("ingredientes", ing));

        try {
            const respuesta = await fetch(`http://localhost:8000/api/recetas/buscar?${params.toString()}`);
            const recetas = await respuesta.json();

            contenedor.innerHTML = "";

            if (recetas.length === 0) {
                contenedor.innerHTML = "<p>No se encontraron recetas con esos ingredientes.</p>";
                return;
            }

            // Crear una tarjeta por cada receta devuelta por la base de datos
            recetas.forEach(receta => {
                const card = document.createElement("div");
                card.style.border = "1px solid #ddd";
                card.style.padding = "15px";
                card.style.marginBottom = "10px";
                card.style.borderRadius = "5px";
                card.style.backgroundColor = "#fff";

                card.innerHTML = `
                    <h3>${receta.nombre}</h3>
                    <p><strong>País:</strong> ${receta.pais}</p>
                    <p><strong>Ingredientes:</strong> ${receta.ingredientes}</p>
                `;
                contenedor.appendChild(card);
            });

        } catch (error) {
            console.error("Error al conectar con la API:", error);
            contenedor.innerHTML = "<p>Error al obtener las recetas del servidor.</p>";
        }
    }

    // Escuchar cuando el usuario marque o desmarque cualquier checkbox
    checkboxes.forEach(cb => {
        cb.addEventListener("change", buscarRecetas);
    });
});