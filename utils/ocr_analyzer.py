"""
OCR Analysis Utilities
"""

import cv2
import numpy as np
from typing import Dict, Any, List
from pathlib import Path


class OCRAnalyzer:
    """OCR analyzer for Chinese text detection and metrics extraction"""
    
    def __init__(self):
        """Initialize EasyOCR reader"""
        import easyocr
        print("🔧 Initializing EasyOCR (Chinese + English)...")
        self.reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    
    def analyze_image(self, image_path: Path, verbose: bool = True) -> Dict[str, Any]:
        """
        Analyze image with OCR
        
        Args:
            image_path: Path to image file
            verbose: Print detected text
        
        Returns:
            Dictionary with metrics
        """
        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            return self._empty_metrics()
        
        # OCR analysis
        results = self.reader.readtext(str(image_path))
        
        if not results:
            if verbose:
                print("  ⚠️  No text detected!")
            return self._empty_metrics()
        
        # Extract metrics
        metrics = {
            'texts': [],
            'confidences': [],
            'avg_confidence': 0,
            'positions': [],
            'bbox_sizes': [],
            'text_detected': True,
            'image_height': img.shape[0],
            'image_width': img.shape[1]
        }
        
        total_confidence = 0
        for bbox, text, confidence in results:
            if verbose:
                print(f"  📝 '{text}' (confidence: {confidence:.2%})")
            
            metrics['texts'].append(text)
            metrics['confidences'].append(confidence)
            metrics['positions'].append(bbox)
            
            # Calculate text bounding box size
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            metrics['bbox_sizes'].append((width, height))
            
            total_confidence += confidence
        
        # Calculate averages
        metrics['avg_confidence'] = total_confidence / len(results)
        
        # Calculate vertical position (percentage from top)
        avg_y_positions = []
        for bbox in metrics['positions']:
            y_coords = [point[1] for point in bbox]
            avg_y = sum(y_coords) / len(y_coords)
            avg_y_positions.append(avg_y / img.shape[0])
        
        metrics['avg_y_position'] = sum(avg_y_positions) / len(avg_y_positions)
        
        # Estimate font size from bounding box height
        if metrics['bbox_sizes']:
            avg_height = sum([h for w, h in metrics['bbox_sizes']]) / len(metrics['bbox_sizes'])
            metrics['estimated_font_size'] = int(avg_height * 0.8)
        
        return metrics
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'texts': [],
            'confidences': [],
            'avg_confidence': 0,
            'positions': [],
            'bbox_sizes': [],
            'text_detected': False
        }
