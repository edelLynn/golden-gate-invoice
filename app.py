import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import requests
import base64

# ======================================================
# API KEY IMGBB!
IMGBB_API_KEY = "a9b93f8b62ea968b7b7cf6c3bdd54a24" 
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
    if IMGBB_API_KEY == "":
        st.error("Bro, API Key ImgBB-nya diisi dulu di baris ke-11!")
    else:
        with st.spinner('Lagi ngeracik invoice...'):
            try:
                # 1. BUKA TEMPLATE & SETUP FONT
                template_img = Image.open("template.png")
                draw = ImageDraw.Draw(template_img)
                
                try:
                    font_normal = ImageFont.truetype("arial.ttf", 45)  
                    font_tebal = ImageFont.truetype("arialbd.ttf", 50) 
                    font_besar = ImageFont.truetype("arialbd.ttf", 65) 
                except:
                    font_normal = font_tebal = font_besar = ImageFont.load_default()

                no_tagihan = f"GG-{random.randint(1000, 9999)}"
                tanggal_str = tanggal.strftime("%d/ %m/ %Y")
                
                # --- KOORDINAT FIX ---
                
                # 1. Setting Font
                try:
                    font_normal = ImageFont.truetype("arial.ttf", 30)  
                    font_tebal = ImageFont.truetype("arialbd.ttf", 32) 
                    font_besar = ImageFont.truetype("arialbd.ttf", 45) 
                except:
                    font_normal = font_tebal = font_besar = ImageFont.load_default()

                tanggal_str = tanggal.strftime("%d/ %m/ %Y")
                
                # --- PROSES NGE-CAP TEKS ---
                
                # --- SETTING FONT SKALA RESOLUSI ---
                try:
                    font_normal = ImageFont.truetype("arial.ttf", 30)  
                    font_tebal = ImageFont.truetype("arialbd.ttf", 32) 
                    font_besar = ImageFont.truetype("arialbd.ttf", 45) 
                except:
                    font_normal = font_tebal = font_besar = ImageFont.load_default()

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

                # --- UPLOAD KE IMGBB DULU BIAR DAPET LINK ---
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
                    
                    # --- BARU BIKIN QR CODE-NYA ---
                    qr = qrcode.QRCode(box_size=10, border=4)
                    qr.add_data(link_online)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                    
                    # Tampilkan Preview Invoice di Web
                    #st.subheader("👀 Preview Invoice Lu")
                    #st.image(template_img, caption="Ini yang bakal muncul pas klien scan QR.")
                    
                    # Tampilkan QR Code Utama buat Kasir
                    st.success("✅ QR Code Siap! Scan buat liat Invoice.")
                    st.image(qr_img, width=300)
                    
                    buf_qr = BytesIO()
                    qr_img.save(buf_qr, format="PNG")
                    st.download_button("📥 Download QR Code", data=buf_qr.getvalue(), file_name=f"QR_{nama_klien}.png")
                else:
                    st.error("Gagal upload ke ImgBB bro!")

            except FileNotFoundError:
                st.error("File 'template.png' ilang dari folder!")