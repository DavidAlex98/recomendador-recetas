// Escanear ingredientes con una foto
// Responsable: Brandon
//
// 1. Abre la cámara (o deja elegir una foto de la galería)
// 2. Manda la foto a POST /api/reconocer
// 3. Muestra los ingredientes encontrados para que el usuario los revise
// 4. Con "Ver qué puedo cocinar" lleva los marcados a ¿Qué tengo en casa?
//
// OJO: el endpoint /api/reconocer todavía no existe en el backend. Se espera que responda así:
//   { "ingredientes": [ { "clave": "tomate", "nombre": "Tomate", "confianza": 0.96 } ],
//     "no_reconocidos": 1 }
// Mientras no exista, la página muestra el aviso de "servidor apagado".
//
// Para revisar el diseño sin el backend: escanear.html?demo=resultado
// (también sirven: analizando, nada, servidor y permiso). Esta parte se puede borrar.

const vistas = ["camara", "analizando", "resultado", "error"];
let flujo = null;       // la cámara abierta
let fotoActual = null;  // la última foto (para poder reintentar)

// Muestra una sola vista. En la cámara se esconde la barra, como en el diseño
function mostrarVista(nombre) {
    for (const vista of vistas) {
        document.getElementById("vista-" + vista).classList.toggle("oculto", vista !== nombre);
    }
    document.body.classList.toggle("en-camara", nombre === "camara");
    if (nombre !== "camara") {
        apagarCamara();
    }
}

async function abrirCamara() {
    mostrarVista("camara");
    try {
        flujo = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
        document.getElementById("video").srcObject = flujo;
    } catch (error) {
        mostrarError("permiso");
    }
}

function apagarCamara() {
    if (flujo) {
        for (const pista of flujo.getTracks()) {
            pista.stop();
        }
        flujo = null;
    }
}

// Los cuatro casos en que algo sale mal
function mostrarError(tipo) {
    const casos = {
        permiso: ["Sin permiso de cámara", "Necesitamos tu cámara para escanear. Actívala en los ajustes del navegador.", "Elegir de la galería"],
        nada: ["No se detectó nada", "No encontramos ingredientes en la foto. Prueba con más luz o más cerca.", "Tomar otra foto"],
        servidor: ["Servidor apagado", "No se pudo analizar la foto. Revisa que el servidor esté encendido.", "Reintentar"],
    };
    const caso = casos[tipo];
    document.getElementById("error-titulo").textContent = caso[0];
    document.getElementById("error-mensaje").textContent = caso[1];
    const boton = document.getElementById("error-boton");
    boton.textContent = caso[2];
    boton.onclick = function () {
        if (tipo === "permiso") {
            document.getElementById("galeria").click();
        } else if (tipo === "servidor" && fotoActual) {
            enviarFoto(fotoActual);
        } else {
            abrirCamara();
        }
    };
    mostrarVista("error");
}

// Manda la foto al backend y muestra lo que encontró
async function enviarFoto(foto, demo) {
    fotoActual = foto;
    document.getElementById("vista-foto").src = URL.createObjectURL(foto);
    mostrarVista("analizando");

    try {
        let datos;
        if (demo) {
            datos = demo;
        } else {
            const formulario = new FormData();
            formulario.append("foto", foto);
            const respuesta = await fetch("/api/reconocer", { method: "POST", body: formulario });
            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }
            datos = await respuesta.json();
        }
        if (!datos.ingredientes || datos.ingredientes.length === 0) {
            mostrarError("nada");
            return;
        }
        mostrarResultado(datos);
    } catch (error) {
        mostrarError("servidor");
    }
}

