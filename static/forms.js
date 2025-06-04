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
        document.getElementById(`label-${checkbox.value}`).disabled = false;
        checkbox.checked = true;
    });
}

function deselectAllCheckboxes(listName) {
    const checkboxes = document.querySelectorAll(
        `input[type="checkbox"][name="${listName}"]`
    );
    checkboxes.forEach((checkbox) => {
        document.getElementById(`label-${checkbox.value}`).disabled = true;
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
