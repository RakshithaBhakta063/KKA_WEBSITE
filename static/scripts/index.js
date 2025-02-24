function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.style.display = 'none');
    
    // Show selected section
    document.getElementById(sectionId).style.display = 'block';
}

function searchTable(tableId, searchInputId) {
    let input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById(searchInputId);
    filter = input.value.toLowerCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        let rowVisible = false;
        td = tr[i].getElementsByTagName("td");
        for (j = 0; j < td.length; j++) {
            if (td[j]) {
                txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toLowerCase().indexOf(filter) > -1) {
                    rowVisible = true;
                    break;
                }
            }
        }
        tr[i].style.display = rowVisible ? "" : "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    generateCharts();
});

function generateCharts() {
    const cityData = {};
    const postcodeData = {};
    let loginCount = 0;
    let registrationCount = 0;

    // Get the user table and registration table
    const userTable = document.getElementById("userTable");
    const registrationTable = document.getElementById("registrationTable");

    const userRows = userTable.getElementsByTagName("tr");
    const registrationRows = registrationTable.getElementsByTagName("tr");

    // Loop through the user table to count logins
    for (let i = 1; i < userRows.length; i++) {
        let cells = userRows[i].getElementsByTagName("td");
        let city = cells[3].innerText.trim(); // Nearest Capital City
        let postcode = cells[4].innerText.trim(); // Postcode

        // Count city and postcode data
        cityData[city] = (cityData[city] || 0) + 1;
        postcodeData[postcode] = (postcodeData[postcode] || 0) + 1;

        // Count logins (based on user rows)
        loginCount++;
    }

    // Loop through the registration table to count actual registrations
    for (let i = 1; i < registrationRows.length; i++) {
        let cells = registrationRows[i].getElementsByTagName("td");

        // Check if the "Number of People" column (4th column) is greater than 0
        let numberOfPeople = parseInt(cells[3].innerText.trim(), 10); // Number of People column

        // If a valid number of people exists, increment registration count
        if (numberOfPeople > 0) {
            registrationCount++;
        }
    }

    // Update the analytics summary on the page
    document.getElementById("totalLogins").textContent = loginCount;
    document.getElementById("totalRegistrations").textContent = registrationCount;

    // Create the pie charts
    createPieChart("cityChart", "Users by Capital City", cityData);
    createPieChart("postcodeChart", "Users by Postcode", postcodeData);
}



function createPieChart(canvasId, title, data) {
    const ctx = document.getElementById(canvasId).getContext("2d");

    // Define pastel colors for the pie chart
    const pastelColors = [
        "#FFB3BA", // Light Pink
        "#FFDFBA", // Light Peach
        "#FFFFBA", // Light Yellow
        "#BAFFC9", // Light Mint Green
        "#BAE1FF", // Light Blue
        "#D0A9F5", // Light Purple
        "#FFABAB", // Pastel Red
        "#A9F1DF", // Pastel Green
        "#F7E4B1", // Pastel Orange
    ];

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(data),
            datasets: [
                {
                    data: Object.values(data),
                    backgroundColor: pastelColors.slice(0, Object.keys(data).length), // Use only required colors
                    borderColor: "#ffffff", // White border for contrast
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
                title: { display: true, text: title },
            },
        },
    });
}


document.getElementById("exportPDF").addEventListener("click", function () {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Title of the PDF
    doc.setFontSize(14);
    doc.text("Registered Users", 14, 15);

    // Get the table data
    const table = document.getElementById("registrationTable");
    const rows = table.getElementsByTagName("tr");

    // Extract table headers
    let headers = [];
    const headerCells = rows[0].getElementsByTagName("th");
    for (let i = 0; i < headerCells.length; i++) {
        headers.push(headerCells[i].innerText.trim());
    }

    // Extract table rows
    let data = [];
    for (let i = 1; i < rows.length; i++) {
        let rowData = [];
        let cells = rows[i].getElementsByTagName("td");
        for (let j = 0; j < cells.length; j++) {
            rowData.push(cells[j].innerText.trim());
        }
        data.push(rowData);
    }

    // Using autoTable to format table
    doc.autoTable({
        head: [headers],
        body: data,
        startY: 25,
        theme: "grid",
        styles: { fontSize: 10, cellPadding: 2 },
        headStyles: { fillColor: [0, 0, 0], textColor: [255, 255, 255] },
        columnStyles: { 0: { cellWidth: 'auto' } }, // Adjusting first column width dynamically
    });

    // Save the PDF
    doc.save("registered_users.pdf");
});


function fetchEventRegistrations() {
    fetch('/fetch-event-registrations')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector("#eventRegistrationTable tbody");
        tableBody.innerHTML = "";
        data.forEach((reg) => {
            let row = `<tr>
                <td>${reg[0]}</td>
                <td>${reg[7]}</td> <!-- Event ID -->
                <td>${reg[8]}</td> <!-- Event Title -->
                <td>${reg[1]}</td> <!-- Name -->
                <td>${reg[2]}</td> <!-- Email -->
                <td>${reg[3]}</td> <!-- Phone -->
                <td>${reg[4]}</td> <!-- Total People -->
                <td>${reg[5]}</td> <!-- Adults -->
                <td>${reg[6]}</td> <!-- Children -->
            </tr>`;
            tableBody.innerHTML += row;
        });
    });
}

// Ensure the function runs when the registrations section is displayed
document.addEventListener("DOMContentLoaded", function () {
    fetchEventRegistrations();
});

function loadEventRegistrations() {
    console.log("Fetching event registrations...");

    fetch('/get-event-registrations')
    .then(response => response.json())
    .then(data => {
        console.log("Received data:", data);  // Log data to check if it's received

        let tableBody = document.querySelector("#eventRegistrationTable tbody");
        tableBody.innerHTML = ""; // Clear previous data

        data.forEach((registration) => {
            let row = `
                <tr>
                    <td>${registration.registration_id}</td>
                    <td>${registration.event_id}</td>
                    <td>${registration.event_title}</td>
                    <td>${registration.name}</td>
                    <td>${registration.email}</td>
                    <td>${registration.phone}</td>
                    <td>${registration.num_people}</td>
                    <td>${registration.adults}</td>
                    <td>${registration.children || "0"}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    })
    .catch(error => console.error("Error loading registrations:", error));
}

document.addEventListener("DOMContentLoaded", loadEventRegistrations);


document.addEventListener("DOMContentLoaded", function () {
    fetch('/admin/data')
    .then(response => response.json())
    .then(data => {
        console.log("Fetched data:", data);  // Debugging
        let tableBody = document.getElementById("adminTableBody");
        tableBody.innerHTML = "";  // Clear existing data

        data.forEach(event => {
            let tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${event[0]}</td>
                <td>${event[1]}</td>
                <td>${event[2]}</td>
                <td><img src="${event[3]}" alt="Event Image" width="100"></td>
                <td>${event[4]}</td>
                <td>${event[5]}</td>
            `;
            tableBody.appendChild(tr);
        });
    })
    .catch(error => console.error("Error fetching admin data:", error));
})