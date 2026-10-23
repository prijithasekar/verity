import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import docx
import pdfplumber
from PIL import Image
from app.services.deterministic_checker import DeterministicChecker

router = APIRouter(prefix="/parser", tags=["Multi-Format Document & Asset Parser"])

@router.post("/extract-text")
async def extract_text_from_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extracts text from DOCX, PDF, or Plain Text files.
    """
    filename = file.filename.lower()
    content_bytes = await file.read()

    extracted_text = ""
    file_type = "unknown"

    if filename.endswith(".docx"):
        file_type = "docx"
        try:
            doc = docx.Document(io.BytesIO(content_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            extracted_text = "\n\n".join(paragraphs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")

    elif filename.endswith(".pdf"):
        file_type = "pdf"
        try:
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                pages_text = []
                for p in pdf.pages:
                    txt = p.extract_text()
                    if txt:
                        pages_text.append(txt)
                extracted_text = "\n\n".join(pages_text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    elif filename.endswith(".txt") or filename.endswith(".md"):
        file_type = "text"
        extracted_text = content_bytes.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload DOCX, PDF, or TXT.")

    return {
        "filename": file.filename,
        "file_type": file_type,
        "character_count": len(extracted_text),
        "extracted_text": extracted_text
    }

@router.post("/inspect-image")
async def inspect_image_asset(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Inspects image file for dimensions, format, and calculates dominant color contrast.
    """
    try:
        content_bytes = await file.read()
        img = Image.open(io.BytesIO(content_bytes))
        width, height = img.size

        # Simple dominant color sampler (resize to 1x1 to get average color)
        img_small = img.convert("RGB").resize((1, 1))
        r, g, b = img_small.getpixel((0, 0))
        dominant_hex = f"#{r:02x}{g:02x}{b:02x}"

        # Test contrast against white background
        contrast_white = DeterministicChecker.calculate_contrast_ratio(dominant_hex, "#FFFFFF")
        contrast_black = DeterministicChecker.calculate_contrast_ratio(dominant_hex, "#000000")

        return {
            "filename": file.filename,
            "format": img.format,
            "dimensions": f"{width}x{height}",
            "dominant_hex": dominant_hex,
            "contrast_on_white": f"{contrast_white}:1",
            "contrast_on_black": f"{contrast_black}:1",
            "wcag_compliant_on_white": contrast_white >= 4.5
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to inspect image: {str(e)}")
