import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import random
import hashlib
from datetime import datetime, timedelta

class VerificationService:
    def __init__(self):
        self.model = self._load_model()
        self.class_names = ['mosquito', 'not_mosquito']
        self.submitted_hashes = set()  # Store hashes of submitted images
        
    def _load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'mosquito_model.h5')
            if os.path.exists(model_path):
                return tf.keras.models.load_model(model_path)
            else:
                print(f"Model not found at {model_path}. Using simple verification.")
                return None
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None

    def _check_image_content(self, image):
        """Basic image validation"""
        try:
            # Convert to grayscale for analysis
            gray_img = image.convert('L')
            gray_array = np.array(gray_img)
            
            # Calculate image statistics
            mean_brightness = np.mean(gray_array)
            std_brightness = np.std(gray_array)
            
            # Check if image is too bright/dark or low contrast
            if mean_brightness > 240 or mean_brightness < 15:
                return False, "Image is too bright or too dark"
            if std_brightness < 5:  # Reduced contrast requirement
                return False, "Image has too little contrast"
                
            return True, "Image validation passed"
        except Exception as e:
            return False, f"Image validation failed: {str(e)}"

    def _calculate_image_hash(self, image_path):
        """Calculate MD5 hash of image file"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error calculating image hash: {str(e)}")
            return None

    def _check_duplicate(self, image_hash):
        """Check if image has been submitted before"""
        return image_hash in self.submitted_hashes

    def preprocess_image(self, image):
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Keep original aspect ratio while resizing
            aspect = image.width / image.height
            if aspect > 1:
                new_width = 224
                new_height = int(224 / aspect)
            else:
                new_height = 224
                new_width = int(224 * aspect)
                
            image = image.resize((new_width, new_height))
            
            # Create new image with padding to 224x224
            new_image = Image.new('RGB', (224, 224), (255, 255, 255))
            offset_x = (224 - new_width) // 2
            offset_y = (224 - new_height) // 2
            new_image.paste(image, (offset_x, offset_y))
            
            # Convert to array and normalize
            img_array = np.array(new_image) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None

    def verify_image(self, image_path, username):
        try:
            # Calculate image hash
            image_hash = self._calculate_image_hash(image_path)
            if image_hash is None:
                return {
                    'success': False,
                    'message': 'Failed to process image',
                    'error': 'PROCESSING_ERROR'
                }

            # Check for duplicate submission
            if self._check_duplicate(image_hash):
                return {
                    'success': False,
                    'message': 'This image has already been submitted',
                    'error': 'DUPLICATE_IMAGE'
                }

            # Load and validate the image
            image = Image.open(image_path)
            
            # Basic content check
            is_valid, message = self._check_image_content(image)
            if not is_valid:
                return {
                    'success': False,
                    'message': message,
                    'error': 'INVALID_IMAGE'
                }

            processed_image = self.preprocess_image(image)
            if processed_image is None:
                return {
                    'success': False,
                    'message': 'Failed to process image',
                    'error': 'PROCESSING_ERROR'
                }

            # Analyze image features
            gray_img = image.convert('L')
            gray_array = np.array(gray_img)
            
            # Calculate image features
            mean_brightness = np.mean(gray_array)
            std_brightness = np.std(gray_array)
            
            # Calculate dark areas (potential mosquito body)
            threshold = mean_brightness - std_brightness
            dark_pixels = np.sum(gray_array < threshold)
            dark_ratio = dark_pixels / gray_array.size
            
            # Check for mosquito-like characteristics
            if 0.01 <= dark_ratio <= 0.2 and 30 <= std_brightness <= 100:
                # Add hash to submitted images
                self.submitted_hashes.add(image_hash)
                
                return {
                    'success': True,
                    'message': 'Image accepted successfully!',
                    'coins': 1,
                    'confidence': 1.0
                }
            else:
                return {
                    'success': False,
                    'message': 'Not a valid mosquito image. Please try another image.',
                    'error': 'INVALID_IMAGE',
                    'confidence': 0.0
                }

        except Exception as e:
            print(f"Error verifying image: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to verify image',
                'error': 'VERIFICATION_ERROR',
                'details': str(e)
            }

# Global verification service instance
verification_service = VerificationService() 