function mostrarResultado(datos) {
    document.getElementById("miniatura").src = document.getElementById("vista-foto").src;
    const total = datos.ingredientes.length;
    document.getElementById("cuantos").textContent = total + (total === 1 ? " ingrediente detectado" : " ingredientes detectados");

    let html = "";
    for (const ingrediente of datos.ingredientes) {
        const porcentaje = Math.round(ingrediente.confianza * 100);
        html += '<label class="item-compra"><input type="checkbox" value="' + escapar(ingrediente.clave) + '" checked> ';
        html += "<span>" + escapar(ingrediente.nombre) + "</span>";
        html += '<span class="barra-confianza"><i style="width:' + porcentaje + '%"></i></span>';
        html += '<span class="porcentaje">' + porcentaje + "%</span></label>";
    }
    document.getElementById("detectados").innerHTML = html;

    const aviso = document.getElementById("no-reconocidos");
    if (datos.no_reconocidos > 0) {
        const n = datos.no_reconocidos;
        aviso.innerHTML = "<strong>No reconocimos " + n + (n === 1 ? " objeto" : " objetos") + "</strong>" +
            '<a class="etiqueta" href="checklist.html">+ Elegir manualmente</a>';
        aviso.classList.remove("oculto");
    } else {
        aviso.classList.add("oculto");
    }
    mostrarVista("resultado");
}

// Pasa los ingredientes marcados a ¿Qué tengo en casa?, que ya sabe buscar las recetas
function verRecetas() {
    const claves = [];
    for (const casilla of document.querySelectorAll("#detectados input:checked")) {
        claves.push(casilla.value);
    }
    sessionStorage.setItem("marcados", JSON.stringify(claves));
    window.location.href = "checklist.html";
}

// Una foto de prueba (un cuadro oscuro) para revisar el diseño
function fotoDePrueba() {
    const lienzo = document.createElement("canvas");
    lienzo.width = 300;
    lienzo.height = 300;
    const dibujo = lienzo.getContext("2d");
    dibujo.fillStyle = "#3a2f28";
    dibujo.fillRect(0, 0, 300, 300);
    const colores = ["#c93e1f", "#e9d8a6", "#e08a1e", "#7fae4f"];
    for (let i = 0; i < 4; i++) {
        dibujo.fillStyle = colores[i];
        dibujo.beginPath();
        dibujo.arc(70 + i * 55, 100 + (i % 2) * 90, 38, 0, Math.PI * 2);
        dibujo.fill();
    }
    return new Promise(function (listo) {
        lienzo.toBlob(listo);
    });
}

async function revisarDiseno(vista) {
    if (vista === "permiso" || vista === "nada" || vista === "servidor") {
        mostrarError(vista);
        return;
    }
    const foto = await fotoDePrueba();
    document.getElementById("vista-foto").src = URL.createObjectURL(foto);
    if (vista === "analizando") {
        mostrarVista("analizando");
    } else {
        mostrarResultado({
            ingredientes: [
                { clave: "tomate", nombre: "Tomate", confianza: 0.96 },
                { clave: "cebolla", nombre: "Cebolla", confianza: 0.91 },
                { clave: "chile_pimiento", nombre: "Chile pimiento", confianza: 0.84 },
                { clave: "huevo", nombre: "Huevo", confianza: 0.78 },
            ],
            no_reconocidos: 1,
        });
    }
}

document.getElementById("disparar").addEventListener("click", function () {
    const video = document.getElementById("video");
    if (!video.videoWidth) {
        return;
    }
    const lienzo = document.createElement("canvas");
    lienzo.width = video.videoWidth;
    lienzo.height = video.videoHeight;
    lienzo.getContext("2d").drawImage(video, 0, 0);
    lienzo.toBlob(function (foto) {
        enviarFoto(foto);
    }, "image/jpeg", 0.9);
});

document.getElementById("galeria").addEventListener("change", function (evento) {
    if (evento.target.files.length > 0) {
        enviarFoto(evento.target.files[0]);
    }
});
document.getElementById("cancelar").addEventListener("click", abrirCamara);
document.getElementById("otra-foto").addEventListener("click", function (evento) {
    evento.preventDefault();
    abrirCamara();
});
document.getElementById("ver-recetas").addEventListener("click", verRecetas);

// Cuando la página termina de cargar
const demo = new URLSearchParams(window.location.search).get("demo");
if (demo) {
    revisarDiseno(demo);
} else {
    abrirCamara();
}
