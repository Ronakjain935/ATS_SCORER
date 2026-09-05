import io
import logging

logger = logging.getLogger('ats_resume_scorer')

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_INSTALLED = True
except (ImportError, OSError, Exception):
    WEASYPRINT_INSTALLED = False

try:
    from xhtml2pdf import pisa
    from pypdf import PdfWriter, PdfReader
    XHTML2PDF_INSTALLED = True
except (ImportError, Exception):
    XHTML2PDF_INSTALLED = False


def _generate_pdf_weasyprint(html_docs: dict[str, str]) -> bytes:
    documents = []
    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()
        documents.append(doc)

    first_doc = documents[0]
    for other_doc in documents[1:]:
        for page in other_doc.pages:
            first_doc.pages.append(page)

    return first_doc.write_pdf()


def _generate_pdf_xhtml2pdf(html_docs: dict[str, str]) -> bytes:
    writer = PdfWriter()
    for name, html_str in html_docs.items():
        pdf_stream = io.BytesIO()
        pisa_status = pisa.CreatePDF(src=html_str, dest=pdf_stream)
        if pisa_status.err:
            logger.warning(f"xhtml2pdf warning while rendering section {name}")
        pdf_stream.seek(0)
        reader = PdfReader(pdf_stream)
        for page in reader.pages:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    """
    Generates a merged PDF from HTML documents.
    Tries WeasyPrint first; falls back to xhtml2pdf if GTK/Cairo libraries are missing.
    """
    if not html_docs:
        raise ValueError("No HTML documents provided for PDF generation.")

    if WEASYPRINT_INSTALLED:
        try:
            return _generate_pdf_weasyprint(html_docs)
        except Exception as e:
            logger.warning(f"WeasyPrint PDF rendering failed ({e}). Falling back to xhtml2pdf...")

    if XHTML2PDF_INSTALLED:
        return _generate_pdf_xhtml2pdf(html_docs)

    raise ImportError("No PDF engine available. Please install xhtml2pdf or configure WeasyPrint dependencies.")
