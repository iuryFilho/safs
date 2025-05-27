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
