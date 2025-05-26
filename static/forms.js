const form = document.getElementById("form");
const debugOutput = document.getElementById("debug-output");

if (debugOutput) {
    function setOutput() {
        debugOutput.textContent = "";
        for (const [key, value] of new FormData(form)) {
            debugOutput.textContent += `${key}: ${value}\n`;
        }
    }
    document.addEventListener("DOMContentLoaded", setOutput);
    (() => {
        const checkboxes = form.querySelectorAll(
            'input[type="checkbox"][name="directory-list"], input[type="checkbox"][name="metric-list"]'
        );
        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", function () {
                setOutput();
            });
        });
        const selections = form.querySelectorAll("select");
        selections.forEach((select) => {
            select.addEventListener("change", function () {
                setOutput();
            });
        });
    })();
}

form.addEventListener("submit", function (event) {
    event.preventDefault();
    console.log(event.submitter.value);
    if (event.submitter.value === "get-metrics") {
        form.method = "post";
        form.action = "/metrics/get-metrics";
        form.submit();
    }
});

// Carregar configuração
async function loadConfig() {
    const inputConfig = document.getElementById("input-config").value;
    if (!inputConfig) {
        return;
    }
    const response = await fetch("/metrics/load-config", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ "input-config": inputConfig }),
    });
    const data = await response.json();
    if (data.error) {
        alert("Erro: " + data.error);
    } else {
        const configData = data.config_data;

        configData.directories.forEach((dir) => {
            const dirCheckbox = document.getElementById(dir);
            dirCheckbox.checked = true;
        });

        Object.entries(configData.metrics).forEach(
            ([metricGroup, metricList]) => {
                const metricGroupBtn = document.getElementById(
                    `${metricGroup}-btn`
                );
                if (metricGroupBtn) {
                    metricGroupBtn.classList.remove("collapsed");
                    metricGroupBtn.ariaExpanded = "true";
                    document
                        .getElementById(`${metricGroup}`)
                        .classList.add("show");
                }

                metricList.forEach((metric) => {
                    const metricCheckbox = document.getElementById(metric);
                    if (metricCheckbox) {
                        metricCheckbox.checked = true;
                    }
                });
            }
        );
        if (debugOutput) {
            setOutput();
        }
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

// Gerar gráficos
async function generateGraphs() {
    const directories = Array.from(
        document.querySelectorAll('[name="directory-list"]:checked')
    ).map((el) => el.value);
    const metrics = Array.from(
        document.querySelectorAll('[name="metric-list"]:checked')
    ).map((el) => el.value);
    const graphType = document.getElementById("graph-type").value;
    const graphComposition = document.getElementById("graph-composition").value;
    const overwrite = document.getElementById("overwrite").value;
    const body = new URLSearchParams();
    body.append("graph-type", graphType);
    body.append("graph-composition", graphComposition);
    body.append("overwrite", overwrite);
    directories.forEach((dir) => body.append("directory-list", dir));
    metrics.forEach((metric) => body.append("metric-list", metric));

    const response = await fetch("/graphs/generate-graphs", {
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
document
    .getElementById("load-config-submit")
    ?.addEventListener("click", loadConfig);
document
    .getElementById("save-config-submit")
    ?.addEventListener("click", saveConfig);
document
    .getElementById("generate-graphs-submit")
    ?.addEventListener("click", generateGraphs);
