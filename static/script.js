let selecting = false;
let selectedData = [];
let columnHeaders = ['Column 1']; // Default column names

function loadPage() {
    const url = document.getElementById('url').value;
    fetch(`/proxy?url=${encodeURIComponent(url)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load the page.');
            }
            return response.text();
        })
        .then(html => {
            const iframe = document.getElementById('pageFrame');
            const iframeDoc = iframe.contentWindow.document;
            iframeDoc.open();
            iframeDoc.write(html);  // Inject the HTML content
            iframeDoc.close();
            console.log("Page loaded successfully in iframe");
        })
        .catch(error => {
            alert(error.message);
            console.error("Error:", error);
        });
}


function toggleSelection() {
    selecting = !selecting;
    const button = document.getElementById('toggleSelection');
    button.textContent = selecting ? 'Stop Selection' : 'Start Selection';
}

function enableSelection() {
    const iframe = document.getElementById('pageFrame');
    const doc = iframe.contentWindow.document;

    doc.addEventListener('click', function (event) {
        if (!selecting) return;
        event.preventDefault();

        const element = event.target;
        element.classList.toggle('highlight');

        if (element.classList.contains('highlight')) {
            const tagName = element.tagName.toLowerCase();
            const className = element.className;
            const id = element.id;

            // Fetch element data
            fetch('/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tagName, className, id, url: iframe.src })
            })
                .then(response => response.json())
                .then(data => {
                    selectedData = data;
                    displayData(data);
                });
        }
    });
}

function displayData(data) {
    if (!data.length) {
        document.getElementById('output').innerHTML = 'No data found!';
        return;
    }

    // Create table with editable headers
    let table = '<table><thead><tr>';
    columnHeaders = Object.keys(data[0]);
    columnHeaders.forEach((header, index) => {
        table += `<th contenteditable="true" onblur="updateColumnName(${index}, this.textContent)">${header}</th>`;
    });
    table += '</tr></thead><tbody>';
    data.forEach(row => {
        table += '<tr>';
        columnHeaders.forEach(header => {
            table += `<td>${row[header] || ''}</td>`;
        });
        table += '</tr>';
    });
    table += '</tbody></table>';
    document.getElementById('output').innerHTML = table;
    document.getElementById('finalControls').style.display = 'block';
}

function updateColumnName(index, newName) {
    columnHeaders[index] = newName;
}

function finalizeScraping() {
    const finalTable = selectedData.map(row => {
        const updatedRow = {};
        columnHeaders.forEach((header, index) => {
            updatedRow[columnHeaders[index]] = row[Object.keys(row)[index]];
        });
        return updatedRow;
    });

    const blob = new Blob([JSON.stringify(finalTable, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'scraped_data.json';
    link.click();
}

document.getElementById('pageFrame').addEventListener('load', enableSelection);
