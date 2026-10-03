# Certificator
a certificate generation software for clubs and companies where one uploads a certificate template and exl sheet and the software generates 1 certificate per name with given name.
A custom certificate automation tool.

**Input:**
- PDF certificate template
- Excel / CSV student list

**Output:**
- One personalized PDF certificate per student
- One ZIP containing all certificates

## Run it

```bash
pip install -r requirements.txt
# streamlit run app.py
python -m streamlit run app.py

```

## Using your Canva template

1. Design the certificate in Canva.
2. Put a selectable placeholder such as `<<Name>>` where the student name should appear.
3. Export the design as PDF.
4. Upload that PDF to this app.
5. Upload your Excel file.
6. Select the name column.
7. Click **Generate certificates**.

## Exact font support

For the best visual match, export/download the font used for the certificate as a `.ttf` or `.otf` file and upload it in the **Optional font** field.

If no font is uploaded, the project includes a bundled script-style fallback font.
