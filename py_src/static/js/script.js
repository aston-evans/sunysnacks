document.addEventListener("DOMContentLoaded", function () {
    let loginForm = document.getElementById("login");

    if (!loginForm) {
        console.error("Login form not found! Check if the ID is correct.");
        return; // Exit the function if the form doesn't exist
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        let username = document.getElementById("username").value;
        let password = document.getElementById("password").value;

        console.log("Logging in with:", username, password);

        let response = await fetch("http://127.0.0.1:8000/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ "username": username, "password": password })
        });

        if (response.ok) {
            let result = await response.json();  // Read JSON response **only once**
            console.log("Login successful, token:", result.access_token);
            localStorage.setItem("token", result.access_token);
            window.location.href = "/menu";
        } else {
            let errorText = await response.text();  // Read error response as text
            console.error("Login failed:", response.status, errorText);
            document.getElementById("error").textContent = "Invalid username or password.";
        }
    });
});
