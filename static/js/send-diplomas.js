document.getElementById("sendDiplomasButton").addEventListener("click", async () => {
    // Confirm before sending
    if (!confirm("Are you sure you want to send diplomas to all recipients?")) {
        return;
    }

    // Get the subject and body values
    const subject = document.getElementById("email-subject").value || "Your Diploma is Ready!";
    const body = document.getElementById("email-body").value || "Hello, your diploma is attached.";

    try {
        // Show a loading indicator (optional)
        const button = document.getElementById("sendDiplomasButton");
        button.textContent = "Sending...";
        button.disabled = true;

        // Send POST request to the /send_email endpoint
        const response = await fetch("/send_email", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ subject, body }) // Include subject and body in the payload
        });

        const result = await response.json();

        if (response.ok) {
            alert("Emails sent successfully!");
            console.log(result); // Log results for debugging
        } else {
            alert(`Failed to send emails: ${result.error || "Unknown error"}`);
        }
    } catch (error) {
        console.error("An error occurred:", error);
        alert("An unexpected error occurred. Please try again.");
    } finally {
        // Reset the button state
        const button = document.getElementById("sendDiplomasButton");
        button.textContent = "Send Diplomas";
        button.disabled = false;
    }
});

function fetchProgress() {
    fetch("/progress")
        .then((response) => response.json())
        .then((data) => {
            const progressBar = document.getElementById("sendingProgressBar");
            const progressLabel = document.getElementById("progressLabel");

            const progress = data.progress || 0;		
            // Update the progress bar value
            progressBar.value = progress;

            // Update the fallback label text
            progressLabel.textContent = `${progress}%`;
        })
        .catch((error) => console.error("Error fetching progress:", error));
}



// Fetch progress every second
setInterval(fetchProgress, 1000);
