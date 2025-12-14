import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import os
import tempfile      
from fpdf import FPDF
from datetime import datetime, timedelta

GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 

if GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except:
        pass 
else:
    genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="BizMind Pro: Analisa UMKM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Font */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Title Styling */
    h1 {
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
    }
    
    /* Subtitle */
    .subtitle {
        font-size: 1.3rem;
        color: #6b7280;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Section Headers */
    h2, h3 {
        font-weight: 600 !important;
        color: #1f2937 !important;
        margin-top: 2rem !important;
        font-size: 1.8rem !important;
    }
    
    /* Metric Cards Custom */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #6b7280 !important;
    }
    
    /* Business Type Input Box */
    .business-input-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .business-input-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .business-input-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Info Boxes */
    .stAlert {
        font-size: 1.05rem !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1f2937 !important;
        font-size: 1.4rem !important;
    }
    
    /* Upload Area */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background: #f8f9ff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem 2rem !important;
    }
    
    /* Divider */
    hr {
        margin: 2.5rem 0 !important;
        border-color: #e5e7eb !important;
    }
    
    /* Caption */
    .caption-custom {
        font-size: 1.05rem;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Card-like containers */
    .analysis-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* Download button special */
    .download-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.cell(0, 15, 'Laporan Analisis Bisnis UMKM', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, f'Generated: {datetime.now().strftime("%d %B %Y, %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.cell(0, 10, f'BizMind Pro - Halaman {self.page_no()}', 0, 0, 'C')

def create_pdf(business_type, ai_advice_text, summary_stats, figures):
    """Create comprehensive PDF report with better visualizations"""
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(102, 126, 234)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, f'Profil Bisnis: {business_type}', 0, 1, 'L', True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Ringkasan Keuangan:", 0, 1)
    pdf.set_font("Arial", "", 11)
    
    for key, value in summary_stats.items():
        clean_key = key.encode('latin-1', 'replace').decode('latin-1')
        clean_value = str(value).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 8, f"  {clean_key}: {clean_value}", 0, 1)
    
    pdf.ln(8)

    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "Analisis & Rekomendasi AI:", 0, 1, 'L', True)
    pdf.ln(3)
    
    pdf.set_font("Arial", "", 10)
    text_processed = ai_advice_text.replace("**", "")
    
    text_processed = text_processed.replace("* ", "- ") 
    
    clean_text = text_processed.encode('latin-1', 'replace').decode('latin-1')
    
    clean_text = clean_text.replace("?", "")

    pdf.multi_cell(0, 6, clean_text)
    pdf.ln(10)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Visualisasi Data Keuangan", 0, 1, 'C')
    pdf.ln(5)
    
    for i, (fig, title) in enumerate(figures):
        if i > 0 and i % 2 == 0:
            pdf.add_page()
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, title, 0, 1)
        pdf.ln(2)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.write_image(tmpfile.name, width=1000, height=600, scale=2)
            pdf.image(tmpfile.name, x=10, w=190)
            pdf.ln(5)
            tmpfile.close()
            os.unlink(tmpfile.name)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_csv_template():
    """Generate improved CSV template"""
    data = {
        'Tanggal': pd.date_range(start='2024-01-01', periods=14, freq='D').strftime('%Y-%m-%d').tolist(),
        'Pemasukan': [1500000, 2000000, 1800000, 2200000, 1900000, 1700000, 1600000,
                      2100000, 2300000, 2000000, 1850000, 1950000, 2050000, 2200000],
        'Pengeluaran': [500000, 450000, 600000, 550000, 500000, 480000, 520000,
                        600000, 580000, 550000, 530000, 560000, 570000, 590000],
        'Catatan': ['Ramai pagi', 'Promo gajian', 'Biasa', 'Weekend ramai', 
                    'Sepi hujan', 'Normal', 'Bahan naik', 'Laris manis',
                    'Event spesial', 'Steady', 'Pelanggan baru', 'Cuaca bagus',
                    'Promosi sosmed', 'Repeat order']
    }
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

