from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
import os
import uuid
import traceback

app = FastAPI(title="Identity Card API")

# ==========================================
# CONFIG
# ==========================================

PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def home():
    return {
        "status": "running",
        "service": "Identity Card API"
    }


# ==========================================
# CREATE ID CARD
# ==========================================

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
    WHITE = (255, 255, 255)

    # Header
    draw.rectangle(
        [(0, 0), (CARD_WIDTH, 100)],
        fill=HEADER_COLOR
    )

    # Fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 40)
        text_font = ImageFont.truetype("arial.ttf", 28)
        small_font = ImageFont.truetype("arial.ttf", 22)

    except Exception:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Company Name
    draw.text(
        (30, 25),
        data["company"],
        fill=WHITE,
        font=title_font
    )

    draw.text(
        (30, 70),
        "IDENTITY CARD",
        fill=WHITE,
        font=small_font
    )

    # ======================================
    # PHOTO
    # ======================================

    photo = Image.open(photo_path).convert("RGB")
    photo = photo.resize((180, 220))

    card.paste(photo, (40, 160))

    # ======================================
    # DETAILS
    # ======================================

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
            (start_x, start_y + (i * 55)),
            text,
            fill="black",
            font=text_font
        )

    # ======================================
    # QR CODE
    # ======================================

    qr_data = f"""
Name: {data['name']}
Age: {data['age']}
City: {data['city']}
Employee ID: {data['employee_id']}
Designation: {data['designation']}
Company: {data['company']}
"""

    qr = qrcode.make(qr_data).convert("RGB")
    qr = qr.resize((180, 180))

    card.paste(qr, (670, 300))

    # ======================================
    # BORDER
    # ======================================

    draw.rectangle(
        [(0, 0), (CARD_WIDTH - 1, CARD_HEIGHT - 1)],
        outline=(0, 0, 0),
        width=4
    )

    # ======================================
    # RETURN IMAGE BUFFER
    # ======================================

    buffer = BytesIO()

    card.save(buffer, format="PNG")

    buffer.seek(0)

    return buffer


# ==========================================
# GENERATE ID API
# ==========================================

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

    try:

        # Save uploaded photo
        photo_path = os.path.join(
            PHOTO_DIR,
            f"{uuid.uuid4()}_{photo.filename}"
        )

        with open(photo_path, "wb") as f:
            f.write(await photo.read())

        # Generate card
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

        # Cleanup uploaded photo
        try:
            os.remove(photo_path)
        except Exception:
            pass

        return StreamingResponse(
            card_buffer,
            media_type="image/png",
            headers={
                "Content-Disposition":
                f"attachment; filename={employee_id}.png"
            }
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
