from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files like CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup for HTML templates
templates = Jinja2Templates(directory="templates")

# Serve the index.html template
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to load website content
@app.get("/load-website")
async def load_website(url: str):
    try:
        # Fetch the website content
        response = requests.get(url)
        html_content = response.text

        # You can parse the HTML with BeautifulSoup or similar tools if needed
        soup = BeautifulSoup(html_content, 'html.parser')

        # You can process the HTML here if necessary
        return {"htmlContent": str(soup)}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to handle scraped data
@app.post("/scrape-data")
async def scrape_data(data: dict):
    try:
        # Process the scraped data (e.g., save to database or send to another service)
        # For now, we'll just print it
        print(data)
        return {"message": "Data successfully received!"}
    except Exception as e:
        return {"error": str(e)}
