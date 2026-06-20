import streamlit as st
import requests

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Identity Card Generator",
    page_icon="🪪",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 35%,
        #2563eb 100%
    );
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Title */
.main-title{
    text-align:center;
    font-size:52px;
    font-weight:800;
    color:white;
    margin-top:10px;
}

.sub-title{
    text-align:center;
    color:#dbeafe;
    font-size:18px;
    margin-bottom:40px;
}

/* Glass Card */
.glass-card{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius:20px;
    padding:30px;
    border:1px solid rgba(255,255,255,0.2);
    box-shadow:0 8px 32px rgba(0,0,0,0.2);
}

/* Input Labels */
label{
    color:white !important;
    font-weight:600 !important;
}

/* Inputs */
.stTextInput input{
    border-radius:12px !important;
    border:2px solid #60a5fa !important;
    padding:10px !important;
}

/* File uploader */
[data-testid="stFileUploader"]{
    background:white;
    border-radius:15px;
    padding:10px;
}

/* Button */
.stButton > button{
    width:100%;
    height:60px;
    border:none;
    border-radius:15px;
    background: linear-gradient(
        90deg,
        #06b6d4,
        #3b82f6
    );
    color:white;
    font-size:20px;
    font-weight:bold;
}

.stButton > button:hover{
    transform:translateY(-2px);
    transition:0.3s;
}

/* Success box */
.success-box{
    background:#22c55e;
    color:white;
    padding:15px;
    border-radius:12px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
    margin-top:20px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="main-title">
🪪 Identity Card Generator
</div>

<div class="sub-title">
Create Professional Employee Identity Cards with QR Verification
</div>
""", unsafe_allow_html=True)

# ==========================================
# FORM SECTION
# ==========================================

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:

    company = st.text_input(
        "🏢 Company Name",
        placeholder="Enter Company Name"
    )

    name = st.text_input(
        "👤 Employee Name",
        placeholder="Enter Employee Name"
    )

    age = st.text_input(
        "🎂 Age",
        placeholder="Enter Age"
    )

    city = st.text_input(
        "📍 City",
        placeholder="Enter City"
    )

    employee_id = st.text_input(
        "🆔 Employee ID",
        placeholder="EMP1001"
    )

    designation = st.text_input(
        "💼 Designation",
        placeholder="Lead Engineer"
    )

with col2:

    st.markdown("### 📸 Upload Employee Photo")

    photo = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"]
    )

    if photo:
        st.image(
            photo,
            width=250,
            caption="Photo Preview"
        )

st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ==========================================
# GENERATE BUTTON
# ==========================================

generate = st.button("🚀 Generate Identity Card")

# ==========================================
# FASTAPI URL
# ==========================================

FASTAPI_URL = "https://identity-card-backend.onrender.com/generate-id"

# ==========================================
# GENERATE CARD
# ==========================================

if generate:

    if not company:
        st.error("Company Name is required")
        st.stop()

    if not name:
        st.error("Employee Name is required")
        st.stop()

    if not employee_id:
        st.error("Employee ID is required")
        st.stop()

    if photo is None:
        st.error("Please upload employee photo")
        st.stop()

    with st.spinner("Generating Identity Card..."):

        files = {
            "photo": (
                photo.name,
                photo.getvalue(),
                photo.type
            )
        }

        data = {
            "company": company,
            "name": name,
            "age": age,
            "city": city,
            "employee_id": employee_id,
            "designation": designation
        }

        try:

            response = requests.post(
                FASTAPI_URL,
                data=data,
                files=files,
                timeout=60
            )

            if response.status_code == 200:

                st.markdown("""
                <div class="success-box">
                ✅ Identity Card Generated Successfully
                </div>
                """, unsafe_allow_html=True)

                st.write("")

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.image(
                        response.content,
                        caption="Generated Identity Card",
                        use_container_width=True
                    )

                with col2:

                    st.download_button(
                        label="⬇ Download Card",
                        data=response.content,
                        file_name=f"{employee_id}.png",
                        mime="image/png"
                    )

            else:
                st.error(
                    f"FastAPI Error: {response.status_code}"
                )

        except Exception as e:
            st.error(str(e))

# ==========================================
# FOOTER
# ==========================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown(
"""
<center style='color:white'>
Built with ❤️ using Streamlit + FastAPI
</center>
""",
unsafe_allow_html=True
)
