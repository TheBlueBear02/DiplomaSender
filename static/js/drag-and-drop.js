document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const diplomaInput = document.getElementById('diplomaTemplate');
    const canvasUpload = document.getElementById('pdfPreview');
    const canvasPlacement = document.getElementById('pdfPreviewPlacement');
    const contextUpload = canvasUpload.getContext('2d');
    const contextPlacement = canvasPlacement.getContext('2d');

    if (!uploadBox || !diplomaInput || !canvasUpload || !canvasPlacement) {
        console.error("One or more required elements are missing in the DOM.");
        return;
    }

    console.log("Drag-and-Drop JavaScript loaded successfully.");

    // Function to render PDF in a specified canvas
    const renderPDF = (file, canvas, context) => {
        console.log(`Rendering PDF (${file.name}) on canvas: ${canvas.id}`);
        const fileReader = new FileReader();

        fileReader.onload = function () {
            const pdfData = new Uint8Array(this.result);
            console.log("PDF data loaded successfully. Initializing PDF.js.");

            pdfjsLib.getDocument({ data: pdfData }).promise.then((pdf) => {
                console.log(`PDF loaded. Total pages: ${pdf.numPages}`);
                pdf.getPage(1).then((page) => {
                    const viewport = page.getViewport({ scale: 1.5 });
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;

                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport,
                    };
                    page.render(renderContext);
                    console.log(`PDF rendered successfully on ${canvas.id}.`);
                }).catch((err) => {
                    console.error("Error rendering PDF page:", err);
                });
            }).catch((err) => {
                console.error("Error loading PDF:", err);
            });
        };

        fileReader.onerror = function (err) {
            console.error("Error reading file:", err);
        };

        fileReader.readAsArrayBuffer(file);
    };

    // Function to handle file upload to the backend
    const uploadFileToServer = (file) => {
        console.log("Uploading file to server:", file.name);

        // Prepare the FormData object
        const formData = new FormData();
        formData.append('diploma_template', file);

        // Send the file to the backend using fetch
        fetch('/upload-template', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("File uploaded successfully:", data);
            //alert("File uploaded successfully!");
        })
        .catch(error => {
            console.error("Error uploading file:", error);
            alert("Error uploading file.");
        });
    };

    // Drag-and-Drop Event Listeners
    ['dragenter', 'dragover'].forEach(event => {
        uploadBox.addEventListener(event, (e) => {
            e.preventDefault();
            uploadBox.classList.add('drag-over');
            console.log(`Event triggered: ${event}`);
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        uploadBox.addEventListener(event, (e) => {
            e.preventDefault();
            uploadBox.classList.remove('drag-over');
            console.log(`Event triggered: ${event}`);
        });
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;

        if (files.length > 0) {
            const file = files[0];
            console.log("File dropped:", file.name);

            if (file.type === 'application/pdf') {
                // Render the PDF in both canvases
                renderPDF(file, canvasUpload, contextUpload); // Upload preview
                renderPDF(file, canvasPlacement, contextPlacement); // Name Placement preview

                // Upload the file to the server
                uploadFileToServer(file);

                diplomaInput.files = files; // Assign files to the input
                console.log("File assigned to input for form submission.");
            } else {
                console.warn("Invalid file type. Only PDFs are supported.");
            }
        } else {
            console.warn("No files detected in drop event.");
        }
    });

    // File Input Change Event Listener
    diplomaInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            console.log("File selected via input:", file.name);

            if (file.type === 'application/pdf') {
                // Render the PDF in both canvases
                renderPDF(file, canvasUpload, contextUpload); // Upload preview
                renderPDF(file, canvasPlacement, contextPlacement); // Name Placement preview

                // Upload the file to the server
                uploadFileToServer(file);
            } else {
                console.warn("Invalid file type selected. Only PDFs are supported.");
            }
        } else {
            console.warn("No file selected via input.");
        }
    });
});
