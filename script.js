async function buscarRecetas() {
    try {
        const respuesta = await fetch('http://127.0.0.1:8000/api/buscar?ingredientes=Arroz');
        const datos = await respuesta.json();
        console.log("Datos recibidos de FastAPI:", datos);
    } catch (error) {
        console.error("Error al conectar con la API:", error);
    }
}

buscarRecetas();