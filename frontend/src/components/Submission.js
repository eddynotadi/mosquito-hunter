import React, { useState, useRef } from 'react';
import axios from 'axios';

const Submission = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [coinsEarned, setCoinsEarned] = useState(0);
  const [username, setUsername] = useState('user1'); // Default username, you can modify this
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (!selectedFile) {
        throw new Error('Please select an image first');
      }

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('username', username);

      const response = await axios.post('http://localhost:5000/submit_image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setSuccess(true);
        setCoinsEarned(response.data.coins);
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        // You can implement fetchUserProfile function if needed
        // await fetchUserProfile();
      } else {
        setError(response.data.message || 'Failed to verify image');
      }
    } catch (err) {
      if (err.response) {
        switch (err.response.data.error) {
          case 'INVALID_FILE':
            setError('Please select a valid image file');
            break;
          case 'FILE_TOO_LARGE':
            setError('Image file is too large');
            break;
          case 'INVALID_TYPE':
            setError('Invalid file type. Please upload an image');
            break;
          case 'PROCESSING_ERROR':
            setError('Error processing the image');
            break;
          case 'VERIFICATION_ERROR':
            setError('Failed to verify the image');
            break;
          case 'DUPLICATE_IMAGE':
            setError('This image has already been submitted');
            break;
          case 'INVALID_IMAGE':
            setError('Not a valid mosquito image');
            break;
          default:
            setError('An error occurred while submitting the image');
        }
      } else {
        setError('Failed to connect to the server');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setError('File size too large. Please select an image under 5MB.');
        e.target.value = '';
        return;
      }
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file.');
        e.target.value = '';
        return;
      }
      setSelectedFile(file);
      setError(null);
      setSuccess(false);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-center">Submit Mosquito Image</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Select Image
            </label>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
          </div>

          {preview && (
            <div className="mt-4">
              <img
                src={preview}
                alt="Preview"
                className="max-w-full h-auto rounded-lg shadow"
              />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {success && (
            <div className="bg-green-50 border-l-4 border-green-400 p-4">
              <p className="text-green-700">
                Success! You earned {coinsEarned} coins.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !selectedFile}
            className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
              ${loading || !selectedFile 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? 'Submitting...' : 'Submit Image'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Submission; 