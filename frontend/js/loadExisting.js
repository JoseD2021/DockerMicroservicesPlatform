// Cargar lista de microservicios al cargar la página
let microList = document.getElementById("micro-list");
const pythonSvg = "/svg/python.svg"
const jsSvg = "/svg/javascript.svg"

window.addEventListener("DOMContentLoaded", async () => loadMicroservices());

let apiWorking = false;

async function loadMicroservices() {
    try {
        let response = await fetch("http://localhost:8000/servicios");

        let microservices = await response.json();
        microList.replaceChildren(); // Limpiar lista antes de cargar

        microservices.forEach(micro => {
            // console.log("loading", micro);
            let microDiv = createMicroDiv(micro);
            microList.appendChild(microDiv);
        });
    } catch (error) {
        alert("No se pudieron cargar los microservicios.");
        console.log("Error al cargar los microservicios. Llenando con placeholders.");
        console.error(error)

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
                if (apiWorking) return;

                apiWorking = true;
                let spin = button.querySelector("#turnOnSpin");
                let text = button.querySelector("#turnOnText");

                spin.classList.toggle('opacity-0');
                text.classList.toggle('opacity-0')

                let id = button.dataset.id;

                try {
                    let response = await fetch(`http://localhost:8000/enablems/${id}`, {
                        method: "POST"
                    });

                    let datos = await response.json();

                    if (datos.status === 'success') {
                        await loadMicroservices();
                    } else {
                        console.log("Error al habilitar el microservicio:", datos);
                        alert("Error al habilitar el microservicio");
                    }
                } catch (error) {
                    console.log("Error al habilitar el microservicio.");
                    alert("Error al habilitar el microservicio.");
                    return;
                } finally {
                    apiWorking = false;
                    spin.classList.toggle('opacity-0');
                    text.classList.toggle('opacity-0')
                }
            });
        });


        turnOffButtons.forEach(button => {
            button.addEventListener("click", async (e) => {
                if (apiWorking) return;
                apiWorking = true;

                let id = button.dataset.id;
                let spin = button.querySelector("#turnOffSpin");
                let text = button.querySelector("#turnOffText");

                spin.classList.toggle('opacity-0');
                text.classList.toggle('opacity-0');

                try {
                    let response = await fetch(`http://localhost:8000/disablems/${id}`, {
                        method: "POST"
                    });

                    let datos = await response.json();

                    if (datos.status === 'success') {
                        await loadMicroservices();
                    } else {
                        console.log("Error al deshabilitar el microservicio:", datos);
                        alert("Error al deshabilitar el microservicio");
                    }
                } catch (error) {
                    console.log("Error al deshabilitar el microservicio.");
                    alert("Error al deshabilitar el microservicio.");
                    return;
                } finally {
                    apiWorking = false;
                    spin.classList.toggle('opacity-0');
                    text.classList.toggle('opacity-0')
                }
            });
        });

        deleteButtons.forEach(button => {
            button.addEventListener("click", async (e) => {
                if (apiWorking) return;
                apiWorking = true;

                let id = button.dataset.id;
                let spin = button.querySelector("#deleteSpin");
                let text = button.querySelector("#deleteText");

                spin.classList.toggle('opacity-0');
                text.classList.toggle('opacity-0');

                try {

                    let response = await fetch(`http://localhost:8000/deletems/${id}`, {
                        method: "DELETE"
                    });

                    let datos = await response.json();

                    if (datos.status === 'success') {
                        // alert("Microservicio borrado exitosamente.");
                        const card = button.closest('.micro-card');
                        if (card) {
                            card.remove();
                        }
                        // console.log(datos)
                        // location.reload();
                    } else {
                        console.log("Error al borrar el microservicio:", datos);
                        alert("Error al borrar el microservicio");
                    }
                } catch (error) {
                    console.log("Error al borrar el microservicio.");
                    alert("Error al borrar el microservicio.");
                    return;
                } finally {
                    apiWorking = false;
                    spin.classList.toggle('opacity-0');
                    text.classList.toggle('opacity-0');
                }
            })
        });
    }
}

function createMicroDiv(micro) {
    let microDiv = document.createElement("div");
    microDiv.classList.add("bg-stone-700", "p-4", "rounded-md", "text-white", "micro-card", "shadow-xl");
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
    isRunning = (micro.estado === 'running');
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
                    <button id="turnOnButton" data-id="${micro.id}" ${isRunning ? 'disabled' : ''} class="relative bg-green-500 text-white px-3 py-1 rounded-md ${isRunning ? 'hover:cursor-not-allowed' : 'hover:bg-green-600 hover:cursor-pointer'}">
                        <span id="turnOnSpin" class="material-symbols-outlined absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-spin opacity-0">
                            progress_activity
                        </span>
                        <p id='turnOnText' class="pointer-events-none select-none">
                            Habilitar
                        </p>
                    </button>
                    <button id="turnOffButton" data-id="${micro.id}" ${!isRunning ? 'disabled' : ''} class="relative bg-red-400 text-white px-3 py-1 rounded-md ${!isRunning ? 'hover:cursor-not-allowed' : 'hover:bg-red-500 hover:cursor-pointer'}">
                        <span id="turnOffSpin" class="material-symbols-outlined absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-spin opacity-0">
                            progress_activity
                        </span>
                        <p id='turnOffText' class="pointer-events-none select-none">
                            Deshabilitar
                        </p>
                    </button>
                    <button id="deleteButton" data-id="${micro.id}" class="relative bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md hover:cursor-pointer">
                        <span id="deleteSpin" class="material-symbols-outlined absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-spin opacity-0">
                            progress_activity
                        </span>
                        <p id='deleteText' class="pointer-events-none select-none">
                            Eliminar
                        </p>
                    </button>
                </div>
            </div>
        `;
}
