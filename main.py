from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from PIL import Image
import io

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse('''
        <form action="/process" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf" required />
            <button type="submit">Process</button>
        </form>
    ''')

@app.post("/process")
async def process(file: UploadFile = File(...)):
    reader = PdfReader(io.BytesIO(await file.read()))
    writer = PdfWriter()
    
    # Image logic (cover.png must be in root)
    def add_img_page(w, h):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(w, h))
        c.drawImage("cover.png", 0, 0, width=w, height=h)
        c.showPage()
        c.save()
        packet.seek(0)
        return PdfReader(packet).pages[0]

    w = float(reader.pages[0].mediabox.width)
    h = float(reader.pages[0].mediabox.height)
    img_page = add_img_page(w, h)
    
    writer.add_page(img_page)
    for p in reader.pages: writer.add_page(p)
    writer.add_page(img_page)
    
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return StreamingResponse(out, media_type="application/pdf")    writer = PdfWriter()

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
