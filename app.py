import io
import re
import time
import zipfile
from pathlib import Path

import fitz
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


APP_DIR = Path(__file__).resolve().parent
DEFAULT_FONT = APP_DIR / "fonts" / "CertificateScript.otf"


st.set_page_config(
    page_title="Certificate Generator",
    page_icon="🏆",
    layout="centered",
)


st.title("🏆 Certificate Generator")
st.caption("PDF certificate template + Excel/CSV → individual PDF certificates")

st.divider()


template_file = st.file_uploader(
    "1. Upload certificate PDF template",
    type=["pdf"],
    help="The PDF should contain a selectable placeholder such as <<Name>>.",
)


excel_file = st.file_uploader(
    "2. Upload student Excel / CSV",
    type=["xlsx", "xls", "csv"],
)


font_file = st.file_uploader(
    "Optional: upload the exact certificate name font",
    type=["ttf", "otf"],
    help="Upload the exact font used in your certificate for the best visual match.",
)


def find_placeholder_rect(template_bytes, placeholder):
    doc = fitz.open(
        stream=template_bytes,
        filetype="pdf"
    )

    page = doc[0]
    placeholder_rect = None

    for block in page.get_text("dict").get("blocks", []):

        for line in block.get("lines", []):

            for span in line.get("spans", []):

                span_text = span.get("text", "")

                if placeholder in span_text:

                    placeholder_rect = fitz.Rect(
                        span["bbox"]
                    )

                    break

            if placeholder_rect:
                break

        if placeholder_rect:
            break

    page_width = page.rect.width
    page_height = page.rect.height

    doc.close()

    return placeholder_rect, page_width, page_height


def get_font_path(font_file):
    if font_file:

        font_path = Path(
            "/tmp/certificate_custom_font"
        )

        font_path.write_bytes(
            font_file.getvalue()
        )

        return font_path

    if DEFAULT_FONT.exists():
        return DEFAULT_FONT

    return None


