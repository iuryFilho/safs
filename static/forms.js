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
        const graphSection = form.querySelector("#graph-section");
        if (graphSection) {
            const inputs = graphSection.querySelectorAll(
                'input[type="text"], input[type="number"]'
            );
            inputs.forEach((input) => {
                input.addEventListener("input", function () {
                    setOutput();
                });
            });
        }
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

function createBody(data) {
    const body = new URLSearchParams();
    for (const [key, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
            value.forEach((item) => body.append(key, item));
        } else if (typeof value === "object" && value !== null) {
            body.append(key, JSON.stringify(value));
        } else {
            body.append(key, value);
        }
    }
    return body;
}

function getElementValue(id) {
    return document.getElementById(id).value;
}

function getCheckedValues(name) {
    return Array.from(
        document.querySelectorAll(`[name="${name}"]:checked`)
    ).map((el) => el.value);
}

function assignSubmitFunction(id, func) {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener("click", func);
    } else {
        console.warn(`Elemento com ID ${id} não encontrado.`);
    }
}

// Carregar configuração
async function loadConfig() {
    const inputConfig = getElementValue("input-config");
    if (!inputConfig) {
        return;
    }
    const response = await fetch("/metrics/load-config", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: createBody({
            "input-config": inputConfig,
        }),
    });
    const data = await response.json();
    if (data.error) {
        alert("Erro: " + data.error);
    } else {
        const configData = data.config_data;

        form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
            checkbox.checked = false;
        });

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
    const outputConfig = getElementValue("output-config");
    const directories = getCheckedValues("directory-list");
    const metrics = getCheckedValues("metric-list");

    const body = createBody({
        "output-config": outputConfig,
        "directory-list": directories,
        "metric-list": metrics,
    });

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

function selectAllCheckboxes(listName) {
    const checkboxes = document.querySelectorAll(
        `input[type="checkbox"][name="${listName}"]`
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = true;
    });
}

function deselectAllCheckboxes(listName) {
    const checkboxes = document.querySelectorAll(
        `input[type="checkbox"][name="${listName}"]`
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });
}

// Gerar gráficos
async function generateGraphs() {
    const directories = getCheckedValues("directory-list");
    const metrics = getCheckedValues("metric-list");
    const graphType = getElementValue("graph-type");
    const graphComposition = getElementValue("graph-composition");
    const overwrite = getElementValue("overwrite");
    const figureWidth = getElementValue("figure-width");
    const figureHeight = getElementValue("figure-height");
    const fontSize = getElementValue("font-size");

    const body = createBody({
        "directory-list": directories,
        "metric-list": metrics,
        "graph-type": graphType,
        "graph-composition": graphComposition,
        overwrite: overwrite,
        "figure-width": figureWidth,
        "figure-height": figureHeight,
        "font-size": fontSize,
    });

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

// Exportar resultados
async function exportResults() {
    const directories = getCheckedValues("directory-list");
    const metrics = getCheckedValues("metric-list");
    const body = createBody({
        "directory-list": directories,
        "metric-list": metrics,
    });

    const response = await fetch("/graphs/export-results", {
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

assignSubmitFunction("load-config-sub", loadConfig);
assignSubmitFunction("save-config-sub", saveConfig);
assignSubmitFunction("select-all-directories-sub", () =>
    selectAllCheckboxes("directory-list")
);
assignSubmitFunction("deselect-all-directories-sub", () =>
    deselectAllCheckboxes("directory-list")
);
assignSubmitFunction("select-all-metrics-sub", () =>
    selectAllCheckboxes("metric-list")
);
assignSubmitFunction("deselect-all-metrics-sub", () =>
    deselectAllCheckboxes("metric-list")
);
assignSubmitFunction("generate-graphs-sub", generateGraphs);
assignSubmitFunction("export-results-sub", exportResults);
