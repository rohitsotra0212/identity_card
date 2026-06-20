from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
import uuid

app = FastAPI(title="Identity Card API")

CARD_DIR = "cards"
PHOTO_DIR = "photos"

os.makedirs(CARD_DIR, exist_ok=True)
os.makedirs(PHOTO_DIR, exist_ok=True)


def create_id_card(data, photo_path):

    CARD_WIDTH = 900
    CARD_HEIGHT = 550

    card = Image.new(
        "RGB",
        (CARD_WIDTH, CARD_HEIGHT),
        (240, 248, 255)
    )

    draw = ImageDraw.Draw(card)

    HEADER_COLOR = (25, 25, 112)

    draw.rectangle(
        [(0, 0), (CARD_WIDTH, 100)],
        fill=HEADER_COLOR
    )

    try:
        title_font = ImageFont.truetype("arial.ttf", 40)
        text_font = ImageFont.truetype("arial.ttf", 28)
        small_font = ImageFont.truetype("arial.ttf", 22)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text(
        (30, 25),
        data["company"],
        fill="white",
        font=title_font
    )

    draw.text(
        (30, 70),
        "IDENTITY CARD",
        fill="white",
        font=small_font
    )

    photo = Image.open(photo_path)
    photo = photo.resize((180, 220))

    card.paste(photo, (40, 160))

    start_x = 270
    start_y = 160

    details = [
        f"Name : {data['name']}",
        f"Age : {data['age']}",
        f"City : {data['city']}",
        f"Employee ID : {data['employee_id']}",
        f"Designation : {data['designation']}"
    ]

    for i, text in enumerate(details):
        draw.text(
            (start_x, start_y + i * 55),
            text,
            fill="black",
            font=text_font
        )

    qr_data = f"""
Name:{data['name']}
Age:{data['age']}
City:{data['city']}
Employee ID:{data['employee_id']}
Designation:{data['designation']}
"""

    qr = qrcode.make(qr_data)
    qr = qr.resize((180, 180))

    card.paste(qr, (670, 300))

    buffer = BytesIO()
    
    card.save(buffer, format="PNG")
    
    buffer.seek(0)
    
    return buffer


@app.post("/generate-id")
async def generate_id(
        name: str = Form(...),
        age: str = Form(...),
        city: str = Form(...),
        employee_id: str = Form(...),
        designation: str = Form(...),
        company: str = Form(...),
        photo: UploadFile = File(...)
):

    photo_path = os.path.join(
        PHOTO_DIR,
        f"{uuid.uuid4()}_{photo.filename}"
    )

    with open(photo_path, "wb") as f:
        f.write(await photo.read())

    card_buffer = create_id_card(
        {
            "name": name,
            "age": age,
            "city": city,
            "employee_id": employee_id,
            "designation": designation,
            "company": company
        },
        photo_path
    )
    
    return StreamingResponse(
        card_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition":
            f"attachment; filename={employee_id}.png"
        }
    )
