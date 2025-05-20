// async function extractMetrics() {
//     const baseDirectory = document.getElementById("base-directory").value;
//     console.log("Base Directory:", baseDirectory);
//     const response = await fetch("/metrics/extract", {
//         method: "POST",
//         headers: { "Content-Type": "application/x-www-form-urlencoded" },
//         body: new URLSearchParams({ "base-directory": baseDirectory }),
//     });
//     console.log("Response:", response);
//     const data = await response.json();
//     console.log("Response Data:", data);
//     if (data.error) {
//         alert("Erro: " + data.error);
//     } else {
//         // Atualize a interface conforme necessário
//         console.log(data);
//         // Exemplo: document.getElementById("output").textContent = JSON.stringify(data, null, 2);
//     }
// }

// Carregar configuração
async function loadConfig() {
    const inputConfig = document.querySelector('[name="input-config"]').value;
    const response = await fetch("/metrics/load-config", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ "input-config": inputConfig }),
    });
    const data = await response.json();
    if (data.error) {
        alert("Erro: " + data.error);
    } else {
        // Atualize a interface conforme necessário
        console.log(data);
    }
}

// Salvar configuração
async function saveConfig() {
    const outputConfig = document.querySelector('[name="output-config"]').value;
    // Exemplo de coleta de métricas e diretórios selecionados
    const directories = Array.from(
        document.querySelectorAll('[name="directory-list"]:checked')
    ).map((el) => el.value);
    const metrics = Array.from(
        document.querySelectorAll('[name="metric-list"]:checked')
    ).map((el) => el.value);

    const body = new URLSearchParams();
    body.append("output-config", outputConfig);
    directories.forEach((dir) => body.append("directory-list", dir));
    metrics.forEach((metric) => body.append("metric-list", metric));
    // grouped-metrics pode precisar de um formato específico, adapte conforme necessário
    // body.append("grouped-metrics", JSON.stringify(groupedMetrics));

    const response = await fetch("/metrics/save-config", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body,
    });
    const data = await response.json();
    if (data.error) {
        alert("Erro: " + data.error);
    } else {
        alert(data.message);
    }
}

// Exemplo de ligação dos scripts aos botões
// document
//     .getElementById("get-metrics-submit")
//     ?.addEventListener("click", extractMetrics);
// document
//     .getElementById("load-config-btn")
//     ?.addEventListener("click", loadConfig);
// document
//     .getElementById("save-config-btn")
//     ?.addEventListener("click", saveConfig);
