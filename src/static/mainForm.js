const mainForm = document.getElementById("form");

// Initialization of Bootstrap tooltips
document.addEventListener("DOMContentLoaded", function () {
    var tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

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
    if (action === "load-directory") {
        const formData = new FormData(mainForm);
        const jsonData = {};
        jsonData["base-directory"] = formData.get("base-directory");
        jsonData["metric-type"] = formData.get("metric-type") || "individual";
        fetch("/config/load-directory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(jsonData),
        }).then((response) => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
});

const checkboxSections = ["directories-section", "metrics-section"];
checkboxSections.forEach((sectionId) => {
    document
        .getElementById(sectionId)
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
});

// Carregar configuração
async function loadConfig() {
    const inputConfig = getElementValue("input-config");
    const response = await fetch("/config/load-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
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
            document
                .getElementById("directories-section")
                .querySelectorAll('input[type="checkbox"]')
                .forEach((checkbox) => {
                    checkbox.checked = false;
                    const labelElement = document.getElementById(
                        `label-${checkbox.value}`
                    );
                    if (labelElement) {
                        labelElement.disabled = true;
                        labelElement.value = "";
                    }
                });
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
                    const metricGroupHeader = document.getElementById(
                        `${metricGroup}-header`
                    );
                    if (metricGroupHeader) {
                        metricGroupHeader.classList.remove("collapsed");
                        metricGroupHeader.ariaExpanded = "true";
                        document
                            .getElementById(`${metricGroup}`)
                            .classList.add("show");
                    }

                    metricList.forEach((metric) => {
                        const metricCheckbox = document.querySelector(
                            `input[type="checkbox"][name="metric-list"][value="${metric}"]`
                        );
                        if (metricCheckbox) {
                            metricCheckbox.checked = true;
                        }
                    });
                }
            );
        }

        if (configData["graph-config"]) {
            if (configData["graph-config"]["loads"]) {
                setLoads(configData["graph-config"]);
            }
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
    const groupedMetrics = getGroupedMetrics();
    const graphConfig = {};
    getLoads(graphConfig);

    const body = {
        "output-config": outputConfig,
        "directory-list": directories,
        labels: labels,
        "grouped-metrics": groupedMetrics,
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
    } else if (data.message) {
        showToast(data.message);
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

async function updateUseCustomLoads() {
    const useCustomLoads = getCheckedValue("use-custom-loads");
    console.log("useCustomLoads:", useCustomLoads);

    const response = await fetch("/config/update-use-custom-loads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "use-custom-loads": useCustomLoads }),
    });

    const data = await response.json();
    if (!data.error) {
        window.location.reload();
    } else {
        alert(data.error);
    }
}

// Gerar gráficos
async function generateGraphs() {
    const directories = getCheckedValues("directory-list");
    const directoryLabels = directories.map((dir) => {
        return document.getElementById(`label-${dir}`).value;
    });
    const groupedMetrics = getGroupedMetrics();
    const graphType = getElementValue("graph-type");
    const language = getElementValue("language");
    const overwrite = getElementValue("overwrite");
    const useGrid = getElementValue("use-grid");
    const ylimLow = getElementValue("ylim-low");
    const ylimUp = getElementValue("ylim-up");
    const xAxisDirection = getElementValue("x-axis-direction");
    const title = getElementValue("title");
    const xlabel = getElementValue("xlabel");
    const ylabel = getElementValue("ylabel");
    const figureWidth = getElementValue("figure-width");
    const figureHeight = getElementValue("figure-height");
    const graphFontSize = getElementValue("graph-font-size");
    const legendFontSize = getElementValue("legend-font-size");
    const legendPosition = getElementValue("legend-position");
    const anchorX = getElementValue("anchor-x");
    const anchorY = getElementValue("anchor-y");
    const frameon = getElementValue("frameon");
    const maxColumns = getElementValue("max-columns");
    const useCustomLoads = getCheckedValue("use-custom-loads");
    let loadMap;
    let loadPointsFilter;
    if (useCustomLoads) {
        loadMap = getListValues("load-list").reduce((acc, load, index) => {
            if (load !== "") {
                acc[index.toString()] = load;
            }
            return acc;
        }, {});
        loadPointsFilter = "";
    } else {
        loadMap = {};
        loadPointsFilter = getElementValue("load-points-filter");
    }

    const body = {
        "directory-list": directories,
        labels: directoryLabels,
        "grouped-metrics": groupedMetrics,
        "graph-type": graphType,
        language: language,
        overwrite: overwrite,
        "use-grid": useGrid,
        "ylim-low": ylimLow,
        "ylim-up": ylimUp,
        "x-axis-direction": xAxisDirection,
        title: title,
        xlabel: xlabel,
        ylabel: ylabel,
        "figure-width": figureWidth,
        "figure-height": figureHeight,
        "graph-font-size": graphFontSize,
        "legend-font-size": legendFontSize,
        "legend-position": legendPosition,
        "anchor-x": anchorX,
        "anchor-y": anchorY,
        frameon: frameon,
        "max-columns": maxColumns,
        loads: loadMap,
        "load-points-filter": loadPointsFilter,
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
    const groupedMetrics = getGroupedMetrics();
    const useCustomLoads = getCheckedValue("use-custom-loads");
    let loadMap;
    let loadPointsFilter;
    if (useCustomLoads) {
        loadMap = getListValues("load-list").reduce((acc, load, index) => {
            if (load !== "") {
                acc[index.toString()] = load;
            }
            return acc;
        }, {});
        loadPointsFilter = "";
    } else {
        loadMap = {};
        loadPointsFilter = getElementValue("load-points-filter");
    }
    const overwrite = getElementValue("overwrite");

    const body = {
        "directory-list": directories,
        labels: directoryLabels,
        "grouped-metrics": groupedMetrics,
        overwrite: overwrite,
        loads: loadMap,
        "load-points-filter": loadPointsFilter,
    };

    const response = await fetch("/generation/export-results", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const data = await response.json();

    const showToast = createToastFunction("export-results-toast");
    if (data.error) {
        showToast("Erro: " + data.error, "warning");
    } else {
        showToast(data.message);
    }
}

assignSubmitFunction("load-config-sub", loadConfig);
assignSubmitFunction("save-config-sub", saveConfig);

assignSubmitFunction("select-all-directories-btn", () =>
    selectAllTextCheckboxes("directory-list", "label")
);
assignSubmitFunction("deselect-all-directories-btn", () =>
    deselectAllTextCheckboxes("directory-list", "label")
);

document.querySelectorAll(".accordion-collapse").forEach((metricGroup) => {
    const metricCheckboxes = metricGroup.querySelectorAll(
        'input[type="checkbox"][name="metric-list"]'
    );
    const selectAllBtn = metricGroup.querySelector(
        `#select-all-${metricGroup.id}-btn`
    );
    const deselectAllBtn = metricGroup.querySelector(
        `#deselect-all-${metricGroup.id}-btn`
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

assignSubmitFunction("select-all-metrics-btn", () =>
    selectAllCheckboxes("metric-list")
);
assignSubmitFunction("deselect-all-metrics-btn", () =>
    deselectAllCheckboxes("metric-list")
);

assignSubmitFunction("radio-individual", () => updateMetricType());
assignSubmitFunction("radio-grouped", () => updateMetricType());

document
    .getElementById("use-custom-loads")
    .addEventListener("change", updateUseCustomLoads);

assignSubmitFunction("generate-graphs-sub", generateGraphs);
assignSubmitFunction("export-results-sub", exportResults);
