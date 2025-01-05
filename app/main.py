from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Pydantic model for scraping request
class ScrapeRequest(BaseModel):
    url: str
    tag: str
    class_: str
    id: str

@app.get("/", response_class=HTMLResponse)
async def get_form():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web Scraper</title>
        <style>
            body { font-family: Arial, sans-serif; }
            #output { margin-top: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 4px; }
            th { background-color: #f2f2f2; font-size: 12px; }
            td { font-size: 12px; }
            .highlight { outline: 2px solid yellow; }
            #splitContainer {
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }
            iframe {
                width: 48%;
                height: 500px;
            }
            #selectedData {
                width: 48%;
                padding: 10px;
                overflow-y: auto;
                height: 500px;
                border: 1px solid #ddd;
            }
            #tableContainer {
                margin-top: 20px;
                overflow-x: auto;
                max-width: 100%;
            }
            #hoverInfo {
                position: fixed;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                color: #333;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                display: none;
                z-index: 1000;
            }
            .button-container {
                margin-top: 20px;
            }
            .result {
                display: flex;
                align-items: center;
            }
            .result span {
                margin-left: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            .green-tick {
                color: green;
            }
            .red-cross {
                color: red;
            }
        </style>
    </head>
    <body>
        <h1>Simple Web Scraper</h1>
        <input type="text" id="url" placeholder="Enter URL" style="width: 300px;">
        <div class="button-container">
            <button onclick="loadPage()">Load Page</button>
            <button onclick="displayTable()">Display Table</button>
        </div>
        
        <div id="splitContainer">
            <iframe id="pageFrame"></iframe>
            <div id="selectedData">Selected Elements will appear here.</div>
        </div>

        <div id="tableContainer">
            <table>
                <thead>
                    <tr>
                        <th>Tag</th>
                        <th>Class</th>
                        <th>ID</th>
                        <th>Text</th>
                        <th>HTML</th>
                        <th>Test</th>
                    </tr>
                </thead>
                <tbody id="selectedElementsTable">
                    <!-- Selected elements will be appended here -->
                </tbody>
            </table>
        </div>

        <div id="output"></div>

        <script>
            let selectedElements = [];  // Store selected elements for scraping

            // Load webpage into iframe
            function loadPage() {
                const url = document.getElementById('url').value;
                if (!url) {
                    alert('Please enter a URL!');
                    return;
                }

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
                        iframeDoc.write(html);  // Inject HTML into the iframe
                        iframeDoc.close();
                    })
                    .catch(error => {
                        alert(error.message);
                        console.error("Error:", error);
                    });
            }

            // Enable selection of elements in the iframe
            function enableSelection() {
                const iframe = document.getElementById('pageFrame');
                const iframeDoc = iframe.contentWindow.document;

                iframeDoc.addEventListener('click', function(event) {
                    event.preventDefault();
                    const element = event.target;

                    // Toggle highlight class for selected element without affecting the actual class attribute
                    if (element.dataset.highlighted === "true") {
                        element.style.outline = "";
                        element.dataset.highlighted = "false";
                        selectedElements = selectedElements.filter(e => e !== element);
                    } else {
                        element.style.outline = "2px solid yellow";
                        element.dataset.highlighted = "true";
                        selectedElements.push(element);
                    }

                    displaySelectedElements();
                });
            }

            // Display selected elements in the right panel
            function displaySelectedElements() {
                const selectedDataDiv = document.getElementById('selectedData');
                selectedDataDiv.innerHTML = '';  // Clear previous selections

                selectedElements.forEach((element, index) => {
                    const elementDetails = `
                        <div style="margin-bottom: 15px;">
                            <strong>Selected Element ${index + 1}:</strong>
                            <p><strong>Tag:</strong> ${element.tagName}</p>
                            <p><strong>Text:</strong> ${element.innerText.trim()}</p>
                            <p><strong>Class:</strong> ${element.className}</p>
                            <p><strong>ID:</strong> ${element.id}</p>
                            <p><strong>HTML:</strong></p>
                            <pre>${element.outerHTML}</pre>
                        </div>
                    `;
                    selectedDataDiv.innerHTML += elementDetails;
                });
            }

            // Display selected elements with details in a table
            function displayTable() {
                const tableBody = document.getElementById('selectedElementsTable');
                tableBody.innerHTML = '';  // Clear previous selections

                selectedElements.forEach((element, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${element.tagName}</td>
                        <td>${element.className}</td>
                        <td>${element.id}</td>
                        <td>${element.innerText.trim()}</td>
                        <td><pre>${element.outerHTML}</pre></td>
                        <td><button onclick="testElement(${index})">Test</button><span class="result" id="result-${index}"></span></td>
                    `;
                    tableBody.appendChild(row);
                });
            }

            // Test if the element text matches the scraped text
            async function testElement(index) {
                const url = document.getElementById('url').value;
                const element = selectedElements[index];
                const tag = element.tagName.toLowerCase();
                const className = element.className;
                const id = element.id;
                const text = element.innerText.trim();

                const response = await fetch("/test", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        url: url,
                        tag: tag,
                        class_: className,
                        id: id
                    })
                });

                const result = await response.text();
                const resultSpan = document.getElementById(`result-${index}`);

                if (result.includes(text)) {
                    resultSpan.innerHTML = `<span class="green-tick">✔</span>`;
                } else {
                    resultSpan.innerHTML = `<span class="red-cross">✘</span>`;
                }
            }

            // Enable hover effect to display element details
            function enableHover() {
                const iframe = document.getElementById('pageFrame');
                const iframeDoc = iframe.contentWindow.document;

                const hoverInfoDiv = document.getElementById('hoverInfo');

                iframeDoc.addEventListener('mousemove', function(event) {
                    const element = event.target;

                    if (element !== iframeDoc.documentElement && element !== iframeDoc.body) {
                        const tagName = element.tagName;
                        const className = element.className || 'No class';
                        const id = element.id || 'No ID';

                        hoverInfoDiv.innerHTML = `
                            <strong>Tag:</strong> ${tagName}<br>
                            <strong>Class:</strong> ${className}<br>
                            <strong>ID:</strong> ${id}
                        `;
                        hoverInfoDiv.style.left = `${event.pageX + 15}px`;
                        hoverInfoDiv.style.top = `${event.pageY + 15}px`;
                        hoverInfoDiv.style.display = 'block';
                    }
                });

                iframeDoc.addEventListener('mouseleave', function() {
                                        hoverInfoDiv.style.display = 'none';
                });

                iframeDoc.addEventListener('mouseout', function(event) {
                    if (event.target.tagName) {
                        hoverInfoDiv.style.display = 'none';
                    }
                });
            }

            // Enable selection and hover functionality when the iframe content loads
            document.getElementById('pageFrame').addEventListener('load', function () {
                enableSelection();
                enableHover();
            });
        </script>
        <div id="hoverInfo"></div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/proxy", response_class=PlainTextResponse)
async def proxy(url: str = Query(..., description="The URL to fetch")):
    """
    Proxy endpoint to fetch the HTML content of a webpage.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error if status is not 200
        return PlainTextResponse(content=response.text, status_code=200)
    except requests.exceptions.RequestException as e:
        return PlainTextResponse(content=f"Error fetching {url}: {e}", status_code=500)

@app.post("/test", response_class=PlainTextResponse)
async def test_scrape(scrape_request: ScrapeRequest):
    """
    Test scraping endpoint to check if the scraped text matches the table text.
    """
    try:
        response = requests.get(scrape_request.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        elements = soup.find_all(scrape_request.tag, class_=scrape_request.class_, id=scrape_request.id)
        texts = [element.get_text(strip=True) for element in elements]
        return PlainTextResponse(content=' '.join(texts), status_code=200)
    except Exception as e:
        return PlainTextResponse(content=f"Error: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

