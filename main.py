# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import Request
# import requests
# from bs4 import BeautifulSoup

# app = FastAPI()

# # Allow CORS for the frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust this to allow specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Serve static files like CSS and JavaScript
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Setup for HTML templates
# templates = Jinja2Templates(directory="templates")

# # Serve the index.html template
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# # Endpoint to load website content
# @app.get("/load-website")
# async def load_website(url: str):
#     try:
#         # Fetch the website content
#         response = requests.get(url)
#         html_content = response.text

#         # You can parse the HTML with BeautifulSoup or similar tools if needed
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # You can process the HTML here if necessary
#         return {"htmlContent": str(soup)}
#     except Exception as e:
#         return {"error": str(e)}

# # Endpoint to handle scraped data
# @app.post("/scrape-data")
# async def scrape_data(data: dict):
#     try:
#         # Process the scraped data (e.g., save to database or send to another service)
#         # For now, we'll just print it
#         print(data)
#         return {"message": "Data successfully received!"}
#     except Exception as e:
#         return {"error": str(e)}






























from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Pydantic model for scraping request
class ScrapeRequest(BaseModel):
    url: str
    selector: str

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
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; }
            .highlight { background-color: yellow; }
            #splitContainer {
                display: flex;
                justify-content: space-between;
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
            #output {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Simple Web Scraper</h1>
        <input type="text" id="url" placeholder="Enter URL" style="width: 300px;">
        <button onclick="loadPage()">Load Page</button>
        <button onclick="scrapeSelected()">Scrape Selected</button>

        <div id="splitContainer">
            <iframe id="pageFrame"></iframe>
            <div id="selectedData">Selected Elements will appear here.</div>
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

            // Toggle highlight class for selected element
            element.classList.toggle('highlight');
            if (element.classList.contains('highlight')) {
                selectedElements.push(element);
                displaySelectedElements();
            } else {
                selectedElements = selectedElements.filter(e => e !== element);
                displaySelectedElements();
            }
        });
    }

    // Display selected elements with details like id, class, and div structure
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

    // Enable selection when the iframe content loads
    document.getElementById('pageFrame').addEventListener('load', enableSelection);
</script>

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

@app.post("/scrape", response_class=JSONResponse)
async def scrape(request: ScrapeRequest):
    """
    Scrape data from the selected element based on tagName, className, and id.
    """
    response = requests.get(request.url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Create a selector based on tag, class, and id
    if request.className:
        selector = f"{request.tagName}.{request.className.replace(' ', '.')}"
    elif request.id:
        selector = f"{request.tagName}#{request.id}"
    else:
        selector = request.tagName

    # Debug: Print the selector being used
    print(f"Using selector: {selector}")

    # Scrape the elements based on the constructed selector
    elements = soup.select(selector)
    
    # Debug: Print how many elements were found
    print(f"Found {len(elements)} elements matching the selector.")

    scraped_data = []

    # Collect text from selected elements
    for elem in elements:
        scraped_data.append({
            'tagName': elem.name,
            'text': elem.get_text(strip=True),
            'className': elem.get('class'),
            'id': elem.get('id')
        })

    # If no elements were found, provide feedback
    if not scraped_data:
        print(f"No elements found for selector: {selector}")
        return JSONResponse(content={"message": "No matching elements found on the page."}, status_code=404)

    return JSONResponse(content=scraped_data)


    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
