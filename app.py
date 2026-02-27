import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import requests
import base64
import os

# ======================================================
# API KEY IMGBB!
IMGBB_API_KEY = st.secrets["IMGBB_API_KEY"]
# ======================================================

# --- JURUS PAMUNGKAS: AUTO-DOWNLOAD FONT ---
def ambil_font(url, nama_file, ukuran):
    if not os.path.exists(nama_file):
        try:
            r = requests.get(url, allow_redirects=True)
            with open(nama_file, 'wb') as f:
                f.write(r.content)
        except:
            pass
    try:
        return ImageFont.truetype(nama_file, ukuran)
    except:
        return ImageFont.load_default()

# Link langsung ke font server Google
url_reguler = "https://raw.githubusercontent.com/google/fonts/main/apache/roboto/static/Roboto-Regular.ttf"
url_tebal = "https://raw.githubusercontent.com/google/fonts/main/apache/roboto/static/Roboto-Bold.ttf"
# ======================================================

st.title("🏆 Golden Gate Auto-QR & Invoice")
st.write("Resolusi Template: 1414 x 2000 px")

with st.form("invoice_form"):
    st.subheader("Data Pelanggan")
    tanggal = st.date_input("Tanggal Transaksi")
    nama_klien = st.text_input("Nama Klien", value="") 
    email = st.text_input("Email Klien", value="")
    
    st.subheader("Detail Pembelian")
    type_emas = st.selectbox("Type Emas", ["Emas Digital", "Emas Fisik"])
    produk = st.selectbox("Detail Produk", ["Goldengate Promo", "Goldengate Share Profit", "Goldengate Premium", "Goldengate Signature"])
    berat_gram = st.text_input("Gram", value="")
    periode_invest = st.radio("Periode Invest", ["30 Hari", "100 Hari"])
    
    st.subheader("Detail Pembayaran")
    harga_rupiah = st.text_input("Harga (Rupiah)", value="")
    harga_usd = st.text_input("Harga (USD)", value="")
    total_amount = st.text_input("Total Amount", placeholder="tambahkan Rp./Usd")
    
    submitted = st.form_submit_button("Generate QR Code Sekarang!")

if submitted:
    if not nama_klien:
        st.error("Nama Klien wajib diisi bro!")
    else:
        with st.spinner('Lagi ngeracik invoice...'):
            try:
                # 1. BUKA TEMPLATE
                template_img = Image.open("template.png")
                draw = ImageDraw.Draw(template_img)
                
                # 2. SETUP FONT PAKE JURUS PAMUNGKAS (Pasti Gede!)
                font_normal = ambil_font(url_reguler, "Roboto-Reguler.ttf", 50)
                font_tebal = ambil_font(url_tebal, "Roboto-Tebal.ttf", 60)
                font_besar = ambil_font(url_tebal, "Roboto-Tebal.ttf", 90)

                no_tagihan = f"GG-{random.randint(1000, 9999)}"
                tanggal_str = tanggal.strftime("%d/ %m/ %Y")
                
                # --- PROSES NGE-CAP DATA ---
                
                # A. TANGGAL
                draw.text((980, 440), tanggal_str, fill="white", font=font_normal)
                
                # B. DATA KLIEN
                draw.text((150, 680), nama_klien, fill="black", font=font_tebal)
                draw.text((150, 740), email, fill="black", font=font_normal)
                
                # C. TABEL
                y_tabel = 1050
                item_desc = f"{type_emas} - {produk}\n(Periode: {periode_invest})"
                
                draw.text((150, y_tabel), item_desc, fill="black", font=font_normal) # Kolom Barang
                draw.text((680, y_tabel), berat_gram, fill="black", font=font_normal) # Kolom Jumlah
                draw.text((880, y_tabel), harga_rupiah, fill="black", font=font_normal)  # Kolom Harga usd
                draw.text((1150, y_tabel), harga_usd, fill="black", font=font_normal) # Kolom Harga rp
                
                # D. TOTAL AMOUNT
                draw.text((1050, 1640), total_amount, fill="white", font=font_besar)

                # --- UPLOAD KE IMGBB ---
                buf_invoice = BytesIO()
                template_img.save(buf_invoice, format="PNG")
                img_bytes = buf_invoice.getvalue()
                
                url_upload = "https://api.imgbb.com/1/upload"
                payload = {
                    "key": IMGBB_API_KEY,
                    "image": base64.b64encode(img_bytes).decode('utf-8')
                }
                res = requests.post(url_upload, data=payload)
                
                if res.status_code == 200:
                    link_online = res.json()["data"]["url"]
                    
                    # --- BIKIN QR CODE ---
                    qr = qrcode.QRCode(box_size=10, border=4)
                    qr.add_data(link_online)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                    
                    st.success("✅ QR Code Siap! Scan buat liat Invoice.")
                    st.image(qr_img, width=300)
                    
                    buf_qr = BytesIO()
                    qr_img.save(buf_qr, format="PNG")
                    st.download_button("📥 Download QR Code", data=buf_qr.getvalue(), file_name=f"QR_{nama_klien}.png")
                else:
                    st.error("Gagal upload ke ImgBB bro!")

            except Exception as e:
                st.error(f"Error: {e}")
