import os
from PIL import Image
import numpy as np
import requests
from io import BytesIO
from app.storage import storage
from datetime import datetime
import tensorflow as tf
from pathlib import Path

# Load the pre-trained model
model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=True)

# Store image hashes in memory
image_hashes = {}

def compute_image_hash(image):
    """Compute a simple perceptual hash of the image using average pixel values."""
    # Convert to grayscale and resize to 8x8
    img_gray = image.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
    # Convert to numpy array
    pixels = np.array(img_gray)
    # Compute average pixel value
    avg_pixel = pixels.mean()
    # Convert to binary hash string
    hash_str = ''.join(['1' if pixel > avg_pixel else '0' for pixel in pixels.flatten()])
    return hash_str

def is_similar_image(current_hash, threshold=5):
    """Check if an image with similar hash exists."""
    for stored_hash in image_hashes.values():
        if isinstance(stored_hash, str):
            # Calculate Hamming distance
            if len(stored_hash) == len(current_hash):
                distance = sum(c1 != c2 for c1, c2 in zip(stored_hash, current_hash))
                if distance < threshold:
                    return True
    return False

def preprocess_image(image):
    """Preprocess the image for the model."""
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to 224x224 (MobileNetV2 input size)
        image = image.resize((224, 224))
        
        # Convert to numpy array and preprocess
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        return None

def verify_image(image_path):
    """Verify if the image contains a mosquito."""
    try:
        # Open and preprocess the image
        img = Image.open(image_path)
        img_array = preprocess_image(img)
        
        if img_array is None:
            return {
                'success': False,
                'message': 'Invalid or corrupted image'
            }
        
        # Compute image hash
        img_hash = compute_image_hash(img)
        
        # Check for similar images
        if is_similar_image(img_hash):
            return {
                'success': False,
                'message': 'This appears to be the same mosquito from a different angle. Please submit a new mosquito image.'
            }
        
        # Get predictions from the model
        predictions = model.predict(img_array)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=10)[0]
        
        # Print predictions for debugging
        print("Model predictions:", decoded_predictions)
        
        # Expanded list of insect-related classes and similar objects
        insect_related_classes = [
            'mosquito', 'insect', 'bug', 'fly', 'beetle', 'arthropod', 
            'invertebrate', 'spider', 'ant', 'bee', 'wasp', 'moth', 
            'butterfly', 'dragonfly', 'cricket', 'grasshopper',
            # Add more general terms that might indicate a small insect
            'dot', 'spot', 'mark', 'speck', 'point', 'dark_spot',
            'creature', 'animal', 'small', 'tiny', 'black', 'wing',
            # Add some similar looking objects
            'nail', 'pin', 'tack', 'dot', 'spot', 'mark'
        ]
        
        # Check for any insect-related predictions with a lower confidence threshold
        found_potential_insect = False
        max_confidence = 0.0
        
        for pred in decoded_predictions:
            class_name = pred[1].lower().replace('_', ' ')
            confidence = pred[2]
            
            # Check if any part of the class name matches our insect classes
            # or if it's a small dark object (potential insect)
            words = class_name.split()
            for word in words:
                if word in insect_related_classes:
                    found_potential_insect = True
                    max_confidence = max(max_confidence, confidence)
                    break
        
        # If we found any potential insect or small object
        if found_potential_insect:
            # Check image quality with very lenient thresholds
            img_array = np.array(img)
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Very relaxed quality thresholds
            if brightness < 20 or contrast < 10:  # Even lower thresholds
                return {
                    'success': False,
                    'message': 'Image is too dark or blurry. Please retake with better lighting.'
                }
            
            # Store the hash for future comparisons
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_hashes[f"{timestamp}_{Path(image_path).name}"] = img_hash
            
            return {
                'success': True,
                'message': 'Insect detected and verified! Coins awarded.',
                'coins_earned': 10,
                'confidence': max_confidence
            }
        
        # If no insect detected, check image quality
        img_array = np.array(img)
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        if brightness < 20:
            return {
                'success': False,
                'message': 'Image is too dark. Please retake with better lighting.'
            }
        elif contrast < 10:
            return {
                'success': False,
                'message': 'Image is blurry. Please retake with better focus.'
            }
        else:
            return {
                'success': False,
                'message': 'Could not detect an insect. Please ensure the mosquito is clearly visible and centered in the image.'
            }
            
    except Exception as e:
        print(f"Error verifying image: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }

def verify_mosquito_image(image_id):
    """Verify a mosquito image from storage."""
    image = storage.get_image(image_id)
    if not image:
        return
    
    try:
        # Download image from S3
        response = requests.get(image['image_url'])
        img = Image.open(BytesIO(response.content))
        
        # Verify the image
        result = verify_image(img)
        
        if result['success']:
            storage.update_image(
                image_id,
                verification_status='verified',
                feedback=result['message'],
                coins_awarded=result['coins_earned'],
                verified_at=datetime.utcnow()
            )
            
            # Update user's coin balance
            storage.update_user_coins(image['user_id'], result['coins_earned'])
        else:
            storage.update_image(
                image_id,
                verification_status='rejected',
                feedback=result['message']
            )
            
    except Exception as e:
        print(f"Error in verify_mosquito_image: {str(e)}")
        storage.update_image(
            image_id,
            verification_status='rejected',
            feedback=f'Error processing image: {str(e)}'
        ) 