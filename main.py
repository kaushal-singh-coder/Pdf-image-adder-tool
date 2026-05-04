from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image
import io
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "assets", "cover.png")

def build_image_pdf(page_width, page_height):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    img = Image.open(IMAGE_PATH)
    img_reader = ImageReader(img)
    c.drawImage(img_reader, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True, mask='auto')
    c.showPage()
    c.save()
    packet.seek(0)
    return PdfReader(packet)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    input_pdf_bytes = await file.read()
    reader = PdfReader(io.BytesIO(input_pdf_bytes))
    writer = PdfWriter()

    first_page = reader.pages[0]
    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)

    img_pdf = build_image_pdf(page_width, page_height)
    img_page = img_pdf.pages[0]

    writer.add_page(img_page)

    for page in reader.pages:
        writer.add_page(page)

    writer.add_page(img_page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="processed.pdf"'}
    )
