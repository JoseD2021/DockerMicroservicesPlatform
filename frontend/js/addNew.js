let newServiceButton = document.getElementById('new-service-button');
let codeArea = document.getElementById('code');

let alreadyAdding = false;

codeArea.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        let start = codeArea.selectionStart;
        let end = codeArea.selectionEnd;

        // insertar tab
        codeArea.value = codeArea.value.substring(0, start) + "\t" + codeArea.value.substring(end);

        // mover cursor después del tab
        codeArea.selectionStart = codeArea.selectionEnd = start + 1;
    }
})

newServiceButton.addEventListener("click", async (e) => {
    if (alreadyAdding) return;
    alreadyAdding = true;
    let spin = document.querySelector("#addingSpin");
    let text = document.querySelector("#addingText");

    spin.classList.toggle("opacity-0");
    text.classList.toggle("opacity-0");

    let lang = document.getElementById('lang').value;
    let code = document.getElementById('code').value;
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;

    try {
        if (lang === "" || code === "" || name === "" || description === "") {
            alert("Por favor, complete todos los campos.");
            return;
        }
        
        let response = await fetch("http://localhost:8000/servicios/nuevo", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ lang, code, name, description })
        });

        if (response.ok) {
            // alert("Microservicio creado exitosamente.");
            await loadMicroservices();
            // console.log(await response.json())
            // location.reload();

            document.getElementById('lang').value = "";
            document.getElementById('code').value = "";
            document.getElementById('name').value = "";
            document.getElementById('description').value = "";
        } else {
            response.json().then(data => {
                console.log("Error al crear el microservicio:", data);
                alert("Error al crear el microservicio");
            }).catch(() => {
                console.log("Error al crear el microservicio.");
                alert("Error al crear el microservicio.");
            });
        }
    } catch (error) {
        console.log("Error al crear el microservicio.");
        console.error(error);
        alert("Error al crear el microservicio.");
        return;
    } finally {
        alreadyAdding = false;
        spin.classList.toggle("opacity-0");
        text.classList.toggle("opacity-0");
    }
});