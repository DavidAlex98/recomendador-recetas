// Escanear ingredientes con una foto
// Responsable: Brandon
//
// 1. Abre la cámara (o deja elegir una foto de la galería)
// 2. Manda la foto a POST /api/reconocer (reconocimiento con AWS)
// 3. Muestra los ingredientes encontrados para que el usuario los revise
// 4. Con "Ver qué puedo cocinar" lleva los marcados a ¿Qué tengo en casa?

const vistas = ["camara", "analizando", "resultado", "error"];
let flujo = null;       // la cámara abierta
let fotoActual = null;  // la última foto (para poder reintentar)
let acumulados = {};    // ingredientes de todas las fotos, por clave: { nombre, confianza, marcado }

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
        const pedirCamara = navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment",
                width: { ideal: 1920 },
                height: { ideal: 1080 },
            },
            audio: false,
        });
        // Si otro programa tiene la cámara ocupada (Camo, OBS, Discord…), a veces nunca responde
        const tiempoLimite = new Promise(function (_, rechazar) {
            setTimeout(function () {
                rechazar(new Error("tiempo_agotado"));
            }, 8000);
        });
        flujo = await Promise.race([pedirCamara, tiempoLimite]);
        document.getElementById("video").srcObject = flujo;
    } catch (error) {
        if (error.message === "tiempo_agotado") {
            mostrarError("ocupada");
            // Si la cámara responde tarde, igual se apaga: ya no la estamos usando
            pedirCamara.then(function (flujoTardio) {
                for (const pista of flujoTardio.getTracks()) {
                    pista.stop();
                }
            }).catch(function () {});
        } else {
            mostrarError("permiso");
        }
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

// Los casos en que algo sale mal
function mostrarError(tipo) {
    const casos = {
        permiso: ["Sin permiso de cámara", "Necesitamos tu cámara para escanear. Actívala en los ajustes del navegador.", "Elegir de la galería"],
        ocupada: ["No se pudo abrir la cámara", "Puede estar siendo usada por otro programa (Camo, OBS, Discord…). Ciérralo e intenta de nuevo, o elige una foto.", "Elegir de la galería"],
        nada: ["No se detectó nada", "No encontramos ingredientes en la foto. Prueba con más luz o más cerca.", "Tomar otra foto"],
        servidor: ["Servidor apagado", "No se pudo analizar la foto. Revisa que el servidor esté encendido.", "Reintentar"],
    };
    const caso = casos[tipo];
    document.getElementById("error-titulo").textContent = caso[0];
    document.getElementById("error-mensaje").textContent = caso[1];
    const boton = document.getElementById("error-boton");
    boton.textContent = caso[2];
    boton.onclick = function () {
        if (tipo === "permiso" || tipo === "ocupada") {
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
async function enviarFoto(foto) {
    fotoActual = foto;
    document.getElementById("vista-foto").src = URL.createObjectURL(foto);
    mostrarVista("analizando");

    try {
        const formulario = new FormData();
        formulario.append("foto", foto);
        const respuesta = await fetch("/api/reconocer", { method: "POST", body: formulario });
        if (!respuesta.ok) {
            throw new Error("Error " + respuesta.status);
        }
        const datos = await respuesta.json();
        const sinNadaNuevo = !datos.ingredientes || datos.ingredientes.length === 0;
        if (sinNadaNuevo && Object.keys(acumulados).length === 0) {
            // Es la primera foto y no se detectó nada: todavía no hay una lista que se pueda perder
            mostrarError("nada");
            return;
        }
        mostrarResultado(datos, sinNadaNuevo);
    } catch (error) {
        mostrarError("servidor");
    }
}

// Guarda en acumulados lo que el usuario dejó marcado o desmarcado antes de la foto nueva
function guardarMarcados() {
    for (const casilla of document.querySelectorAll("#detectados input")) {
        if (acumulados[casilla.value]) {
            acumulados[casilla.value].marcado = casilla.checked;
        }
    }
}

function mostrarResultado(datos, sinNadaNuevo) {
    guardarMarcados();

    // Lo de esta foto se suma a lo que ya se había detectado en fotos anteriores
    for (const ingrediente of datos.ingredientes) {
        const marcado = acumulados[ingrediente.clave] ? acumulados[ingrediente.clave].marcado : true;
        acumulados[ingrediente.clave] = {
            nombre: ingrediente.nombre,
            confianza: ingrediente.confianza,
            marcado: marcado,
        };
    }

    document.getElementById("miniatura").src = document.getElementById("vista-foto").src;
    const claves = Object.keys(acumulados);
    const total = claves.length;
    let texto = total + " ingredientes detectados";
    if (total === 1) {
        texto = total + " ingrediente detectado";
    }
    document.getElementById("cuantos").textContent = texto;

    let html = "";
    for (const clave of claves) {
        const ingrediente = acumulados[clave];
        const porcentaje = Math.round(ingrediente.confianza * 100);
        const marcado = ingrediente.marcado ? " checked" : "";
        html += '<label class="item-compra"><input type="checkbox" value="' + escapar(clave) + '"' + marcado + "> ";
        html += "<span>" + escapar(ingrediente.nombre) + "</span>";
        html += '<span class="barra-confianza"><i style="width:' + porcentaje + '%"></i></span>';
        html += '<span class="porcentaje">' + porcentaje + "%</span></label>";
    }
    document.getElementById("detectados").innerHTML = html;

    const aviso = document.getElementById("no-reconocidos");
    if (sinNadaNuevo) {
        aviso.innerHTML = "<strong>En esta foto no encontramos nada nuevo</strong>" +
            "Prueba con más luz o más cerca. Lo que ya tenías detectado sigue en la lista de abajo.";
        aviso.classList.remove("oculto");
    } else if (datos.no_reconocidos > 0) {
        const n = datos.no_reconocidos;
        let palabra = " objetos";
        if (n === 1) {
            palabra = " objeto";
        }
        aviso.innerHTML = "<strong>No reconocimos " + n + palabra + "</strong>" +
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

abrirCamara();