def validate_and_clean_data(df):
    """Enhanced data validation"""
    df.columns = df.columns.str.lower().str.strip()
    
    column_mapping = {
        'date': 'Date', 'tanggal': 'Date', 'tgl': 'Date',
        'income': 'Income', 'pemasukan': 'Income', 'pendapatan': 'Income', 
        'masuk': 'Income', 'omset': 'Income', 'omzet': 'Income',
        'expense': 'Expense', 'pengeluaran': 'Expense', 'keluar': 'Expense', 
        'outcome': 'Expense', 'biaya': 'Expense',
        'notes': 'Notes', 'catatan': 'Notes', 'keterangan': 'Notes', 'ket': 'Notes'
    }
    
    df = df.rename(columns=column_mapping)
    
    required_cols = ['Date', 'Income', 'Expense']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        return None, f"❌ Kolom wajib tidak ditemukan: {', '.join(missing_cols)}. Pastikan ada kolom Tanggal, Pemasukan, dan Pengeluaran."
    
    if 'Notes' not in df.columns:
        df['Notes'] = '-'
    
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            return None, f"⚠️ Ada {invalid_dates} tanggal yang tidak valid. Pastikan format tanggal benar (YYYY-MM-DD)."
        
        df['Income'] = pd.to_numeric(df['Income'], errors='coerce').fillna(0)
        df['Expense'] = pd.to_numeric(df['Expense'], errors='coerce').fillna(0)
        df['Notes'] = df['Notes'].fillna('-').astype(str)
        
        df = df[(df['Income'] != 0) | (df['Expense'] != 0)]
        
    except Exception as e:
        return None, f"❌ Format data salah: {e}"
        
    return df.sort_values('Date').reset_index(drop=True), None

def get_ai_advice(business_type, df_summary, trend_info):
    """Enhanced AI prompt with more context"""
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Peran: Kamu adalah Konsultan Bisnis UMKM Senior berpengalaman 15+ tahun.
    Gaya: Santai, supportif, actionable, hindari jargon.
    
    Konteks Bisnis: "{business_type}"
    
    Data Keuangan:
    {df_summary}
    
    Tren Performa:
    {trend_info}
    
    Tugas: Berikan analisa tajam dan saran konkret.
    
    Format Jawaban (WAJIB):
    
    📊 **KONDISI BISNIS**
    (2-3 kalimat: Bagaimana performa? Untung stabil atau fluktuatif? Ada pola menarik?)
    
    💡 **SARAN AKSI SEGERA** 
    (Berikan 2-3 aksi spesifik yang bisa dilakukan minggu ini. Contoh: "Tambah stok Senin-Rabu karena trend tinggi", "Kurangi bahan X 20%", "Buat paket bundling weekend")
    
    ⚠️ **PERHATIAN KHUSUS**
    (Warning tentang: pengeluaran mencurigakan, tren menurun, atau apresiasi jika sehat)
    
    🎯 **STRATEGI 30 HARI KE DEPAN**
    (1 strategi jangka pendek untuk boost profit atau efisiensi)
    
    ---
    Contoh Output Bagus:
    📊 **KONDISI BISNIS**: Bisnismu tumbuh positif! Profit naik 23% minggu ini dengan rata-rata 650rb/hari. Ada lonjakan signifikan tiap Jumat-Sabtu.
    
    💡 **SARAN AKSI SEGERA**: 
    1. Maksimalkan weekend: Tambah porsi produksi Jumat pagi karena weekend selalu sold out
    2. Efisiensi Selasa: Hari ini paling sepi, coba buat flash sale jam 2-4 sore
    3. Stok pintar: Pesan bahan untuk 3 hari saja, hindari overstock
    
    ⚠️ **PERHATIAN KHUSUS**: Pengeluaran naik 15% tanpa peningkatan omset proporsional. Cek supplier, mungkin ada harga yang bisa dinegosiasi.
    
    🎯 **STRATEGI 30 HARI**: Bangun loyalty program sederhana (beli 5 gratis 1) untuk mendorong repeat customer di hari sepi.
    
    ---
    Analisa data {business_type} di atas:
    """
    
    try:
        with st.spinner('🤖 AI sedang menganalisa pola bisnis Anda...'):
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"⚠️ AI sedang maintenance. Error: {e}"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📖 Panduan Cepat")
    
    with st.expander("🚀 Cara Menggunakan", expanded=True):
        st.markdown("""
        1. **Isi nama bisnis** di halaman utama
        2. **Siapkan data** keuangan harian (Excel/Spreadsheet)
        3. **Save as CSV** dari aplikasi spreadsheet
        4. **Upload** file CSV
        5. **Dapatkan insights** otomatis + saran AI
        """)
    
    with st.expander("📋 Format Data yang Benar"):
        st.info("""
        **Kolom Wajib:**
        - 📅 Tanggal (YYYY-MM-DD)
        - 💰 Pemasukan (angka)
        - 💸 Pengeluaran (angka)
        - 📝 Catatan (opsional)
        
        **Contoh:**
        ```
        2024-01-15,1500000,500000,Ramai
        ```
        """)
    
    st.divider()
    
    st.download_button(
        label="📥 Download Template CSV",
        data=generate_csv_template(),
        file_name="template_bizmind_pro.csv",
        mime="text/csv",
        help="File contoh lengkap dengan 14 hari data",
        use_container_width=True
    )
    
    st.divider()
    
    st.markdown("### ℹ️ Tentang BizMind Pro")
    st.caption("""
    Aplikasi analisis keuangan UMKM berbasis AI. 
    Membantu pemilik usaha kecil memahami performa 
    bisnis dan mendapat rekomendasi actionable.
    
    v2.0 - Enhanced Edition
    """)

# --- HALAMAN UTAMA ---

st.markdown("<h1>BizMind Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Asisten Analisis Bisnis UMKM Berbasis AI - Ubah data jadi keputusan pintar</p>", unsafe_allow_html=True)

st.markdown("""
<div class='business-input-container'>
    <div class='business-input-title'>🏪 Profil Bisnis Anda</div>
    <div class='business-input-subtitle'>Mulai dengan memberitahu kami jenis usaha yang Anda jalani</div>
