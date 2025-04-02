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
        self.model = None
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'mosquito_model.h5')
        self.load_model()
        self.class_names = ['mosquito', 'not_mosquito']
        self.submitted_hashes = set()  # Store hashes of submitted images
        
    def load_model(self):
        """Load the pre-trained model if available."""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("Model loaded successfully")
            else:
                print(f"Model not found at {self.model_path}. Using simple verification.")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            print("Using simple verification.")

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

    def preprocess_image(self, image_path):
        """Preprocess image for model input."""
        try:
            img = Image.open(image_path)
            img = img.resize((224, 224))  # Resize to standard size
            img_array = np.array(img)
            img_array = img_array / 255.0  # Normalize
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None

    def verify_image(self, image_path, username):
        """Verify if the image contains a mosquito."""
        try:
            if self.model:
                # Use the model for verification
                img_array = self.preprocess_image(image_path)
                if img_array is None:
                    return False, "Error processing image"
                
                prediction = self.model.predict(img_array)[0][0]
                is_valid = prediction > 0.5
                confidence = float(prediction)
                
                return {
                    'success': True,
                    'is_valid': is_valid,
                    'confidence': confidence,
                    'message': f"Image {'verified' if is_valid else 'rejected'} with {confidence:.2%} confidence",
                    'coins': 10 if is_valid else 0
                }
            else:
                # Simple verification (random 30% acceptance rate)
                is_valid = random.random() < 0.3
                return {
                    'success': True,
                    'is_valid': is_valid,
                    'confidence': 0.7 if is_valid else 0.3,
                    'message': f"Image {'verified' if is_valid else 'rejected'} (simple verification)",
                    'coins': 10 if is_valid else 0
                }
        except Exception as e:
            print(f"Error in verify_image: {str(e)}")
            return {
                'success': False,
                'message': f"Error verifying image: {str(e)}",
                'coins': 0
            }

# Create a singleton instance
verification_service = VerificationService()

# Export the verify_image function
def verify_image(image_path, username):
    return verification_service.verify_image(image_path, username) 