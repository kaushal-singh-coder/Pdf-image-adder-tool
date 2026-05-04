from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io

app = FastAPI()

# HTML yahan string ke form mein hai, alag file ki zaroorat nahi
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head><title>PDF Image Adder</title></head>
<body>
  <h2>Upload PDF</h2>
  <form action="/process" method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept="application/pdf" required />
    <button type="submit">Process PDF</button>
  </form>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/process")
async def process(file: UploadFile = File(...)):
    # ... baki ka wahi logic jo pehle tha ...
    reader = PdfReader(io.BytesIO(await file.read()))
    writer = PdfWriter()
    
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
    return StreamingResponse(out, media_type="application/pdf")
