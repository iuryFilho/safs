const mainForm = document.getElementById("form");
const debugOutput = document.getElementById("debug-output");

if (debugOutput) {
    function setOutput() {
        debugOutput.textContent = "";
        for (const [key, value] of new FormData(mainForm)) {
            debugOutput.textContent += `${key}: ${value}\n`;
        }
    }
    document.addEventListener("DOMContentLoaded", setOutput);
    (() => {
        const checkboxes = mainForm.querySelectorAll(
            'input[type="checkbox"][name="directory-list"], input[type="checkbox"][name="metric-list"]'
        );
        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", function () {
                setOutput();
            });
        });
        const selections = mainForm.querySelectorAll("select");
        selections.forEach((select) => {
            select.addEventListener("change", function () {
                setOutput();
            });
        });
        const graphSection = mainForm.querySelector("#graph-section");
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
mainForm.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        if (event.target.id == "base-directory") {
            return;
        } else if (
            ["INPUT", "TEXTAREA"].includes(event.target.tagName) &&
            event.target.type !== "textarea"
        ) {
            event.preventDefault();
        }
    }
});

mainForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const action = event.submitter.value;
    console.log(action);
    if (action === "get-metrics") {
        mainForm.method = "post";
        mainForm.action = "/metrics/get-metrics";
        mainForm.submit();
    }
});

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

        mainForm
            .querySelectorAll('input[type="checkbox"]')
            .forEach((checkbox) => {
                checkbox.checked = false;
                const labelElement = document.getElementById(
                    `label-${checkbox.value}`
                );
                if (labelElement) {
                    labelElement.disabled = true;
                    labelElement.value = "";
                    checkbox.addEventListener("change", function () {
                        labelElement.disabled = !this.checked;
                    });
                }
            });

        Object.entries(configData.directories).forEach(([dir, label]) => {
            const dirCheckbox = document.getElementById(dir);
            const labelElement = document.getElementById(`label-${dir}`);
            dirCheckbox.checked = true;
            labelElement.disabled = false;
            labelElement.value = label;
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
    const labels = directories.map((dir) => {
        return document.getElementById(`label-${dir}`).value;
    });
    console.log("Labels:", labels);

    const metrics = getCheckedValues("metric-list");

    const body = createBody({
        "output-config": outputConfig,
        "directory-list": directories,
        labels: labels,
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

// Gerar gráficos
async function generateGraphs() {
    const directories = getCheckedValues("directory-list");
    const directoryLabels = directories.map((dir) => {
        return document.getElementById(`label-${dir}`).value;
    });
    const metrics = getCheckedValues("metric-list");
    const graphType = getElementValue("graph-type");
    const graphComposition = getElementValue("graph-composition");
    const overwrite = getElementValue("overwrite");
    const figureWidth = getElementValue("figure-width");
    const figureHeight = getElementValue("figure-height");
    const fontSize = getElementValue("font-size");

    const body = createBody({
        "directory-list": directories,
        "directory-labels": directoryLabels,
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
