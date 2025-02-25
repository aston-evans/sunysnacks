let token = localStorage.getItem("token"); // Get the token from localStorage

if (!token) {
    console.error("No token found! Redirecting to login...");
    window.location.href = "/auth/login";  // Redirect if not logged in
} else {
    // Include the token in the Authorization header
    fetch("/menu", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`  // Include the token
        }
    })
    .then(response => {
        if (response.ok) {
            return response.text();  // Process the response
        } else {
            console.error("Access denied:", response.status);
            window.location.href = "/auth/login";  // Redirect if unauthorized
        }
    })
    .then(data => {
        console.log("Protected content loaded:", data);
        document.body.innerHTML = data;  // Replace page content with menu
    })
    .catch(error => console.error("Error fetching menu:", error));
}
