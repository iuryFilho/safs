const navbarForm = document.getElementById("navbar-form");

navbarForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const action = event.submitter.value;
    console.log(action);
});

async function clearSession() {
    confirmation = confirm(
        "Are you sure you want to clear the session? This will remove all saved data."
    );
    if (!confirmation) return;

    const response = await fetch("/config/clear-session", {
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
