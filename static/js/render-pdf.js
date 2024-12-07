document.addEventListener('DOMContentLoaded', () => {
    const diplomaInput = document.getElementById('diplomaTemplate');
    const canvas = document.getElementById('pdfPreview');
    const context = canvas.getContext('2d');

    // Function to render PDF in canvas
    const renderPDF = (file) => {
        const fileReader = new FileReader();
        fileReader.onload = function () {
            const pdfData = new Uint8Array(this.result);

            // Load PDF using PDF.js
            pdfjsLib.getDocument({ data: pdfData }).promise.then((pdf) => {
                // Render the first page
                pdf.getPage(1).then((page) => {
                    const viewport = page.getViewport({ scale: 1 });
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;

                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport,
                    };
                    page.render(renderContext);
                });
            }).catch((error) => {
                console.error("Error rendering PDF:", error);
            });
        };
        fileReader.readAsArrayBuffer(file);
    };

    // Listen for changes on the file input
    diplomaInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file.type === 'application/pdf') {
            renderPDF(file); // Render PDF preview
        } else {
            console.error("Invalid file type. Please upload a PDF.");
        }
    });
});
