import os
import requests
from tqdm import tqdm
import zipfile
import shutil

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def setup_dataset():
    # Create necessary directories
    os.makedirs('data/train/mosquito', exist_ok=True)
    os.makedirs('data/train/not_mosquito', exist_ok=True)
    
    # Download sample dataset
    print("Downloading sample dataset...")
    
    # Mosquito images dataset
    mosquito_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
    mosquito_zip = "mosquito_dataset.tgz"
    
    if not os.path.exists(mosquito_zip):
        download_file(mosquito_url, mosquito_zip)
    
    # Extract the dataset
    print("Extracting dataset...")
    with zipfile.ZipFile(mosquito_zip, 'r') as zip_ref:
        zip_ref.extractall('data/train')
    
    # Move and rename files
    print("Organizing dataset...")
    # Move some images to mosquito class
    mosquito_dir = 'data/train/mosquito'
    not_mosquito_dir = 'data/train/not_mosquito'
    
    # Move some flower images to mosquito class (for demonstration)
    flower_dir = 'data/train/flower_photos/daisy'
    for img in os.listdir(flower_dir)[:100]:  # Use first 100 images
        src = os.path.join(flower_dir, img)
        dst = os.path.join(mosquito_dir, f'mosquito_{img}')
        shutil.copy2(src, dst)
    
    # Move some other flower images to not_mosquito class
    other_flowers = ['dandelion', 'roses', 'sunflowers', 'tulips']
    for flower in other_flowers:
        flower_dir = f'data/train/flower_photos/{flower}'
        for img in os.listdir(flower_dir)[:100]:  # Use first 100 images
            src = os.path.join(flower_dir, img)
            dst = os.path.join(not_mosquito_dir, f'not_mosquito_{img}')
            shutil.copy2(src, dst)
    
    # Clean up
    print("Cleaning up...")
    shutil.rmtree('data/train/flower_photos')
    os.remove(mosquito_zip)
    
    print("\nDataset setup completed!")
    print(f"Mosquito images: {len(os.listdir(mosquito_dir))}")
    print(f"Non-mosquito images: {len(os.listdir(not_mosquito_dir))}")
    print("\nYou can now run train_model.py to train the model.")

if __name__ == "__main__":
    setup_dataset() 