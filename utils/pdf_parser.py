# PDF and Document Parsing Utilities
"""
Extract text and images from PDFs for processing.
Handles both digital (text-based) and scanned (image-based) PDFs.
"""

import io
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile


def extract_text_from_pdf(pdf_path: Path) -> Tuple[str, bool]:
    """
    Extract text from PDF.
    Returns (text, is_digital) - is_digital is True if text was extractable.
    """
    try:
        import pypdf
        
        reader = pypdf.PdfReader(str(pdf_path))
        text_parts = []
        
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        
        full_text = "\n".join(text_parts)
        
        # Consider it digital if we got meaningful text
        is_digital = len(full_text.strip()) > 100
        
        return full_text, is_digital
        
    except ImportError:
        raise ImportError("pypdf not installed. Run: pip install pypdf")
    except Exception as e:
        return f"Error extracting text: {e}", False


def convert_pdf_to_images(pdf_path: Path, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Convert PDF pages to images for AI processing.
    Returns list of image paths.
    """
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="tma_pdf_"))
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import pdf2image
        
        images = pdf2image.convert_from_path(
            str(pdf_path),
            dpi=150,  # Balance quality vs size
            fmt="png"
        )
        
        paths = []
        for i, image in enumerate(images):
            path = output_dir / f"page_{i+1:03d}.png"
            image.save(str(path), "PNG")
            paths.append(path)
        
        return paths
        
    except ImportError:
        raise ImportError("pdf2image not installed. Run: pip install pdf2image")


def extract_text_from_excel(excel_path: Path) -> str:
    """Extract text representation from Excel file."""
    try:
        import pandas as pd
        
        # Read all sheets
        xlsx = pd.ExcelFile(str(excel_path))
        text_parts = []
        
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            text_parts.append(f"=== Sheet: {sheet_name} ===")
            text_parts.append(df.to_string())
        
        return "\n\n".join(text_parts)
        
    except ImportError:
        raise ImportError("pandas and openpyxl not installed. Run: pip install pandas openpyxl")


def detect_file_type(file_path: Path) -> str:
    """Detect file type from extension."""
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        return "pdf"
    elif suffix in [".xlsx", ".xls"]:
        return "excel"
    elif suffix in [".csv"]:
        return "csv"
    elif suffix in [".png", ".jpg", ".jpeg"]:
        return "image"
    else:
        return "unknown"
