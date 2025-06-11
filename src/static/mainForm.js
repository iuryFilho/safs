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
        mainForm.action = "/config/get-metrics";
        mainForm.submit();
    }
});

mainForm.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    checkbox.checked = false;
    const labelElement = document.getElementById(`label-${checkbox.value}`);
    if (labelElement) {
        labelElement.disabled = true;
        labelElement.value = "";
        checkbox.addEventListener("change", function () {
            labelElement.disabled = !this.checked;
        });
    }
});

// Carregar configuração
async function loadConfig() {
    const inputConfig = getElementValue("input-config");
    if (!inputConfig) {
        return;
    }
    const response = await fetch("/config/load-config", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: createBody({
            "input-config": inputConfig,
        }),
    });
    const data = await response.json();

    const showToast = createToastFunction("input-config-toast");

    if (data.error) {
        showToast("Error: " + data.error, "warning");
    } else {
        const configData = data.config_data;

        if (configData.directories) {
            Object.entries(configData.directories).forEach(([dir, label]) => {
                const dirCheckbox = document.getElementById(dir);
                const labelElement = document.getElementById(`label-${dir}`);
                dirCheckbox.checked = true;
                labelElement.disabled = false;
                labelElement.value = label;
            });
        }

        if (configData.metrics) {
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
        }

        if (configData["graph-config"]) {
            setLoads(configData["graph-config"]);
        }
        if (debugOutput) {
            setOutput();
        }
        showToast(data.message || "Configuration loaded successfully!");
    }
}

// Salvar configuração
async function saveConfig() {
    const outputConfig = getElementValue("output-config");
    const directories = getCheckedValues("directory-list");
    const labels = directories.map((dir) => {
        return document.getElementById(`label-${dir}`).value;
    });
    const metrics = getCheckedValues("metric-list");
    const graphConfig = {};
    getLoads(graphConfig);

    const body = {
        "output-config": outputConfig,
        "directory-list": directories,
        labels: labels,
        "metric-list": metrics,
        "graph-config": graphConfig,
    };

    const response = await fetch("/config/save-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const data = await response.json();

    const showToast = createToastFunction("output-config-toast");

    if (data.error) {
        showToast("Erro: " + data.error, "warning");
    } else {
        showToast(data.message || "Configuração salva com sucesso!");
    }
}

async function updateMetricType() {
    const previousMetricType = getElementValue("previous-metric-type");
    const metricType = getRadioValue("metric-type");

    if (previousMetricType !== metricType) {
        const response = await fetch("/config/update-metric-type", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "metric-type": metricType }),
        });

        const data = response.json();
        if (!data.error) {
            window.location.reload();
        } else {
            alert(data.error);
        }
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
    const loadMap = getListValues("load-list").reduce((acc, load, index) => {
        if (load !== "") {
            acc[index.toString()] = load;
        }
        return acc;
    }, {});

    const body = {
        "directory-list": directories,
        "directory-labels": directoryLabels,
        "metric-list": metrics,
        "graph-type": graphType,
        overwrite: overwrite,
        "figure-width": figureWidth,
        "figure-height": figureHeight,
        "font-size": fontSize,
        loads: loadMap,
    };

    const response = await fetch("/generation/generate-graphs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const data = await response.json();
    const showToast = createToastFunction("generate-graphs-toast");
    if (data.error) {
        showToast("Erro: " + data.error, "warning");
    } else {
        showToast(data.message);
    }
}

// Exportar resultados
async function exportResults() {
    const directories = getCheckedValues("directory-list");
    const directoryLabels = directories.map((dir) => {
        return document.getElementById(`label-${dir}`).value;
    });
    const metrics = getCheckedValues("metric-list");
    const loadMap = getListValues("load-list").reduce((acc, load, index) => {
        if (load !== "") {
            acc[index.toString()] = load;
        }
        return acc;
    }, {});
    const overwrite = getElementValue("overwrite");

    const body = {
        "directory-list": directories,
        "directory-labels": directoryLabels,
        "metric-list": metrics,
        overwrite: overwrite,
        loads: loadMap,
    };

    const response = await fetch("/generation/export-results", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const data = await response.json();
    console.log(data);

    const showToast = createToastFunction("export-results-toast");
    if (data.error) {
        showToast("Erro: " + data.error, "warning");
    } else {
        showToast(data.message);
    }
}

assignSubmitFunction("load-config-sub", loadConfig);
assignSubmitFunction("save-config-sub", saveConfig);
assignSubmitFunction("select-all-directories-sub", () =>
    selectAllTextCheckboxes("directory-list", "label")
);
assignSubmitFunction("deselect-all-directories-sub", () =>
    deselectAllTextCheckboxes("directory-list", "label")
);

document.querySelectorAll(".accordion-collapse").forEach((metricGroup) => {
    const metricCheckboxes = metricGroup.querySelectorAll(
        'input[type="checkbox"][name="metric-list"]'
    );
    const selectAllBtn = metricGroup.querySelector(
        `#select-all-${metricGroup.id}-sub`
    );
    const deselectAllBtn = metricGroup.querySelector(
        `#deselect-all-${metricGroup.id}-sub`
    );

    selectAllBtn.addEventListener("click", () => {
        metricCheckboxes.forEach((checkbox) => {
            checkbox.checked = true;
        });
    });

    deselectAllBtn.addEventListener("click", () => {
        metricCheckboxes.forEach((checkbox) => {
            checkbox.checked = false;
        });
    });
});

assignSubmitFunction("select-all-metrics-sub", () =>
    selectAllCheckboxes("metric-list")
);
assignSubmitFunction("deselect-all-metrics-sub", () =>
    deselectAllCheckboxes("metric-list")
);

assignSubmitFunction("radio-individual", () => updateMetricType());
assignSubmitFunction("radio-grouped", () => updateMetricType());

assignSubmitFunction("generate-graphs-sub", generateGraphs);
assignSubmitFunction("export-results-sub", exportResults);
