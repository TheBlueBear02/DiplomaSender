document.getElementById("reviewButton").addEventListener("click", async () => {
    // Retrieve the test email address
    const testEmail = document.getElementById("testEmailInput").value.trim();
    if (!testEmail) {
        alert("Please enter a valid email address.");
        return;
    }


 try {
    // Retrieve email subject and body
    const subject = document.getElementById("email-subject").value || "Test Email";
    const body = document.getElementById("email-body").value || "This is a test email.";

    // Send the test email via an API call (update the endpoint as needed)
    const response = await fetch("/send_email", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            to: testEmail,
            subject: subject,
            body: body,
        })
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
 } 

	//finally {
          // Reset the button state
        // const button = document.getElementById("reviewButton");
        // button.textContent = "Review send";
        //button.disabled = false;
        //}

});
