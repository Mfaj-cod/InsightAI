import io
import os
from pathlib import Path

try:
    import cv2
except Exception:
    cv2 = None

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception:
    pytesseract = None

try:
    from PIL import Image
except Exception:
    Image = None

# PDF handling
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

# Optional: Google Vision
try:
    from google.cloud import vision
    _GCV_AVAILABLE = True
except Exception:
    vision = None
    _GCV_AVAILABLE = False


#  PDF extraction
def _extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    if PdfReader is None:
        raise RuntimeError("PyPDF2 is not installed. Install it to process PDFs.")

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


#  Image preprocessing 
def _opencv_preprocess(image_path: str) -> bytes:
    # Load image, deskew, denoise, and return bytes suitable for OCR.
    if cv2 is None:
        with open(image_path, "rb") as f:
            return f.read()

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # resizing small images
    h, w = gray.shape
    if max(h, w) < 1000:
        scale = 1000 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # denoising
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # deskew
    coords = cv2.findNonZero(255 - thresh)
    if coords is not None:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.1:
            (h, w) = thresh.shape
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # encoding to PNG bytes
    is_success, buffer = cv2.imencode('.png', thresh)
    if not is_success:
        raise RuntimeError("Failed to encode preprocessed image")
    return buffer.tobytes()


# OCR (image only)
def _ocr_image_to_text(image_path: str, use_gvision: bool = False) -> str:
    # Runs OCR on an image using Google Vision or pytesseract.

    if use_gvision and _GCV_AVAILABLE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        client = vision.ImageAnnotatorClient()
        with open(image_path, 'rb') as f:
            content = f.read()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        if response.error.message:
            raise RuntimeError(f"Google Vision error: {response.error.message}")
        return response.full_text_annotation.text

    # Otherwise pytesseract
    preprocessed = _opencv_preprocess(image_path)
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed. Install pytesseract for OCR.")

    try:
        image = Image.open(io.BytesIO(preprocessed))
        return pytesseract.image_to_string(image, lang='eng')
    except Exception:
        # fallback: writing file and calling tesseract CLI
        tmp = image_path + ".preproc.png"
        with open(tmp, 'wb') as f:
            f.write(preprocessed)
        text = pytesseract.image_to_string(tmp, lang='eng', config='--psm 6')
        try:
            os.remove(tmp)
        except Exception:
            pass
        return text


# unified entrypoint
def file_to_text(file_path: str, use_gvision: bool = False) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(file_path)
    else:
        return _ocr_image_to_text(file_path, use_gvision=use_gvision)
