let newServiceButton = document.getElementById('new-service-button');
newServiceButton.addEventListener("click", async (e) => {
    let lang = document.getElementById('lang').value;
    let code = document.getElementById('code').value;
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;

    if (lang === "" || code === "" || name === "" || description === "") {
        alert("Por favor, complete todos los campos.");
        return;
    }

    console.log({lang, code, name, description});

    try {

        // TODO: Modificar esto, probablemente
        let response = await fetch("/api/microservices", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ lang, code, name, description })
        });

        if (response.ok) {
            alert("Microservicio creado exitosamente.");
            location.reload();
        }
    } catch (error) {
        console.log("Error al crear el microservicio.");
        alert("Error al crear el microservicio.");
        return;
    }
});