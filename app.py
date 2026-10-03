import io
import time
import zipfile

import pandas as pd
import streamlit as st

from certificate_engine import (
    find_placeholder_rect,
    get_font_path,
    create_certificate,
    render_pdf_preview,
    safe_filename,
)

from ui import (
    load_styles,
    render_header,
    render_hero,
    render_section_title,
    render_upload_card,
    render_metrics,
    render_preview_header,
    render_footer,
)

st.set_page_config(
    page_title="CertiFlow",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_styles()
render_header()
render_hero()


render_section_title(
    "Start with your files",
    "Upload the certificate design, student list, and optionally the matching font."
)

col1, col2 = st.columns(2)

with col1:
    template_file = render_upload_card(
        "Certificate template",
        "Upload the PDF certificate containing your <<Name>> placeholder.",
        "template",
        "Upload certificate PDF",
        ["pdf"],
        "The PDF should contain selectable text such as <<Name>>."
    )

with col2:
    excel_file = render_upload_card(
        "Student list",
        "Upload an Excel or CSV file containing the student names.",
        "students",
        "Upload Excel / CSV",
        ["xlsx", "xls", "csv"]
    )

font_file = st.file_uploader(
    "Optional: upload the exact certificate name font",
    type=["ttf", "otf"],
    help="Upload the exact font used in your certificate for the best visual match.",
    key="font"
)




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

        render_metrics(
            student_count=len(names),
            template_status="Ready",
            font_status="Custom" if font_file else "Default"
        )  

        # =====================================================
        # SETTINGS
        # =====================================================

        render_section_title(
            "Certificate settings",
            "Fine-tune how student names appear on the certificate."
        )

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

        placeholder_rect = find_placeholder_rect(
            template_bytes,
            placeholder
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
            
            longest_name = ""
            longest_length = 0
            total_names = len(names)

            search_box = st.empty()

            progress_bar = st.progress(
                0
            )

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
            render_preview_header(longest_name)

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

                        generated.append(
                            (
                                safe_filename(name, number),
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


render_footer()
