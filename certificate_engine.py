import io
import re
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


APP_DIR = Path(__file__).resolve().parent
DEFAULT_FONT = APP_DIR / "fonts" / "CertificateScript.otf"


def find_placeholder_rect(
    template_bytes,
    placeholder
):
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

    doc.close()

    return placeholder_rect


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

    name_area = fitz.Rect(
        220,
        placeholder_rect.y0 - 12,
        page.rect.width - 220,
        placeholder_rect.y1 + 12
    )

    # Remove ONLY placeholder text.
    # Background images and graphics remain untouched.

    page.add_redact_annot(
        placeholder_rect,
        fill=None
    )

    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
        text=fitz.PDF_REDACT_TEXT_REMOVE
    )

    # Create transparent name image.

    scale = 4

    box_w = int(
        name_area.width * scale
    )

    box_h = int(
        name_area.height * scale
    )

    current_size = font_size

    font = None
    draw = None
    bbox = None
    test_img = None

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

    # Center name.

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


def safe_filename(
    name,
    number
):

    filename = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        name
    )

    filename = re.sub(
        r"\s+",
        "_",
        filename
    ).strip("._")

    if not filename:

        filename = f"Student_{number}"

    return f"Certificate_{filename}.pdf"
