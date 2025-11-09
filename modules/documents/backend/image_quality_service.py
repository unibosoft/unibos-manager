"""
Image Quality Assessment and Preprocessing Service
Evaluates image quality and applies preprocessing for optimal OCR results
Based on GPT architecture recommendations
"""

import logging
import numpy as np
from typing import Dict, Tuple, Optional
from PIL import Image
import io
import base64

logger = logging.getLogger('documents.image_quality')


class ImageQualityService:
    """
    Service for image quality assessment and preprocessing
    Determines optimal OCR method based on image characteristics
    """

    # Quality thresholds
    BLUR_THRESHOLD_HIGH = 100  # Above this = high quality
    BLUR_THRESHOLD_LOW = 30    # Below this = low quality
    CONTRAST_THRESHOLD_LOW = 30  # Below this = poor contrast
    MIN_DPI_HIGH_QUALITY = 200
    MIN_DPI_MEDIUM_QUALITY = 150

    def __init__(self):
        """Initialize the image quality service"""
        self.cv2_available = False
        try:
            import cv2
            self.cv2 = cv2
            self.cv2_available = True
            logger.info("OpenCV available for advanced image processing")
        except ImportError:
            logger.warning("OpenCV not available. Install with: pip install opencv-python")

    def assess_quality(self, image_path: str) -> Dict:
        """
        Assess image quality and recommend OCR method

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with quality metrics and OCR recommendation
        """
        try:
            # Load image
            img = Image.open(image_path)

            # Calculate metrics
            blur_score = self._calculate_blur(image_path)
            contrast_score = self._calculate_contrast(img)
            dpi = self._estimate_dpi(img)
            orientation = self._detect_orientation(image_path)

            # Determine quality level
            if blur_score >= self.BLUR_THRESHOLD_HIGH and dpi >= self.MIN_DPI_HIGH_QUALITY:
                quality_level = 'high'
                recommended_ocr = 'tesseract'
            elif blur_score >= self.BLUR_THRESHOLD_LOW and dpi >= self.MIN_DPI_MEDIUM_QUALITY:
                quality_level = 'medium'
                recommended_ocr = 'paddleocr'
            else:
                quality_level = 'low'
                recommended_ocr = 'vision'  # Use vision model for poor quality

            # Check if preprocessing is needed
            needs_deskew = orientation != 0
            needs_contrast_enhancement = contrast_score < self.CONTRAST_THRESHOLD_LOW
            needs_denoising = blur_score < self.BLUR_THRESHOLD_LOW

            return {
                'success': True,
                'quality_level': quality_level,
                'blur_score': blur_score,
                'contrast_score': contrast_score,
                'dpi': dpi,
                'orientation': orientation,
                'recommended_ocr': recommended_ocr,
                'preprocessing_needed': {
                    'deskew': needs_deskew,
                    'contrast_enhancement': needs_contrast_enhancement,
                    'denoising': needs_denoising
                }
            }

        except Exception as e:
            logger.error(f"Quality assessment error: {e}")
            return {
                'success': False,
                'error': str(e),
                'quality_level': 'unknown',
                'recommended_ocr': 'paddleocr'  # Default fallback
            }

    def preprocess_image(self, image_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Apply preprocessing to improve OCR results

        Args:
            image_path: Path to input image
            output_path: Path to save preprocessed image (optional)

        Returns:
            Dictionary with preprocessing results and processed image path
        """
        if not self.cv2_available:
            return {
                'success': False,
                'error': 'OpenCV not available for preprocessing'
            }

        try:
            # Assess quality first
            quality = self.assess_quality(image_path)

            if not quality['success']:
                return quality

            # Load image with OpenCV
            img = self.cv2.imread(image_path)

            if img is None:
                return {
                    'success': False,
                    'error': 'Failed to load image with OpenCV'
                }

            original_img = img.copy()
            preprocessing_applied = []

            # Apply preprocessing based on quality assessment
            needs = quality['preprocessing_needed']

            # 1. Deskew (if needed)
            if needs['deskew'] and quality['orientation'] != 0:
                img = self._deskew_image(img, quality['orientation'])
                preprocessing_applied.append('deskew')
                logger.info(f"Applied deskew: {quality['orientation']} degrees")

            # 2. Contrast enhancement (if needed)
            if needs['contrast_enhancement']:
                img = self._enhance_contrast(img)
                preprocessing_applied.append('contrast_enhancement')
                logger.info("Applied contrast enhancement")

            # 3. Denoising (if needed)
            if needs['denoising']:
                img = self._denoise_image(img)
                preprocessing_applied.append('denoising')
                logger.info("Applied denoising")

            # 4. Adaptive threshold for better text extraction
            img = self._adaptive_threshold(img)
            preprocessing_applied.append('adaptive_threshold')

            # Save preprocessed image
            if output_path:
                self.cv2.imwrite(output_path, img)
                result_path = output_path
            else:
                # Save to temporary file
                import tempfile
                import os
                temp_dir = tempfile.gettempdir()
                temp_filename = f"preprocessed_{os.path.basename(image_path)}"
                result_path = os.path.join(temp_dir, temp_filename)
                self.cv2.imwrite(result_path, img)

            return {
                'success': True,
                'original_path': image_path,
                'preprocessed_path': result_path,
                'preprocessing_applied': preprocessing_applied,
                'quality_assessment': quality
            }

        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_blur(self, image_path: str) -> float:
        """
        Calculate blur score using Laplacian variance
        Higher score = sharper image

        Args:
            image_path: Path to image file

        Returns:
            Blur score (0-500+, higher is better)
        """
        if not self.cv2_available:
            return 100.0  # Default medium score

        try:
            img = self.cv2.imread(image_path, self.cv2.IMREAD_GRAYSCALE)
            if img is None:
                return 100.0

            # Calculate Laplacian variance
            laplacian = self.cv2.Laplacian(img, self.cv2.CV_64F)
            blur_score = laplacian.var()

            logger.debug(f"Blur score: {blur_score:.2f}")
            return blur_score

        except Exception as e:
            logger.error(f"Blur calculation error: {e}")
            return 100.0

    def _calculate_contrast(self, img: Image.Image) -> float:
        """
        Calculate image contrast using standard deviation

        Args:
            img: PIL Image

        Returns:
            Contrast score (0-100+)
        """
        try:
            # Convert to grayscale
            if img.mode != 'L':
                img = img.convert('L')

            # Convert to numpy array
            img_array = np.array(img)

            # Calculate standard deviation (contrast measure)
            contrast = float(np.std(img_array))

            logger.debug(f"Contrast score: {contrast:.2f}")
            return contrast

        except Exception as e:
            logger.error(f"Contrast calculation error: {e}")
            return 50.0  # Default medium contrast

    def _estimate_dpi(self, img: Image.Image) -> int:
        """
        Estimate DPI from image metadata or dimensions

        Args:
            img: PIL Image

        Returns:
            Estimated DPI
        """
        try:
            # Try to get DPI from image metadata
            dpi = img.info.get('dpi', None)

            if dpi:
                # DPI is a tuple (x_dpi, y_dpi)
                return int(dpi[0])

            # Estimate from dimensions (assume standard paper size)
            width, height = img.size

            # Assume A4 paper (8.27 x 11.69 inches)
            # If width ~= 8.27 inches, calculate DPI
            if width > height:
                # Landscape
                estimated_dpi = int(width / 11.69)
            else:
                # Portrait
                estimated_dpi = int(width / 8.27)

            logger.debug(f"Estimated DPI: {estimated_dpi}")
            return estimated_dpi

        except Exception as e:
            logger.error(f"DPI estimation error: {e}")
            return 150  # Default medium DPI

    def _detect_orientation(self, image_path: str) -> int:
        """
        Detect image orientation (0, 90, 180, 270 degrees)

        Args:
            image_path: Path to image file

        Returns:
            Orientation in degrees (0, 90, 180, 270)
        """
        # For now, return 0 (no rotation)
        # TODO: Implement using Tesseract OSD or custom algorithm
        return 0

    def _deskew_image(self, img, angle: int):
        """
        Rotate image to correct orientation

        Args:
            img: OpenCV image
            angle: Rotation angle in degrees

        Returns:
            Rotated image
        """
        if angle == 0:
            return img

        try:
            height, width = img.shape[:2]
            center = (width // 2, height // 2)

            # Get rotation matrix
            M = self.cv2.getRotationMatrix2D(center, -angle, 1.0)

            # Apply rotation
            rotated = self.cv2.warpAffine(img, M, (width, height),
                                          flags=self.cv2.INTER_CUBIC,
                                          borderMode=self.cv2.BORDER_REPLICATE)

            return rotated

        except Exception as e:
            logger.error(f"Deskew error: {e}")
            return img

    def _enhance_contrast(self, img):
        """
        Enhance image contrast using CLAHE

        Args:
            img: OpenCV image

        Returns:
            Contrast-enhanced image
        """
        try:
            # Convert to LAB color space
            lab = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2LAB)

            # Split channels
            l, a, b = self.cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = self.cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge channels
            lab = self.cv2.merge([l, a, b])

            # Convert back to BGR
            enhanced = self.cv2.cvtColor(lab, self.cv2.COLOR_LAB2BGR)

            return enhanced

        except Exception as e:
            logger.error(f"Contrast enhancement error: {e}")
            return img

    def _denoise_image(self, img):
        """
        Remove noise from image

        Args:
            img: OpenCV image

        Returns:
            Denoised image
        """
        try:
            # Apply Non-Local Means Denoising
            denoised = self.cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            return denoised

        except Exception as e:
            logger.error(f"Denoising error: {e}")
            return img

    def _adaptive_threshold(self, img):
        """
        Apply adaptive thresholding for better text extraction

        Args:
            img: OpenCV image

        Returns:
            Thresholded image
        """
        try:
            # Convert to grayscale
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

            # Apply adaptive threshold
            thresh = self.cv2.adaptiveThreshold(
                gray, 255,
                self.cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                self.cv2.THRESH_BINARY,
                11, 2
            )

            # Convert back to BGR for consistency
            result = self.cv2.cvtColor(thresh, self.cv2.COLOR_GRAY2BGR)

            return result

        except Exception as e:
            logger.error(f"Adaptive threshold error: {e}")
            return img