</div>
""", unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    business_type = st.text_input(
        "Nama/Jenis Usaha",
        placeholder="Contoh: Warung Kopi Sentosa, Toko Sembako Bahagia, Catering Ibu Ani",
        label_visibility="collapsed",
        key="business_input"
    )
    
    if not business_type:
        st.warning("⚠️ Mohon isi nama bisnis Anda untuk hasil analisis yang lebih personal")

st.divider()

st.markdown("### 📤 Upload Data Keuangan")
col_upload_1, col_upload_2 = st.columns([2, 1])

with col_upload_1:
    uploaded_file = st.file_uploader(
        "Pilih file CSV data transaksi harian Anda",
        type=['csv'],
        help="File harus berformat CSV dengan kolom: Tanggal, Pemasukan, Pengeluaran"
    )

with col_upload_2:
    st.info("""
    **Tips:**
    - Min. 7 hari data
    - Maks. 365 hari
    - Format: CSV UTF-8
    """)

st.markdown("### 🏦 Status Pinjaman (Opsional)")
has_loan = st.checkbox("Apakah ada pinjaman modal/hutang usaha yang aktif?")
input_loan = 0.0

if has_loan:
    col_loan_input, _ = st.columns([1, 2])
    with col_loan_input:
        input_loan = st.number_input(
            "Masukkan Total Sisa Pinjaman",
            min_value=0,
            value=0,
            step=500000,
            help="Masukkan nominal hutang yang harus dilunasi"
        )

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    df, error_msg = validate_and_clean_data(raw_df)
    
    if error_msg:
        st.error(error_msg)
        with st.expander("🔍 Lihat Data yang Diupload"):
            st.dataframe(raw_df.head(10), use_container_width=True)
            st.caption(f"Total baris: {len(raw_df)}")
    else:
        st.success(f"✅ Data berhasil dibaca! Total: {len(df)} hari transaksi")

        df['Profit'] = df['Income'] - df['Expense']
        df['Profit_Margin'] = (df['Profit'] / df['Income'] * 100).round(2)
        df['Day'] = df['Date'].dt.day_name()
        df['Week'] = df['Date'].dt.isocalendar().week
        
        total_income = df['Income'].sum()
        total_expense = df['Expense'].sum()
        net_profit = total_income - total_expense
        avg_profit = df['Profit'].mean()
        profit_margin_avg = (net_profit / total_income * 100) if total_income > 0 else 0
        
        best_day = df.loc[df['Profit'].idxmax()]
        worst_day = df.loc[df['Profit'].idxmin()]
        
        profitable_days = len(df[df['Profit'] > 0])
        loss_days = len(df[df['Profit'] < 0])
        
        # Dashboard
        st.divider()
        st.markdown("## 📈 Dashboard Performa Bisnis")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "💰 Total Pemasukan", 
            f"Rp {total_income:,.0f}",
            delta=f"{len(df)} hari"
        )
        m2.metric(
            "💸 Total Pengeluaran", 
            f"Rp {total_expense:,.0f}",
            delta=f"{(total_expense/total_income*100):.1f}% dari omset"
        )
        m3.metric(
            "✨ Keuntungan Bersih", 
            f"Rp {net_profit:,.0f}",
            delta="Sehat" if net_profit > 0 else "Perlu Perhatian",
            delta_color="normal" if net_profit > 0 else "inverse"
        )
        m4.metric(
            "📊 Margin Profit", 
            f"{profit_margin_avg:.1f}%",
            delta=f"Rp {avg_profit:,.0f}/hari"
        )

        if has_loan and input_loan > 0:
            st.divider()
            st.markdown("### 💳 Simulasi Pelunasan Pinjaman")
    
            if net_profit > 0:
                st.info("💡 Bisnis untung! Tentukan berapa persen profit yang mau dipakai bayar hutang.")
                
                allocation_pct = st.slider(
                    "Geser untuk atur alokasi pembayaran (%)",
                    min_value=0,
                    max_value=100,
                    value=30,  
                    step=5,
                    help="Berapa persen dari Keuntungan Bersih yang akan disetor ke pinjaman"
                )
        
                payment_amount = net_profit * (allocation_pct / 100)
                retained_earnings = net_profit - payment_amount  # Sisa uang buat owner
                remaining_loan = max(0, input_loan - payment_amount)
                
                col_pay1, col_pay2, col_pay3 = st.columns(3)
                
                with col_pay1:
                    st.metric(
                        "💸 Disetor ke Pinjaman",
                        f"Rp {payment_amount:,.0f}",
                        delta=f"{allocation_pct}% dari Profit"
                    )
                    
                with col_pay2:
                    is_lunas = remaining_loan == 0
                    st.metric(
                        "📉 Sisa Pinjaman Akhir",
                        f"Rp {remaining_loan:,.0f}",
                        delta="LUNAS 🎉" if is_lunas else f"Sisa hutang berkurang",
                        delta_color="normal" if is_lunas else "inverse"
                    )
                
                with col_pay3:
                    st.metric(
                        "💰 Sisa Profit Ditahan",
                        f"Rp {retained_earnings:,.0f}",
                        help="Uang ini aman untuk diambil owner atau diputar lagi",
                        delta="Cashflow Aman"
                    )

                if not is_lunas:
                    st.write(f"**Progress Pelunasan Periode Ini:**")
                    progress_val = min(1.0, payment_amount / input_loan)
                    st.progress(progress_val)
                    st.caption(f"Dari total hutang Rp {input_loan:,.0f}, kamu membayar Rp {payment_amount:,.0f} hari ini.")
                else:
                    st.success("🎉 Selamat! Alokasi keuntungan ini cukup untuk melunasi seluruh sisa pinjaman Anda!")

            else:
                st.warning(f"⚠️ Periode ini bisnis merugi (Rp {net_profit:,.0f}). Tidak bisa melakukan pembayaran pinjaman dari profit.")
                st.metric("Sisa Pinjaman Tetap", f"Rp {input_loan:,.0f}")
        
        st.markdown("---")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        col_stat1.metric("🏆 Hari Terbaik", f"Rp {best_day['Profit']:,.0f}", 
                        delta=best_day['Date'].strftime('%d %b'))
        col_stat2.metric("📉 Hari Terburuk", f"Rp {worst_day['Profit']:,.0f}",
                        delta=worst_day['Date'].strftime('%d %b'))
        col_stat3.metric("✅ Hari Untung", profitable_days, 
                        delta=f"{(profitable_days/len(df)*100):.0f}%")
        col_stat4.metric("⚠️ Hari Rugi", loss_days,
                        delta=f"{(loss_days/len(df)*100):.0f}%")
        
        st.divider()
        st.markdown("## 📊 Visualisasi Data")
        
        tab1, tab2, tab3, tab4 = st.tabs(["💹 Tren Keuangan", "📅 Analisis Harian", "🎯 Performa Detail", "📋 Data Lengkap"])
        
        with tab1:
            st.markdown("<p class='caption-custom'>Pergerakan Pemasukan, Pengeluaran, dan Profit</p>", unsafe_allow_html=True)
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Income'],
                name='Pemasukan',
                line=dict(color='#10b981', width=3),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>Pemasukan</b><br>Tanggal: %{x|%d %b %Y}<br>Nilai: Rp %{y:,.0f}<extra></extra>'
            ))

            fig_trend.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Expense'],
                name='Pengeluaran',
                line=dict(color='#ef4444', width=3),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>Pengeluaran</b><br>Tanggal: %{x|%d %b %Y}<br>Nilai: Rp %{y:,.0f}<extra></extra>'
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Profit'],
                name='Keuntungan',
                line=dict(color='#8b5cf6', width=3, dash='dash'),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>Keuntungan</b><br>Tanggal: %{x|%d %b %Y}<br>Nilai: Rp %{y:,.0f}<extra></extra>'
            ))
            
            fig_trend.update_layout(
                height=500,
                hovermode='x unified',
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="right", 
                    x=1,
                    font=dict(size=12)
                ),
                yaxis=dict(
                    title="Rupiah (Rp)", 
                    gridcolor='#f3f4f6',
                    tickformat=',.0f'
                ),
                xaxis=dict(
                    title="Tanggal", 
                    gridcolor='#f3f4f6'
                ),
                plot_bgcolor='white',
                font=dict(size=12)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            col_insight1, col_insight2 = st.columns(2)
            with col_insight1:
                trend_direction = "📈 Naik" if df['Profit'].iloc[-1] > df['Profit'].iloc[0] else "📉 Turun"
                st.info(f"**Tren Profit:** {trend_direction}")
            with col_insight2:
                volatility = df['Profit'].std()
                st.info(f"**Volatilitas:** {'Stabil' if volatility < avg_profit * 0.5 else 'Fluktuatif'}")
        
        with tab2:
            col_day1, col_day2 = st.columns(2)
            
            with col_day1:
                st.markdown("<p class='caption-custom'>Profit per Hari</p>", unsafe_allow_html=True)
                
                colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Profit']]
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=df['Date'],
                        y=df['Profit'],
                        marker=dict(
                            color=colors,
                            line=dict(color='white', width=1)
                        ),
                        text=[f"Rp {x:,.0f}" for x in df['Profit']],
                        textposition='outside',
                        hovertemplate='<b>%{x|%d %b}</b><br>Profit: Rp %{y:,.0f}<extra></extra>'
                    )
                ])
                fig_bar.update_layout(
                    height=400,
                    yaxis=dict(title="Profit (Rp)", gridcolor='#f3f4f6'),
                    xaxis=dict(title="Tanggal", gridcolor='#f3f4f6'),
                    plot_bgcolor='white',
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_day2:
                st.markdown("<p class='caption-custom'>Rata-rata per Hari dalam Seminggu</p>", unsafe_allow_html=True)
                
                day_avg = df.groupby('Day')['Profit'].mean().reindex([
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                ])
                day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
                
                fig_day = go.Figure(data=[
                    go.Bar(
                        x=day_names,
                        y=day_avg.values,
                        marker=dict(
                            color=day_avg.values,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Profit")
                        ),
                        text=[f"Rp {x:,.0f}" for x in day_avg.values],
                        textposition='outside'
                    )
                ])
                fig_day.update_layout(
                    height=400,
                    yaxis=dict(title="Avg Profit (Rp)", gridcolor='#f3f4f6'),
                    xaxis=dict(title="Hari", gridcolor='#f3f4f6'),
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_day, use_container_width=True)
        
        with tab3:
            col_perf1, col_perf2 = st.columns(2)
            
            with col_perf1:
                st.markdown("<p class='caption-custom'>Distribusi Profit Margin (%)</p>", unsafe_allow_html=True)
                
                valid_margins = df[df['Profit_Margin'].notna() & (df['Profit_Margin'] != float('inf'))]['Profit_Margin']
                
                if len(valid_margins) > 0:
                    fig_margin = go.Figure(data=[
                        go.Histogram(
                            x=valid_margins,
                            nbinsx=15,
                            marker=dict(
                                color='#8b5cf6',
                                line=dict(color='white', width=1)
                            ),
                            hovertemplate='Margin: %{x:.1f}%<br>Count: %{y}<extra></extra>'
                        )
                    ])
                    fig_margin.update_layout(
                        height=350,
                        xaxis_title="Profit Margin (%)",
                        yaxis_title="Frekuensi (Hari)",
                        plot_bgcolor='white',
                        bargap=0.1,
                        xaxis=dict(gridcolor='#f3f4f6'),
                        yaxis=dict(gridcolor='#f3f4f6')
                    )
                    st.plotly_chart(fig_margin, use_container_width=True)
                    st.metric("Median Margin", f"{valid_margins.median():.1f}%")
                else:
                    st.warning("Data profit margin tidak tersedia")
            
            with col_perf2:
                st.markdown("<p class='caption-custom'>Perbandingan Income vs Expense</p>", unsafe_allow_html=True)
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Keuntungan Bersih', 'Pengeluaran'],
                    values=[net_profit, total_expense],
                    hole=.4,
                    marker=dict(colors=['#10b981', '#ef4444']),
                    textinfo='label+percent',
                    textfont_size=13,
                    hovertemplate='<b>%{label}</b><br>Nilai: Rp %{value:,.0f}<br>Persentase: %{percent}<extra></extra>'
                )])
                fig_pie.update_layout(
                    height=350,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                efficiency = (net_profit / total_income * 100) if total_income > 0 else 0
                st.metric("Efisiensi Bisnis", f"{efficiency:.1f}%")
            
            st.markdown("---")
            st.markdown("<p class='caption-custom'>Tren Mingguan</p>", unsafe_allow_html=True)
           
            weekly = df.groupby('Week').agg({
                'Income': 'sum',
                'Expense': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            if len(weekly) > 0:
                fig_weekly = go.Figure()
                fig_weekly.add_trace(go.Bar(
                    x=[f"Minggu {int(w)}" for w in weekly['Week']],
                    y=weekly['Profit'],
                    name='Profit Mingguan',
                    marker=dict(
                        color=weekly['Profit'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Profit (Rp)")
                    ),
                    text=[f"Rp {p:,.0f}" for p in weekly['Profit']],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Profit: Rp %{y:,.0f}<extra></extra>'
                ))
                fig_weekly.update_layout(
                    height=350,
                    xaxis_title="Periode",
                    yaxis_title="Profit (Rp)",
                    plot_bgcolor='white',
                    xaxis=dict(gridcolor='#f3f4f6'),
                    yaxis=dict(gridcolor='#f3f4f6', tickformat=',.0f'),
                    showlegend=False
                )
                st.plotly_chart(fig_weekly, use_container_width=True)
            else:
                st.info("Data mingguan belum cukup untuk ditampilkan")
        
        with tab4:
            st.markdown("<p class='caption-custom'>Tabel Data Lengkap dengan Analisis</p>", unsafe_allow_html=True)
            
            display_df = df.copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%d %b %Y')
            display_df['Income'] = display_df['Income'].apply(lambda x: f"Rp {x:,.0f}")
            display_df['Expense'] = display_df['Expense'].apply(lambda x: f"Rp {x:,.0f}")
            display_df['Profit'] = display_df['Profit'].apply(lambda x: f"Rp {x:,.0f}")
            display_df['Profit_Margin'] = display_df['Profit_Margin'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                display_df[['Date', 'Day', 'Income', 'Expense', 'Profit', 'Profit_Margin', 'Notes']],
                use_container_width=True,
                height=400
            )
            
            csv_export = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Data (CSV)",
                csv_export,
                "data_analisis_bizmind.csv",
                "text/csv"
            )
        
        st.divider()
        st.markdown("## 🤖 Konsultasi AI - Analisis Mendalam")
        
        col_ai_desc, col_ai_button = st.columns([3, 1])
        
        with col_ai_desc:
            st.markdown("""
            AI kami akan menganalisis pola bisnis Anda dan memberikan:
            - 📊 Evaluasi kondisi keuangan terkini
            - 💡 Rekomendasi aksi konkret yang bisa dilakukan segera
            - ⚠️ Peringatan dini jika ada tren yang perlu diwaspadai
            - 🎯 Strategi jangka pendek untuk optimasi profit
            """)
        
        with col_ai_button:
            st.markdown("<br>", unsafe_allow_html=True)
            ai_trigger = st.button("🚀 Analisa Sekarang", type="primary", use_container_width=True)
        
        if ai_trigger or 'ai_result' in st.session_state:
            if ai_trigger:
                summary = f"""
                📊 RINGKASAN KEUANGAN:
                - Total Pemasukan: Rp {total_income:,.0f}
                - Total Pengeluaran: Rp {total_expense:,.0f}
                - Keuntungan Bersih: Rp {net_profit:,.0f}
                - Profit Margin: {profit_margin_avg:.1f}%
                - Rata-rata Profit Harian: Rp {avg_profit:,.0f}
                
                📅 PERIODE & PERFORMA:
                - Periode: {df['Date'].min().strftime('%d %b %Y')} - {df['Date'].max().strftime('%d %b %Y')}
                - Total Hari: {len(df)} hari
                - Hari Untung: {profitable_days} hari ({profitable_days/len(df)*100:.0f}%)
                - Hari Rugi: {loss_days} hari ({loss_days/len(df)*100:.0f}%)
                
                🏆 BEST & WORST:
                - Hari Terbaik: {best_day['Date'].strftime('%d %b')} (Rp {best_day['Profit']:,.0f})
                - Hari Terburuk: {worst_day['Date'].strftime('%d %b')} (Rp {worst_day['Profit']:,.0f})
                
                📈 TREN:
                - Hari paling menguntungkan: {df.groupby('Day')['Profit'].mean().idxmax()}
                - Volatilitas: {"Tinggi" if df['Profit'].std() > avg_profit else "Rendah"}
                """
                
                trend_info = f"""
                - Tren profit: {"Meningkat" if df['Profit'].iloc[-1] > df['Profit'].iloc[0] else "Menurun"}
                - Stabilitas: {"Stabil" if df['Profit'].std() < avg_profit * 0.5 else "Fluktuatif"}
                - 3 Catatan terakhir: {', '.join(df['Notes'].tail(3).values)}
                """
                
                analysis_result = get_ai_advice(business_type, summary, trend_info)
                st.session_state['ai_result'] = analysis_result
            
            st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
            st.markdown("### 🎯 Hasil Analisis AI")
            st.markdown(st.session_state['ai_result'])
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📄 Simpan Laporan Lengkap")
            
            col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
            
            with col_pdf2:
                st.info("💾 Dapatkan laporan PDF lengkap dengan analisis AI dan semua visualisasi")
                
                if st.button("📥 Generate Laporan PDF", type="primary", use_container_width=True):
                    with st.spinner("🎨 Membuat laporan profesional..."):
                        
                        summary_stats = {
                            "Jenis Bisnis": business_type,
                            "Periode": f"{df['Date'].min().strftime('%d %b %Y')} - {df['Date'].max().strftime('%d %b %Y')}",
                            "Total Hari": f"{len(df)} hari",
                            "Total Pemasukan": f"Rp {total_income:,.0f}",
                            "Total Pengeluaran": f"Rp {total_expense:,.0f}",
                            "Keuntungan Bersih": f"Rp {net_profit:,.0f}",
                            "Profit Margin": f"{profit_margin_avg:.1f}%",
                            "Hari Untung": f"{profitable_days} hari",
                            "Hari Rugi": f"{loss_days} hari"
                        }
                        
                        fig_pdf1 = go.Figure()
                        fig_pdf1.add_trace(go.Scatter(
                            x=df['Date'], y=df['Income'],
                            name='Pemasukan', line=go.scatter.Line(color='green', width=3)
                        ))
                        fig_pdf1.add_trace(go.Scatter(
                            x=df['Date'], y=df['Expense'],
                            name='Pengeluaran',line=go.scatter.Line(color='red', width=3)
                        ))
                        fig_pdf1.update_layout(
                            title="Grafik Pemasukan vs Pengeluaran",
                            xaxis_title="Tanggal", yaxis_title="Rupiah",
                            height=500, plot_bgcolor='white'
                        )
                        
                        fig_pdf2 = go.Figure(data=[
                            go.Bar(
                                x=df['Date'], y=df['Profit'],
                                marker=dict(color=['green' if x > 0 else 'red' for x in df['Profit']])
                            )
                        ])
                        fig_pdf2.update_layout(
                            title="Keuntungan Harian",
                            xaxis_title="Tanggal", yaxis_title="Profit (Rp)",
                            height=500, plot_bgcolor='white', showlegend=False
                        )
                        
                        day_avg = df.groupby('Day')['Profit'].mean().reindex([
                            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                        ])
                        day_names_id = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
                        
                        fig_pdf3 = go.Figure(data=[
                            go.Bar(x=day_names_id, y=day_avg.values, marker=dict(color='blue'))
                        ])
                        fig_pdf3.update_layout(
                            title="Rata-rata Profit per Hari Minggu",
                            xaxis_title="Hari", yaxis_title="Avg Profit (Rp)",
                            height=500, plot_bgcolor='white'
                        )
                        
                        figures_with_titles = [
                            (fig_pdf1, "Grafik 1: Tren Pemasukan & Pengeluaran"),
                            (fig_pdf2, "Grafik 2: Profit Harian"),
                            (fig_pdf3, "Grafik 3: Performa per Hari dalam Seminggu")
                        ]
                        
                        pdf_bytes = create_pdf(
                            business_type,
                            st.session_state['ai_result'],
                            summary_stats,
                            figures_with_titles
                        )
                        
                        st.download_button(
                            label="📄 Download Laporan PDF",
                            data=pdf_bytes,
                            file_name=f"Laporan_{business_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success("✅ Laporan siap diunduh!")

else:
    st.info("👆 **Mulai dengan mengupload file CSV data keuangan Anda di atas**")
    
    st.markdown("---")
    st.markdown("### 🎯 Apa yang Bisa Dilakukan BizMind Pro?")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("""
        #### 📊 Analisis Otomatis
        - Hitung profit/loss otomatis
        - Identifikasi tren keuangan
        - Deteksi pola performa harian
        - Analisis margin & efisiensi
        """)
    
    with col_feat2:
        st.markdown("""
        #### 🤖 Rekomendasi AI
        - Saran bisnis konkret
        - Strategi optimasi profit
        - Peringatan dini masalah
        - Tips berdasarkan data riil
        """)
    
    with col_feat3:
        st.markdown("""
        #### 📈 Visualisasi Lengkap
        - 10+ jenis grafik interaktif
        - Perbandingan periode
        - Ekspor laporan PDF
        - Dashboard real-time
        """)
    
    st.markdown("---")
    st.markdown("### 💼 Cocok untuk:")
    
    col_use1, col_use2 = st.columns(2)
    with col_use1:
        st.markdown("""
        - ☕ Warung & Kedai Kopi
        - 🍜 Resto & Catering
        - 🛒 Toko & Minimarket
        - 👕 Fashion & Boutique
        """)
    
    with col_use2:
        st.markdown("""
        - 💇 Salon & Barbershop
        - 🎂 Bakery & Pastry
        - 🚗 Bengkel & Cuci Mobil
        - 📦 Jasa Pengiriman
        """)
    
    st.markdown("---")
    st.success("🚀 Upload data Anda sekarang dan dapatkan insights dalam hitungan detik!")