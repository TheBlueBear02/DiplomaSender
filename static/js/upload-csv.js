document.addEventListener('DOMContentLoaded', () => {
    const csvUploadBox = document.getElementById('csvUploadBox');
    const recipientListInput = document.getElementById('recipientListInput');
    const recipientListTable = document.getElementById('recipientListTable').getElementsByTagName('tbody')[0];
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');

    if (!recipientListInput || !recipientListTable || !selectAllCheckbox || !csvUploadBox) {
        console.error("One or more required elements are missing in the DOM.");
        return;
    }

    console.log("CSV Drag-and-Drop functionality loaded.");

    // Drag-and-Drop Event Listeners
    ['dragenter', 'dragover'].forEach(event => {
        csvUploadBox.addEventListener(event, (e) => {
            e.preventDefault();
            csvUploadBox.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        csvUploadBox.addEventListener(event, (e) => {
            e.preventDefault();
            csvUploadBox.classList.remove('drag-over');
        });
    });

    csvUploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;

        if (files.length > 0) {
            const file = files[0];
            console.log("File dropped:", file.name);

            if (file.type === 'text/csv') {
                // Send the CSV file to the server
                uploadCSV(file);
            } else {
                alert("Invalid file type. Only CSV files are supported.");
            }
        } else {
            console.warn("No files detected in drop event.");
        }
    });

    // File Input Change Event Listener
    recipientListInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            console.log("File selected via input:", file.name);

            if (file.type === 'text/csv') {
                // Send the CSV file to the server
                uploadCSV(file);
            } else {
                alert("Invalid file type. Only CSV files are supported.");
            }
        } else {
            console.warn("No file selected via input.");
        }
    });

    // Function to upload CSV file to the server
    const uploadCSV = (file) => {
        console.log("Uploading CSV file to server:", file.name);

        const formData = new FormData();
        formData.append('recipient_list', file);

        fetch('/upload-csv', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("CSV uploaded successfully:", data.students);
                renderRecipientList(data.students);
            } else {
                console.error("Error uploading CSV:", data.error);
                alert("Error uploading CSV: " + data.error);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert("An error occurred while uploading the CSV.");
        });
    };

    // Function to render recipient list in the table
    const renderRecipientList = (students) => {
        // Clear existing rows
        recipientListTable.innerHTML = '';

        students.forEach((student, index) => {
            const row = recipientListTable.insertRow();
            row.innerHTML = `
                <td><input type="checkbox" class="rowCheckbox" id="select_${index}" /></td>
                <td>${student.name}</td>
                <td>${student.email}</td>
                <td>${student.new}</td>
                <td>${student.send}</td>
            `;
        });

        console.log("Recipient list rendered successfully.");
    };
     // Event Listener for "Select All" checkbox
     selectAllCheckbox.addEventListener('change', () => {
        const allCheckboxes = recipientListTable.querySelectorAll('.rowCheckbox');
        const selectAll = selectAllCheckbox.checked;

        allCheckboxes.forEach(checkbox => {
            checkbox.checked = selectAll;
        });

        console.log(`All rows ${selectAll ? "selected" : "deselected"}.`);
    });

    // Example: Simulating the fetch data (replace with your actual fetch logic)
    const exampleStudents = [
        { name: "John Doe", email: "john@example.com", new: "Yes", send: "Yes" },
        { name: "Jane Smith", email: "jane@example.com", new: "No", send: "No" },
    ];

    // Simulate rendering the table with example data
    renderRecipientList(exampleStudents);
});
