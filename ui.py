import streamlit as st
import html

def load_styles():
    st.markdown(
        """
        <style>

        /* ==============================
           GLOBAL
        ============================== */

        .stApp {
            background: #f6f7fb;
        }

        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* ==============================
           HEADER
        ============================== */

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 8px;
        }

        .brand-icon {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: #111827;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .brand-name {
            font-size: 30px;
            font-weight: 800;
            color: #111827;
            letter-spacing: -1px;
        }

        .brand-subtitle {
            color: #6b7280;
            font-size: 14px;
            margin-top: -3px;
        }

        /* ==============================
           HERO
           ============================== */

        .hero {
            background: #111827;
            border-radius: 24px;
            padding: 34px 36px;
            margin: 24px 0 28px 0;
            color: white;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.15);
            padding: 6px 11px;
            border-radius: 999px;
            font-size: 12px;
            margin-bottom: 16px;
        }

        .hero-title {
            font-size: 34px;
            font-weight: 800;
            letter-spacing: -1.2px;
            margin-bottom: 8px;
        }

        .hero-text {
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.6;
            max-width: 680px;
        }

        /* ==============================
           SECTION HEADERS
           ============================== */

        .section-title {
            font-size: 21px;
            font-weight: 750;
            color: #111827;
            margin-top: 28px;
            margin-bottom: 5px;
        }

        .section-description {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 18px;
        }

        /* ==============================
           CARDS
           ============================== */

        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 16px;
            box-shadow: 0 4px 15px rgba(15,23,42,0.035);
        }

        .card-title {
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 5px;
        }

        .card-text {
            color: #6b7280;
            font-size: 13px;
            line-height: 1.5;
        }

        /* ==============================
           METRICS
           ============================== */

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
        }

        .metric-number {
            font-size: 25px;
            font-weight: 800;
            color: #111827;
        }

        .metric-label {
            color: #6b7280;
            font-size: 12px;
            margin-top: 3px;
        }

        /* ==============================
           PREVIEW
           ============================== */

        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0 12px 0;
        }

        .preview-badge {
            background: #ecfdf5;
            color: #047857;
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: 600;
        }

        /* ==============================
           FOOTER
           ============================== */

        .footer {
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
            padding-top: 25px;
        }

        /* ==============================
           BUTTONS
           ============================== */

        .stButton > button {
            border-radius: 12px;
            min-height: 44px;
            font-weight: 650;
        }

        .stDownloadButton > button {
            border-radius: 12px;
            min-height: 44px;
            font-weight: 650;
        }

        /* ==============================
           FILE UPLOADER
           ============================== */

        [data-testid="stFileUploader"] {
            background: #fafafa;
            border-radius: 14px;
        }

        /* ==============================
           DATAFRAME
           ============================== */

        [data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🏆</div>
            <div>
                <div class="brand-name">CertiFlow</div>
                <div class="brand-subtitle">
                    Automated certificate generation
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_hero():
    html = (
        '<div class="hero">'
        '<div class="hero-badge">CERTIFICATE AUTOMATION</div>'
        '<div class="hero-title">Create certificates in seconds.</div>'
        '<div class="hero-text">'
        'Upload your certificate template and student list. '
        'CertiFlow automatically personalizes every certificate '
        'while preserving your original design.'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )

    

def render_section_title(title, description=None):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )

    if description:
        st.markdown(
            f"""
            <div class="section-description">
                {description}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_upload_card(
    title,
    description,
    uploader_key,
    label,
    file_types,
    help_text=None
):
    safe_title = html.escape(title)
    safe_description = html.escape(description)

    card_html = (
        '<div class="card">'
        '<div class="card-title">'
        f'{safe_title}'
        '</div>'
        '<div class="card-text">'
        f'{safe_description}'
        '</div>'
        '</div>'
)

    st.markdown(
        card_html,
        unsafe_allow_html=True
    )

    return st.file_uploader(
        label,
        type=file_types,
        help=help_text,
        key=uploader_key
    )

def render_metrics(
    student_count,
    template_status,
    font_status
):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {student_count}
                </div>
                <div class="metric-label">
                    Students detected
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {template_status}
                </div>
                <div class="metric-label">
                    Template
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {font_status}
                </div>
                <div class="metric-label">
                    Font
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_preview_header(longest_name):
    safe_name = html.escape(longest_name)

    preview_html = (
        '<div class="preview-header">'
        '<div>'
        '<div class="section-title">'
        'Certificate Preview'
        '</div>'
        '<div class="section-description">'
        'Showing the longest student name: '
        f'<strong>{safe_name}</strong>'
        '</div>'
        '</div>'
        '<div class="preview-badge">'
        'PREVIEW'
        '</div>'
        '</div>'
    )

    st.markdown(
        preview_html,
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            CertiFlow • V1 • Reusable PDF certificate generation
        </div>
        """,
        unsafe_allow_html=True
    )
