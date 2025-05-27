const navbarForm = document.getElementById("navbar-form");

navbarForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const action = event.submitter.value;
    console.log(action);
});

async function clearSession() {
    const response = await fetch("/clear-session", {
        method: "POST",
    });
    const data = await response.json();
    if (data.message) {
        alert(data.message + "\nReloading page...");
        window.location.reload();
    } else {
        alert("Failed to clear session: " + data.error);
    }
}

assignSubmitFunction("clear-session-sub", clearSession);
