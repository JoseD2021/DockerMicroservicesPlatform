// Cargar lista de microservicios al cargar la página
let microList = document.getElementById("micro-list");
const pythonSvg = "https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/files/python-logo-only.svg"
const jsSvg = "https://upload.wikimedia.org/wikipedia/commons/9/99/Unofficial_JavaScript_logo_2.svg"

window.addEventListener("DOMContentLoaded", async () => load());

async function load (){
    try {
        let response = await fetch("http://localhost:8000/servicios");

        let microservices = await response.json();
        microservices.forEach(micro => {
            let microDiv = createMicroDiv(micro);
            microList.appendChild(microDiv);
        });
    } catch (error) {
        console.log("Error al cargar los microservicios. Llenando con placeholders.");

        for (let index = 0; index < 9; index++) {
            let lang = Math.random() > 0.5 ? "py" : "js";
            micro = {
                id: index + 1,
                lang,
                code: lang === "py" ? `print("Hello, World!")` : "console.log('Hello, World!');",
                status: ["running", "stopped", "starting"][Math.floor(Math.random() * 3)],
            }

            let microDiv = createMicroDiv(micro);
            microList.appendChild(microDiv);

        }
    } finally {
        Prism.highlightAll(); // Resaltar el código de los microservicios cargados

        let turnOnButtons = document.querySelectorAll("#turnOnButton");
        let turnOffButtons = document.querySelectorAll("#turnOffButton");
        let deleteButtons = document.querySelectorAll("#deleteButton");

        turnOnButtons.forEach(button => {
            button.addEventListener("click", async (e) => {
            let id = e.target.dataset.id;

            try {
                let response = await fetch(`http://localhost:8000/enablems/${id}`, {
                    method: "POST"
                });

                let datos = await response.json();

                if (datos.status === 'success') {
                    alert("Microservicio habilitado exitosamente.");
                
                    const card = button.closest('.micro-card');
                    if (card) {
                        card.remove();
                    }

                    await load();
                }
            } catch (error) {
                console.log("Error al habilitar el microservicio.");
                alert("Error al habilitar el microservicio.");
                return;
            }
    });
});


        turnOffButtons.forEach(button => {
            button.addEventListener("click", async (e) => {
                let id = e.target.dataset.id;

                try {
                    let response = await fetch(`http://localhost:8000/disablems/${id}`, {
                        method: "POST"
                    });

                    let datos = await response.json();

                    if (datos.status === 'success') {
                        alert("Microservicio deshabilitado exitosamente.");
                
                        const card = button.closest('.micro-card');
                        if (card) {
                            card.remove();
                        }

                        await load();
                    }       
                } catch (error) {
                    console.log("Error al deshabilitar el microservicio.");
                    alert("Error al deshabilitar el microservicio.");
                    return;
                }
    });
        });

        deleteButtons.forEach(button => {
            button.addEventListener("click", async (e) => {
                let id = e.target.dataset.id;
                
                try {

                    let response = await fetch(`http://localhost:8000/deletems/${id}`, {
                        method: "DELETE"
                    });
            
                    let datos = await response.json();

                    if (datos.status === 'success') {
                        alert("Microservicio borrado exitosamente.");
                        const card = button.closest('.micro-card'); 
                        if (card) {
                            card.remove();
                        }
                        // console.log(datos)
                        // location.reload();
                    }
                } catch (error) {
                    console.log("Error al borrar el microservicio.");
                    alert("Error al borrar el microservicio.");
                    return;
                }
                // console.log(`Deleting microservice ${id}`);
            })
        });
    }

}

function createMicroDiv(micro) {
    let microDiv = document.createElement("div");
    microDiv.classList.add("bg-stone-700", "p-4", "rounded-md", "text-white", "micro-card");
    microDiv.innerHTML = structureMicroservice(micro);
    return microDiv;
}

function getLanguageIcon(lang) {
    if (!lang) {
        console.warn("Lenguaje no especificado, asignando aleatoriamente.");
        lang = Math.random() > 0.5 ? "py" : "js";
    }

    switch (lang) {
        case "py":
            return pythonSvg;
        case "js":
            return jsSvg;
        default:
            return "";
    }
}

function getStatus(status) {
    switch (status) {
        case "running":
            return "bg-green-500 shadow-green-500 animate-pulse";
        case "restarting":
            return "bg-yellow-500 shadow-yellow-500 animate-pulse";
        case "paused":
            return "bg-red-500 shadow-red-500";
        default:
            return "bg-gray-500";
    }
}

function structureMicroservice(micro) {
    return `
            <div class="bg-stone-700 p-4 rounded-md text-white relative">
                <div class="absolute top-2 right-2">
                    <div class="relative w-5 h-5 ${getStatus(micro.estado)} rounded-full">
                        <div class="absolute w-[50%] h-[50%] inset-0 ${getStatus(micro.estado)} blur-xl -z-10"></div>
                    </div>
                </div>
                <div class="flex flex-row gap-2 items-center">
                    <img src="${getLanguageIcon(micro.ms.language)}" alt="Language Icon" class="h-8 pointer-events-none select-none">
                    <h2 class="font-bold text-lg">${micro.ms.name ?? `Microcontrolador ${micro.id}`}</h2>                    
                </div>
                <div class="bg-stone-600 p-2 rounded-xl mt-2">
                    <p class="text-sm text-gray-400">${micro.ms.description ?? "Sin descripción..."}</p>
                </div>
                <pre class="language-${micro.ms.language} rounded-xl" ><code class="language-${micro.ms.language}">${micro.ms.code}</code></pre>
                <a href="/${micro.ms.name}" class="text-blue-400 hover:text-blue-300 underline" target="_blank">Ir a endpoint</a>
                <div class="flex flex-row gap-2 mt-4 justify-end">
                    <button id="turnOnButton" data-id="${micro.id}" class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-md hover:cursor-pointer">Habilitar</button>
                    <button id="turnOffButton" data-id="${micro.id}" class="bg-red-400 hover:bg-red-400 text-white px-3 py-1 rounded-md hover:cursor-pointer">Deshabilitar</button>
                    <button id="deleteButton" class="deleteButton" data-id="${micro.id}" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md hover:cursor-pointer">Eliminar</button>
                </div>
            </div>
        `;
}