def create_certificate(
    template_bytes,
    placeholder_rect,
    name,
    font_path,
    font_size,
    max_width
):
    doc = fitz.open(
        stream=template_bytes,
        filetype="pdf"
    )

    page = doc[0]

    # ---------------------------------------------------------
    # NAME AREA
    # ---------------------------------------------------------

    name_area = fitz.Rect(
        220,
        placeholder_rect.y0 - 12,
        page.rect.width - 220,
        placeholder_rect.y1 + 12
    )

    # ---------------------------------------------------------
    # REMOVE ONLY PLACEHOLDER TEXT
    # ---------------------------------------------------------

    page.add_redact_annot(
        placeholder_rect,
        fill=None
    )

    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
        text=fitz.PDF_REDACT_TEXT_REMOVE
    )

    # ---------------------------------------------------------
    # CREATE TRANSPARENT NAME IMAGE
    # ---------------------------------------------------------

    scale = 4

    box_w = int(
        name_area.width * scale
    )

    box_h = int(
        name_area.height * scale
    )

    current_size = font_size

    while current_size >= 24:

        font = ImageFont.truetype(
            str(font_path),
            int(current_size * scale)
        )

        test_img = Image.new(
            "RGBA",
            (box_w, box_h),
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(
            test_img
        )

        bbox = draw.textbbox(
            (0, 0),
            name,
            font=font
        )

        text_w = (
            bbox[2] - bbox[0]
        )

        if text_w <= max_width * scale:
            break

        current_size -= 2

    # ---------------------------------------------------------
    # CENTER NAME
    # ---------------------------------------------------------

    bbox = draw.textbbox(
        (0, 0),
        name,
        font=font
    )

    text_w = (
        bbox[2] - bbox[0]
    )

    text_h = (
        bbox[3] - bbox[1]
    )

    x = (
        box_w - text_w
    ) / 2 - bbox[0]

    y = (
        box_h - text_h
    ) / 2 - bbox[1]

    draw.text(
        (x, y),
        name,
        font=font,
        fill=(0, 0, 0, 255)
    )

    # ---------------------------------------------------------
    # INSERT NAME
    # ---------------------------------------------------------

    png = io.BytesIO()

    test_img.save(
        png,
        format="PNG"
    )

    png.seek(0)

    page.insert_image(
        name_area,
        stream=png.getvalue(),
        keep_proportion=False,
        overlay=True
    )

    # ---------------------------------------------------------
    # SAVE PDF
    # ---------------------------------------------------------

    output = io.BytesIO()

    doc.save(
        output,
        garbage=4,
        deflate=True
    )

    doc.close()

    return output.getvalue()


def render_pdf_preview(pdf_bytes):
    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    page = doc[0]

    pix = page.get_pixmap(
        matrix=fitz.Matrix(1.5, 1.5),
        alpha=False
    )

    image = Image.open(
        io.BytesIO(
            pix.tobytes("png")
        )
    )

    doc.close()

    return image


if template_file and excel_file:

    try:

        # =====================================================
        # READ EXCEL
        # =====================================================

        if excel_file.name.lower().endswith(".csv"):

            df = pd.read_csv(
                excel_file
            )

        else:

            df = pd.read_excel(
                excel_file
            )

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        st.subheader("Student data")

        st.dataframe(
            df.head(8),
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
        # FIND NAME COLUMN
        # =====================================================

        name_candidates = [
            c
            for c in df.columns
            if str(c).strip().lower()
            in {
                "name",
                "student name",
                "student_name",
                "full name",
                "full_name",
            }
        ]

        default_index = (
            df.columns.get_loc(
                name_candidates[0]
            )
            if name_candidates
            else 0
        )

        name_column = st.selectbox(
            "Which column contains the student names?",
            list(df.columns),
            index=default_index,
        )

        names = (
            df[name_column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        names = [
            name
            for name in names.tolist()
            if name
        ]

        st.info(
            f"Found **{len(names)}** student names."
        )

        # =====================================================
        # SETTINGS
        # =====================================================

        st.subheader("Certificate settings")

        placeholder = st.text_input(
            "Name placeholder",
            value="<<Name>>"
        )

        font_size = st.slider(
            "Name font size",
            30,
            90,
            65
        )

        max_width = st.slider(
            "Maximum name width",
            400,
            850,
            700,
            help="Long names automatically shrink until they fit."
        )

        # =====================================================
        # PREPARE TEMPLATE
        # =====================================================

        template_bytes = template_file.getvalue()

        placeholder_rect, page_width, page_height = (
            find_placeholder_rect(
                template_bytes,
                placeholder
            )
        )

        if placeholder_rect is None:

            st.error(
                f"Could not find `{placeholder}` in the PDF. "
                "Make sure the placeholder is selectable text."
            )

            st.stop()

        font_path = get_font_path(
            font_file
        )

        if font_path is None:

            st.error(
                "No usable font is available."
            )

            st.stop()

        # =====================================================
        # FIND LONGEST NAME
        # =====================================================

        if names:

            st.subheader("👀 Certificate preview")

            search_box = st.empty()

            progress_bar = st.progress(
                0
            )

            longest_name = ""

            longest_length = 0

            total_names = len(names)

            for index, current_name in enumerate(
                names,
                start=1
            ):

                search_box.markdown(
                    f"🔎 **Finding longest name...**  \n"
                    f"Checking **{index} / {total_names}**: "
                    f"`{current_name}`"
                )

                if len(current_name) > longest_length:

                    longest_name = current_name
                    longest_length = len(current_name)

                progress_bar.progress(
                    index / total_names
                )

                time.sleep(0.035)

            search_box.success(
                f"✅ Longest name found: **{longest_name}** "
                f"({len(longest_name)} characters)"
            )

            progress_bar.empty()

            # =================================================
            # GENERATE PREVIEW
            # =================================================

            preview_pdf = create_certificate(
                template_bytes=template_bytes,
                placeholder_rect=placeholder_rect,
                name=longest_name,
                font_path=font_path,
                font_size=font_size,
                max_width=max_width
            )

            preview_image = render_pdf_preview(
                preview_pdf
            )

            st.image(
                preview_image,
                use_container_width=True
            )

            st.caption(
                f"Preview uses the longest student name: "
                f"**{longest_name}**"
            )

            st.divider()

            # =================================================
            # GENERATE BUTTON
            # =================================================

            generate = st.button(
                "🚀 Generate certificates",
                type="primary",
                use_container_width=True
            )

            # =================================================
            # GENERATE ALL
            # =================================================

            if generate:

                with st.spinner(
                    "Generating certificates..."
                ):

                    generated = []

                    for number, raw_name in enumerate(
                        names,
                        start=1
                    ):

                        name = raw_name.strip()

                        pdf_bytes = create_certificate(
                            template_bytes=template_bytes,
                            placeholder_rect=placeholder_rect,
                            name=name,
                            font_path=font_path,
                            font_size=font_size,
                            max_width=max_width
                        )

                        # -------------------------------------
                        # SAFE FILE NAME
                        # -------------------------------------

                        safe_name = re.sub(
                            r'[<>:"/\\|?*\x00-\x1f]',
                            "_",
                            name
                        )

                        safe_name = re.sub(
                            r"\s+",
                            "_",
                            safe_name
                        ).strip("._")

                        if not safe_name:

                            safe_name = (
                                f"Student_{number}"
                            )

                        generated.append(
                            (
                                f"Certificate_{safe_name}.pdf",
                                pdf_bytes
                            )
                        )

                # =================================================
                # CREATE ZIP
                # =================================================

                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(
                    zip_buffer,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as zf:

                    for filename, content in generated:

                        zf.writestr(
                            filename,
                            content
                        )

                # =================================================
                # SUCCESS
                # =================================================

                st.success(
                    f"Done! Generated **{len(generated)} certificates**."
                )

                st.download_button(
                    "📦 Download all certificates (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="certificates.zip",
                    mime="application/zip",
                    use_container_width=True
                )

                st.download_button(
                    "📄 Download first certificate (PDF)",
                    data=generated[0][1],
                    file_name=generated[0][0],
                    mime="application/pdf",
                    use_container_width=True
                )

                with st.expander(
                    "Generated files"
                ):

                    for filename, _ in generated:

                        st.write(
                            "✓",
                            filename
                        )

    except Exception as exc:

        st.error(
            f"Something went wrong: {exc}"
        )


st.divider()

st.caption(
    "V1 • Built for reusable PDF certificate generation"
)
