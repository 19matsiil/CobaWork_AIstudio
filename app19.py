import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# KONFIGURASI HALAMAN & TEMA KORPORAT TELKOM
# ==============================================================================
st.set_page_config(
    page_title="Telkom Group 2025: Subsidiary & Venture Health Tracker",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Warna Korporat Telkom (Merah, Abu-abu Gelap, Abu-abu Terang)
TELKOM_RED = "#E60000"
TELKOM_DARK_RED = "#B30000"
TELKOM_DARK_GRAY = "#2C3E50"
TELKOM_GRAY = "#6C757D"
TELKOM_LIGHT_GRAY = "#E9ECEF"

# Custom CSS untuk estetika kartu metrik & header
st.markdown(
    f"""
    <style>
        .main-header {{
            font-size: 2.1rem;
            font-weight: 800;
            color: {TELKOM_DARK_GRAY};
            border-bottom: 4px solid {TELKOM_RED};
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .sub-header {{
            font-size: 1.05rem;
            color: {TELKOM_GRAY};
            margin-top: -12px;
            margin-bottom: 25px;
        }}
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-left: 5px solid {TELKOM_RED};
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: #F8F9FA;
            border-radius: 6px 6px 0px 0px;
            padding: 10px 20px;
            font-weight: 600;
            color: {TELKOM_DARK_GRAY};
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {TELKOM_RED} !important;
            color: white !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# FUNGSI DATA MOCK (KONSISTEN DENGAN PROFIL KEUANGAN TELKOM 2025)
# ==============================================================================
@st.cache_data
def load_consolidated_kpis():
    """Mengembalikan KPI utama konsolidasi Telkom Group 2025."""
    return {
        "revenue_2025": 146742.0,  # Rp Miliar
        "revenue_yoy": -2.2,       # %
        "net_income_2025": 17814.0,
        "net_income_yoy": -20.5,
        "ebt_2025": 24150.0,       # Estimasi Laba Sebelum Pajak (EBT)
        "depr_amort_2025": 37649.0,
        "depr_amort_yoy": 10.1,
        "mtm_loss_2025": -242.0,   # Mark-to-Market Loss 2025
        "mtm_gain_2024": 188.0,    # Mark-to-Market Gain 2024
    }


@st.cache_data
def load_subsidiary_data():
    """Data kinerja entitas anak & segmen bisnis (2024 vs 2025) dalam Rp Miliar."""
    data = [
        {
            "Entitas": "Telkomsel (B2C)",
            "Segmen": "B2C Mobile & Fixed",
            "Pendapatan_2024": 113400.0,
            "Pendapatan_2025": 111700.0,
            "Laba_Bersih_2024": 22150.0,
            "Laba_Bersih_2025": 20450.0,
            "Total_Aset": 185000.0,
            "Kategori_Kuadran": "Cash Cow",
            "Catatan": "Margin tinggi, pertumbuhan mendatar akibat saturasi pasar.",
        },
        {
            "Entitas": "Mitratel / Infra (B2B Infra)",
            "Segmen": "B2B Infra",
            "Pendapatan_2024": 18500.0,
            "Pendapatan_2025": 19650.0,
            "Laba_Bersih_2024": 3120.0,
            "Laba_Bersih_2025": 1987.0,  # Margin operasional/bersih tertekan (-36.3%)
            "Total_Aset": 62500.0,
            "Kategori_Kuadran": "Stars / Expansion",
            "Catatan": "Pendapatan kuat, namun margin tertekan beban ekspansi & akuisisi.",
        },
        {
            "Entitas": "Telkomsigma (B2B ICT)",
            "Segmen": "B2B ICT",
            "Pendapatan_2024": 5420.0,
            "Pendapatan_2025": 5664.0,
            "Laba_Bersih_2024": -185.0,
            "Laba_Bersih_2025": -363.6,
            "Total_Aset": 7800.0,
            "Kategori_Kuadran": "Turnaround",
            "Catatan": "Dalam fase transformasi Clean Sheet Strategy, rugi Rp363,6 M.",
        },
        {
            "Entitas": "Telkomsat",
            "Segmen": "B2B Infra & Satelit",
            "Pendapatan_2024": 1820.0,
            "Pendapatan_2025": 1965.0,
            "Laba_Bersih_2024": -95.0,
            "Laba_Bersih_2025": -249.5,
            "Total_Aset": 9200.0,
            "Kategori_Kuadran": "Question Mark / Turnaround",
            "Catatan": "Rugi Rp249,5 M akibat beban bunga pinjaman & depresiasi satelit.",
        },
        {
            "Entitas": "MDI Ventures / GoTo",
            "Segmen": "Venture Capital",
            "Pendapatan_2024": 480.0,
            "Pendapatan_2025": 410.0,
            "Laba_Bersih_2024": 188.0,   # MTM Gain 2024
            "Laba_Bersih_2025": -242.0,  # MTM Loss 2025
            "Total_Aset": 11500.0,
            "Kategori_Kuadran": "Question Mark",
            "Catatan": "Volatilitas nilai wajar portofolio startup & saham GoTo.",
        },
        {
            "Entitas": "Lainnya & Eliminasi",
            "Segmen": "Lainnya",
            "Pendapatan_2024": 10420.0,
            "Pendapatan_2025": 7353.0,
            "Laba_Bersih_2024": -2770.0,
            "Laba_Bersih_2025": -3767.9,
            "Total_Aset": 24000.0,
            "Kategori_Kuadran": "Holding / Eliminasi",
            "Catatan": "Biaya korporat holding, eliminasi antar entitas, dan pajak.",
        },
    ]
    df = pd.DataFrame(data)
    df["Pertumbuhan_Pendapatan_YoY"] = (
        (df["Pendapatan_2025"] - df["Pendapatan_2024"]) / df["Pendapatan_2024"]
    ) * 100
    df["Net_Profit_Margin_2025"] = (df["Laba_Bersih_2025"] / df["Pendapatan_2025"]) * 100
    return df


@st.cache_data
def load_portfolio_history():
    """Data historis nilai portofolio investasi VC & GoTo Telkom Group (Rp Miliar)."""
    return pd.DataFrame(
        {
            "Tahun": ["2021", "2022", "2023", "2024", "2025"],
            "Nilai_Portofolio_Miliar": [14800, 9200, 10450, 10638, 10396],
            "Unrealized_Gain_Loss_Miliar": [2100, -5600, 1250, 188, -242],
        }
    )


def convert_df_to_excel(df):
    """Mengonversi DataFrame ke format Excel (bytes) untuk tombol unduh."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Telkom_2025_Summary")
    return output.getvalue()


# ==============================================================================
# LOAD DATA
# ==============================================================================
kpis = load_consolidated_kpis()
df_subs = load_subsidiary_data()
df_port_hist = load_portfolio_history()

# ==============================================================================
# SIDEBAR & FILTER KONTROL
# ==============================================================================
with st.sidebar:
    st.markdown(
        f"<h2 style='color:{TELKOM_RED}; margin-bottom:0;'>📡 TELKOM GROUP</h2>"
        "<p style='color:gray; font-size:0.9rem;'>Holding Management Control</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # 1. Filter Segmen / Anak Perusahaan
    filter_options = [
        "All",
        "Telkomsel (B2C)",
        "Telkomsigma (B2B ICT)",
        "Telkomsat",
        "Mitratel / Infra (B2B Infra)",
        "MDI Ventures / GoTo",
    ]
    selected_entity = st.selectbox(
        "🔍 Filter Segmen / Anak Perusahaan:",
        options=filter_options,
        index=0,
    )

    st.divider()

    # 2. Slider Skenario Mark-to-Market GoTo
    st.markdown("### 📉 Skenario Mark-to-Market GoTo")
    st.caption(
        "Simulasikan perubahan harga saham GoTo terhadap laba bersih konsolidasian (Asumsi basis 2025: Rp70/lembar)."
    )
    goto_price = st.slider(
        "Harga Saham GoTo (Rp/lembar):",
        min_value=40,
        max_value=120,
        value=70,
        step=5,
        format="Rp%d",
    )

    # Asumsi eksposur: ~23.7 Miliar lembar saham (sensitivitas Rp23,7 M per Rp1 perubahan harga)
    goto_shares_billion = 23.7
    goto_base_price = 70
    goto_impact_miliar = (goto_price - goto_base_price) * goto_shares_billion

    st.info(
        f"Dampak Simulasi GoTo: **{'+' if goto_impact_miliar >= 0 else ''}Rp{goto_impact_miliar:,.1f} Miliar** ke Laba Konsolidasi"
    )

    st.divider()

    # 3. Tombol Unduh Laporan Ringkas
    st.markdown("### 📥 Unduh Laporan Ringkas")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_data = df_subs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 CSV",
            data=csv_data,
            file_name="Telkom_2025_Subsidiary_Health.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_dl2:
        try:
            excel_data = convert_df_to_excel(df_subs)
            st.download_button(
                label="📊 Excel",
                data=excel_data,
                file_name="Telkom_2025_Subsidiary_Health.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Gagal ekspor Excel: {e}")


# Filter DataFrame berdasarkan pilihan sidebar
if selected_entity == "All":
    df_filtered = df_subs.copy()
else:
    df_filtered = df_subs[df_subs["Entitas"] == selected_entity].copy()


# ==============================================================================
# HEADER UTAMA
# ==============================================================================
st.markdown(
    '<div class="main-header">Telkom Group 2025: Subsidiary & Venture Health Tracker</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Dashboard Pemantauan Kinerja Operasional, Solvabilitas, Profitabilitas Anak Usaha, & Volatilitas Portofolio Investasi</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# STRUKTUR TAB DASHBOARD
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Executive Overview & KPI",
        "🎯 Matriks Kuadran Anak Usaha",
        "🔧 Deep Dive Pemulihan (Sigma & Sat)",
        "💹 Simulator Valuasi VC & GoTo",
    ]
)

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW & KPI PORTOFOLIO
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Ringkasan Kinerja Konsolidasi (FY 2025)")

    # Top Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Total Pendapatan Konsolidasi",
            value=f"Rp{kpis['revenue_2025']:,.0f} M",
            delta=f"{kpis['revenue_yoy']}% YoY",
            delta_color="normal",
        )
    with m2:
        # Laba bersih disesuaikan jika slider GoTo digeser di sidebar
        adjusted_net_income = kpis["net_income_2025"] + goto_impact_miliar
        delta_ni_text = f"{kpis['net_income_yoy']}% YoY"
        if goto_impact_miliar != 0:
            delta_ni_text += f" (Simulasi: {'+' if goto_impact_miliar>0 else ''}{goto_impact_miliar:,.0f}M)"
        st.metric(
            label="Laba Bersih Pemilik Entitas Induk",
            value=f"Rp{adjusted_net_income:,.0f} M",
            delta=delta_ni_text,
            delta_color="normal",
        )
    with m3:
        st.metric(
            label="Beban Depresiasi & Amortisasi",
            value=f"Rp{kpis['depr_amort_2025']:,.0f} M",
            delta=f"+{kpis['depr_amort_yoy']}% YoY",
            delta_color="inverse",  # Kenaikan beban diberi warna merah
        )
    with m4:
        mtm_diff = kpis["mtm_loss_2025"] - kpis["mtm_gain_2024"]
        st.metric(
            label="Portofolio Mark-to-Market",
            value=f"Rp{kpis['mtm_loss_2025']:,.0f} M",
            delta=f"Rp{mtm_diff:,.0f} M vs 2024 (+188M)",
            delta_color="normal",
        )

    st.markdown("---")

    # Grafik Interaktif
    col_c1, col_c2 = st.columns([1.4, 1])

    with col_c1:
        st.markdown("#### Perbandingan Pendapatan & Laba Bersih per Entitas (2024 vs 2025)")
        metric_choice = st.radio(
            "Pilih Metrik:",
            ["Pendapatan", "Laba Bersih"],
            horizontal=True,
            key="tab1_radio",
        )

        # Persiapkan data untuk grouped bar chart
        df_plot = df_filtered[df_filtered["Entitas"] != "Lainnya & Eliminasi"].copy()
        if metric_choice == "Pendapatan":
            df_melt = df_plot.melt(
                id_vars="Entitas",
                value_vars=["Pendapatan_2024", "Pendapatan_2025"],
                var_name="Tahun",
                value_name="Nilai (Rp Miliar)",
            )
            df_melt["Tahun"] = df_melt["Tahun"].replace(
                {"Pendapatan_2024": "2024", "Pendapatan_2025": "2025"}
            )
        else:
            df_melt = df_plot.melt(
                id_vars="Entitas",
                value_vars=["Laba_Bersih_2024", "Laba_Bersih_2025"],
                var_name="Tahun",
                value_name="Nilai (Rp Miliar)",
            )
            df_melt["Tahun"] = df_melt["Tahun"].replace(
                {"Laba_Bersih_2024": "2024", "Laba_Bersih_2025": "2025"}
            )

        fig_bar = px.bar(
            df_melt,
            x="Entitas",
            y="Nilai (Rp Miliar)",
            color="Tahun",
            barmode="group",
            color_discrete_map={"2024": TELKOM_GRAY, "2025": TELKOM_RED},
            text_auto=".0f",
            template="plotly_white",
        )
        fig_bar.update_layout(
            xaxis_title="",
            yaxis_title="Rp Miliar",
            legend_title="Tahun",
            height=420,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.markdown("#### Kontribusi Laba/Rugi Entitas (2025)")
        # Untuk Donut chart, gunakan nilai absolut agar proporsi terlihat, dan tampilkan status Laba/Rugi di hover
        df_donut = df_subs[df_subs["Entitas"] != "Lainnya & Eliminasi"].copy()
        df_donut["Abs_Laba"] = df_donut["Laba_Bersih_2025"].abs()
        df_donut["Status"] = np.where(
            df_donut["Laba_Bersih_2025"] >= 0, "Laba", "Rugi"
        )

        fig_donut = px.pie(
            df_donut,
            values="Abs_Laba",
            names="Entitas",
            hole=0.52,
            color="Entitas",
            color_discrete_sequence=[
                TELKOM_RED,
                TELKOM_DARK_GRAY,
                "#FF6B6B",
                "#FFA07A",
                "#ADB5BD",
            ],
            hover_data=["Laba_Bersih_2025", "Status"],
            template="plotly_white",
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Laba/Rugi: Rp%{customdata[0][0]:,.1f} M<br>Status: %{customdata[0][1]}<extra></extra>",
        )
        fig_donut.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Tabel Ringkasan
    with st.expander("📋 Lihat Tabel Detail Kinerja Entitas Anak (2024 vs 2025)"):
        st.dataframe(
            df_filtered[
                [
                    "Entitas",
                    "Segmen",
                    "Pendapatan_2024",
                    "Pendapatan_2025",
                    "Pertumbuhan_Pendapatan_YoY",
                    "Laba_Bersih_2024",
                    "Laba_Bersih_2025",
                    "Net_Profit_Margin_2025",
                    "Kategori_Kuadran",
                ]
            ].style.format(
                {
                    "Pendapatan_2024": "Rp{:,.1f} M",
                    "Pendapatan_2025": "Rp{:,.1f} M",
                    "Pertumbuhan_Pendapatan_YoY": "{:+.2f}%",
                    "Laba_Bersih_2024": "Rp{:,.1f} M",
                    "Laba_Bersih_2025": "Rp{:,.1f} M",
                    "Net_Profit_Margin_2025": "{:+.2f}%",
                }
            ),
            use_container_width=True,
        )


# ------------------------------------------------------------------------------
# TAB 2: MATRIKS KUADRAN ANAK PERUSAHAAN (GROWTH-SHARE MATRIX)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Matriks Kuadran Anak Perusahaan (Growth-Share Matrix 2025)")
    st.caption(
        "Pemetaan posisi strategis entitas anak berdasarkan Pertumbuhan Pendapatan YoY (Sumbu X), "
        "Net Profit Margin (Sumbu Y), dan Total Aset (Ukuran Gelembung)."
    )

    df_matrix = df_subs[df_subs["Entitas"] != "Lainnya & Eliminasi"].copy()

    fig_scatter = px.scatter(
        df_matrix,
        x="Pertumbuhan_Pendapatan_YoY",
        y="Net_Profit_Margin_2025",
        size="Total_Aset",
        color="Kategori_Kuadran",
        text="Entitas",
        hover_name="Entitas",
        hover_data={
            "Total_Aset": ":,.0f",
            "Pendapatan_2025": ":,.0f",
            "Laba_Bersih_2025": ":,.1f",
            "Catatan": True,
        },
        size_max=65,
        color_discrete_map={
            "Cash Cow": TELKOM_DARK_GRAY,
            "Stars / Expansion": "#28A745",
            "Turnaround": TELKOM_RED,
            "Question Mark / Turnaround": "#FD7E14",
            "Question Mark": "#FFC107",
        },
        template="plotly_white",
    )

    # Garis Kuadran (X = 3% pertumbuhan, Y = 5% NPM)
    fig_scatter.add_vline(x=3.0, line_dash="dash", line_color="gray", opacity=0.6)
    fig_scatter.add_hline(y=5.0, line_dash="dash", line_color="gray", opacity=0.6)

    # Anotasi Kuadran
    fig_scatter.add_annotation(
        x=9, y=23, text="⭐ STARS", showarrow=False, font=dict(size=13, color="#28A745")
    )
    fig_scatter.add_annotation(
        x=-8, y=23, text="🐄 CASH COWS", showarrow=False, font=dict(size=13, color=TELKOM_DARK_GRAY)
    )
    fig_scatter.add_annotation(
        x=9, y=-20, text="❓ QUESTION MARKS", showarrow=False, font=dict(size=13, color="#FD7E14")
    )
    fig_scatter.add_annotation(
        x=-8, y=-20, text="🔧 TURNAROUND / DOGS", showarrow=False, font=dict(size=13, color=TELKOM_RED)
    )

    fig_scatter.update_traces(textposition="top center", textfont=dict(size=11))
    fig_scatter.update_layout(
        xaxis_title="Pertumbuhan Pendapatan YoY (%)",
        yaxis_title="Net Profit Margin (%)",
        height=550,
        xaxis=dict(range=[-18, 14]),
        yaxis=dict(range=[-65, 30]),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 3: DEEP DIVE ANAK USAHA DALAM PEMULIHAN (TELKOMSIGMA & TELKOMSAT)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Deep Dive Pemulihan: Telkomsigma & Telkomsat")

    col_t1, col_t2 = st.columns(2)

    # --- SUB-ANALISIS TELKOMSIGMA ---
    with col_t1:
        st.markdown("### 1. Telkomsigma: Pelacak *Clean Sheet Strategy*")
        st.caption(
            "Jembatan pemulihan laba dari posisi rugi bersih 2025 (-Rp363,6 M) menuju target titik impas (Break-Even)."
        )

        fig_wf = go.Figure(
            go.Waterfall(
                name="Clean Sheet",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "total"],
                x=[
                    "Rugi Bersih 2025",
                    "Hapus Proyek Margin Rendah",
                    "Efisiensi OPEX & SDM",
                    "Pertumbuhan Cloud/AI B2B",
                    "Target Break-Even 2026",
                ],
                textposition="outside",
                text=["-363.6", "+145.0", "+120.0", "+110.0", "+11.4"],
                y=[-363.6, 145.0, 120.0, 110.0, 11.4],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": TELKOM_RED}},
                increasing={"marker": {"color": "#28A745"}},
                totals={"marker": {"color": TELKOM_DARK_GRAY}},
            )
        )
        fig_wf.update_layout(
            yaxis_title="Rp Miliar",
            height=400,
            template="plotly_white",
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)

        st.warning(
            "**Actionable Insight (Telkomsigma):** Fokus pada selektivitas kontrak B2B ICT, "
            "hentikan proyek *legacy* dengan margin <10%, dan percepat migrasi ke layanan *Managed Cloud*."
        )

    # --- SUB-ANALISIS TELKOMSAT ---
    with col_t2:
        st.markdown("### 2. Telkomsat: Struktur Biaya & Transisi Orbit")
        st.caption(
            "Analisis beban bunga & depresiasi satelit vs pergeseran pendapatan transponder ke satelit orbit rendah (LEO/HTS)."
        )

        df_sat_cost = pd.DataFrame(
            {
                "Komponen": [
                    "Pendapatan Transponder Konvensional",
                    "Pendapatan HTS & LEO (Starlink/MP2)",
                    "Beban Depresiasi Satelit",
                    "Beban Bunga Pinjaman",
                    "Beban Operasional Lainnya",
                ],
                "Nilai_Miliar": [1120, 845, -1080, -490, -644.5],
                "Tipe": ["Pendapatan", "Pendapatan", "Beban", "Beban", "Beban"],
            }
        )

        fig_sat = px.bar(
            df_sat_cost,
            x="Nilai_Miliar",
            y="Komponen",
            orientation="h",
            color="Tipe",
            color_discrete_map={"Pendapatan": "#28A745", "Beban": TELKOM_RED},
            text_auto=".1f",
            template="plotly_white",
        )
        fig_sat.update_layout(
            xaxis_title="Rp Miliar (2025)",
            yaxis_title="",
            height=400,
            legend_title="Kategori",
        )
        st.plotly_chart(fig_sat, use_container_width=True)

        st.info(
            "**Actionable Insight (Telkomsat):** Optimalkan utilisasi kapasitas *High Throughput Satellite* (HTS) "
            "untuk sektor maritim & *backhaul* 3T, serta lakukan *refinancing* utang berbunga tinggi."
        )


# ------------------------------------------------------------------------------
# TAB 4: SIMULATOR VALUASI PORTOFOLIO VENTURE CAPITAL & GOTO
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Simulator Valuasi Portofolio Venture Capital & GoTo")
    st.caption(
        "Uji sensitivitas perubahan nilai wajar portofolio investasi (GoTo & MDI Ventures) "
        "terhadap Laba Sebelum Pajak (EBT) konsolidasian Telkom Group."
    )

    col_sim1, col_sim2 = st.columns([1, 1.5])

    with col_sim1:
        st.markdown("#### Parameter Simulasi")
        sim_goto_price = st.number_input(
            "Asumsi Harga Saham GoTo (Rp/lembar):",
            min_value=20,
            max_value=200,
            value=goto_price,
            step=5,
        )
        sim_mdi_pct = st.slider(
            "Perubahan Valuasi Startup MDI Ventures (%):",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            format="%d%%",
        )

        # Kalkulasi dampak
        mdi_base_val = 4500.0  # Asumsi nilai portofolio aktif MDI Rp4.500 Miliar
        impact_goto = (sim_goto_price - 70) * goto_shares_billion
        impact_mdi = mdi_base_val * (sim_mdi_pct / 100.0)
        total_mtm_sim = kpis["mtm_loss_2025"] + impact_goto + impact_mdi
        projected_ebt = kpis["ebt_2025"] + impact_goto + impact_mdi

        st.markdown("---")
        st.metric(
            "Proyeksi Total Mark-to-Market",
            f"Rp{total_mtm_sim:,.1f} M",
            delta=f"Rp{(impact_goto + impact_mdi):+,.1f} M vs Basis 2025 (-242M)",
        )
        st.metric(
            "Proyeksi EBT Konsolidasian",
            f"Rp{projected_ebt:,.1f} M",
            delta=f"{((projected_ebt - kpis['ebt_2025'])/kpis['ebt_2025'])*100:+.2f}%",
        )

    with col_sim2:
        st.markdown("#### Tren Nilai Portofolio Investasi Telkom (2021 - 2025 & Proyeksi)")
        df_hist_plot = df_port_hist.copy()
        proj_val = 10396.0 + impact_goto + impact_mdi
        df_proj = pd.DataFrame(
            {
                "Tahun": ["2026 (Simulasi)"],
                "Nilai_Portofolio_Miliar": [proj_val],
                "Unrealized_Gain_Loss_Miliar": [total_mtm_sim],
            }
        )
        df_combined = pd.concat([df_hist_plot, df_proj], ignore_index=True)

        fig_line = px.line(
            df_combined,
            x="Tahun",
            y="Nilai_Portofolio_Miliar",
            markers=True,
            text="Nilai_Portofolio_Miliar",
            template="plotly_white",
        )
        fig_line.update_traces(
            line_color=TELKOM_RED,
            line_width=3,
            marker=dict(size=10, color=TELKOM_DARK_GRAY),
            textposition="top center",
            texttemplate="Rp%{text:,.0f}M",
        )
        fig_line.update_layout(
            yaxis_title="Nilai Portofolio (Rp Miliar)",
            xaxis_title="Tahun",
            height=420,
        )
        st.plotly_chart(fig_line, use_container_width=True)
