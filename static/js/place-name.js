document.addEventListener('DOMContentLoaded', () => {
    const canvasPlacement = document.getElementById('pdfPreviewPlacement');
    const placeNameButton = document.getElementById('placeNameButton');
    const xPositionInput = document.getElementById('xPositionInput');
    const yPositionInput = document.getElementById('yPositionInput');
    //const studentNameInput = document.getElementById('studentName');
    const namePlacementForm = document.getElementById('namePlacementForm');
    
    if (!canvasPlacement || !placeNameButton ){//|| !studentNameInput) {
        console.error("One or more required elements are missing.");
        return;
    }

    console.log("Name Placement JavaScript loaded.");

    // Function to render PDF on the canvas
    const renderPDFOnCanvas = (pdfUrl, canvas, context) => {
        pdfjsLib.getDocument(pdfUrl).promise.then((pdf) => {
            pdf.getPage(1).then((page) => {
                const viewport = page.getViewport({ scale: 1.5 });
                canvas.width = viewport.width;
                canvas.height = viewport.height;

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport,
                };
                page.render(renderContext);
                console.log("Updated PDF rendered successfully.");
            }).catch(err => {
                console.error("Error rendering updated PDF page:", err);
            });
        }).catch(err => {
            console.error("Error loading updated PDF:", err);
        });
    };


    placeNameButton.addEventListener('click', () => {
        const xPosition = xPositionInput.value;
        const yPosition = yPositionInput.value;
        // const studentName = studentNameInput.value;

        //if (!studentName) {
        //    alert("Please enter a student name.");
        //    return;
        //}

        // Update hidden inputs
        document.getElementById('xPosition').value = xPosition;
        document.getElementById('yPosition').value = yPosition;

        // Create FormData to send
        const formData = new FormData(namePlacementForm);

        // Send POST request to the backend
        fetch('/place-name', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                //alert("Name placed successfully!");
                console.log("PDF URL:", data.pdf_url);

                // Optionally update the Name Placement preview
                const pdfUrl = data.pdf_url;
                const canvasPlacement = document.getElementById('pdfPreviewPlacement');
                const contextPlacement = canvasPlacement.getContext('2d');

                // Render the updated PDF
                pdfjsLib.getDocument(pdfUrl).promise.then((pdf) => {
                    pdf.getPage(1).then((page) => {
                        const viewport = page.getViewport({ scale: 1.5 });
                        canvasPlacement.width = viewport.width;
                        canvasPlacement.height = viewport.height;

                        const renderContext = {
                            canvasContext: contextPlacement,
                            viewport: viewport,
                        };
                        page.render(renderContext);
                    });
                });
            } else {
                alert("Error placing name: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while placing the name.");
        });
    });
});
// New functionality for the Next button
document.getElementById("nextButton").addEventListener("click", () => {
    // Close the Name Placement section
    const namePlacementSection = document.querySelector("#namePlacementForm").closest(".card");
    const namePlacementContent = namePlacementSection.querySelector(".content");
    namePlacementContent.style.display = "none";

    // Open the Upload Recipient List section
    const recipientListSection = document.querySelector("#csvUploadBox").closest(".card");
    const recipientListContent = recipientListSection.querySelector(".content");
    recipientListContent.style.display = "block";
});

