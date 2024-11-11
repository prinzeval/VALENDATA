function loadWebsite() {
    const url = document.getElementById("urlInput").value;
    if (!url) {
        alert("Please enter a URL.");
        return;
    }

    // Make a request to your backend (FastAPI) to fetch the webpage
    fetch(`/load-website?url=${encodeURIComponent(url)}`)
        .then(response => response.json())
        .then(data => {
            // Assuming data contains HTML content to display in the div
            document.getElementById("webpageDisplay").innerHTML = data.htmlContent;
        })
        .catch(error => console.error("Error loading website:", error));
}

function scrapeData() {
    const elements = document.querySelectorAll('.selected');
    const data = [];
    
    elements.forEach(element => {
        data.push({
            name: element.getAttribute('data-name'),
            content: element.innerText
        });
    });

    // Send scraped data to the backend to store or process
    fetch('/scrape-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data })
    })
    .then(response => response.json())
    .then(result => {
        alert("Data scraped and saved!");
    })
    .catch(error => console.error("Error scraping data:", error));
}
