function getElementValue(id) {
    return document.getElementById(id).value;
}

function getRadioValue(name) {
    const radio = document.querySelector(`input[name="${name}"]:checked`);
    return radio ? radio.value : null;
}

function getListValues(name) {
    return Array.from(document.querySelectorAll(`[name="${name}"]`)).map(
        (el) => el.value
    );
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
function selectAllTextCheckboxes(listName, prefix) {
    const checkboxes = document.querySelectorAll(
        `input[type="checkbox"][name="${listName}"]`
    );
    checkboxes.forEach((checkbox) => {
        document.getElementById(`${prefix}-${checkbox.value}`).disabled = false;
        checkbox.checked = true;
    });
}

function deselectAllTextCheckboxes(listName, prefix) {
    const checkboxes = document.querySelectorAll(
        `input[type="checkbox"][name="${listName}"]`
    );
    checkboxes.forEach((checkbox) => {
        document.getElementById(`${prefix}-${checkbox.value}`).disabled = true;
        checkbox.checked = false;
    });
}

function createToastFunction(id) {
    return (message, type = "success") => {
        const outputConfigToast = document.getElementById(id);
        outputConfigToast.classList.remove(
            "text-bg-success",
            "text-bg-warning"
        );
        outputConfigToast.classList.add("text-bg-" + type);
        const btnClose = outputConfigToast.querySelector(".btn-close");
        btnClose.classList.remove("btn-close-success", "btn-close-warning");
        btnClose.classList.add("btn-close-" + type);
        const toastBody = outputConfigToast?.querySelector(".toast-body");
        if (toastBody) toastBody.textContent = message;
        const toastBootstrap =
            bootstrap.Toast.getOrCreateInstance(outputConfigToast);
        toastBootstrap.show();
    };
}

function getLoads(graphConfig) {
    const allLoadList = getListValues("load-list");
    let loadFilter = "";
    const nonEmptyLoads = allLoadList.filter((load) => load !== "");
    const nonEmptyIndices = [];
    allLoadList.forEach((load, index) => {
        if (load !== "") {
            nonEmptyIndices.push(index);
        }
    });
    if (nonEmptyIndices.length > 0) {
        let ranges = [];
        let start = nonEmptyIndices[0];
        let end = nonEmptyIndices[0];
        for (let i = 1; i < nonEmptyIndices.length; i++) {
            if (nonEmptyIndices[i] === end + 1) {
                end = nonEmptyIndices[i];
            } else {
                if (start === end) {
                    ranges.push(`${start}`);
                } else {
                    ranges.push(`${start}-${end}`);
                }
                start = end = nonEmptyIndices[i];
            }
        }
        if (start === end) {
            ranges.push(`${start}`);
        } else {
            ranges.push(`${start}-${end}`);
        }
        loadFilter = ranges.join(",");
        if (loadFilter === `0-${allLoadList.length - 1}`) {
            loadFilter = "";
        }
    }
    graphConfig["loads"] = nonEmptyLoads;
    if (loadFilter) {
        graphConfig["load-filter"] = loadFilter;
    }
}

function setLoads(graphConfig) {
    const loads = graphConfig.loads;
    const nonEmptyLoads = loads.filter((load) => load !== "");
    if (nonEmptyLoads) {
        if (!graphConfig["load-filter"]) {
            nonEmptyLoads.forEach((load, index) => {
                const loadInput = document.getElementById(`load-${index}`);
                if (loadInput) {
                    loadInput.value = load;
                }
            });
        } else {
            const ranges = graphConfig["load-filter"].split(",");
            let loadIndex = 0;
            ranges.forEach((range) => {
                if (range.includes("-")) {
                    const [start, end] = range.split("-").map(Number);
                    if (isNaN(start) || isNaN(end)) {
                        return;
                    }
                    for (let i = start; i <= end; i++) {
                        const loadInput = document.getElementById(`load-${i}`);
                        if (loadInput) {
                            loadInput.value = nonEmptyLoads[loadIndex] || "";
                            loadIndex++;
                        }
                    }
                } else {
                    const i = Number(range);
                    if (isNaN(i)) {
                        return;
                    }
                    const loadInput = document.getElementById(`load-${i}`);
                    if (loadInput) {
                        loadInput.value = nonEmptyLoads[loadIndex] || "";
                        loadIndex++;
                    }
                }
            });
        }
    }
}
