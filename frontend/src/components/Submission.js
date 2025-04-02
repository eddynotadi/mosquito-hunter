import React, { useState } from 'react';
import axios from 'axios';

const Submission = () => {
  const [file, setFile] = useState(null);
  const [username, setUsername] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) { // 5MB limit
        setError('File size too large. Please select an image under 5MB.');
        e.target.value = '';
        return;
      }
      if (!selectedFile.type.startsWith('image/')) {
        setError('Please select a valid image file.');
        e.target.value = '';
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (!file) {
      setError('Please select an image file');
      setLoading(false);
      return;
    }

    if (!username) {
      setError('Please enter a username');
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('username', username);

    try {
      const response = await axios.post('http://localhost:5000/api/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data && response.data.success) {
        setMessage(response.data.message || 'Image submitted successfully');
        setFile(null);
        setUsername('');
        // Reset file input
        const fileInput = document.getElementById('image');
        if (fileInput) {
          fileInput.value = '';
        }
      } else {
        setError(response.data?.message || response.data?.error || 'Failed to submit image');
      }
    } catch (err) {
      console.error('Submission error:', err);
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(err.response.data?.message || err.response.data?.error || 'Server error occurred');
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response from server. Please check your connection.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError('Error setting up the request. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="submission-container">
      <h2>Submit Mosquito Image</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={handleUsernameChange}
            required
            placeholder="Enter your username"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="image">Image:</label>
          <input
            type="file"
            id="image"
            accept="image/*"
            onChange={handleFileChange}
            required
            disabled={loading}
          />
          <small className="file-hint">Maximum file size: 5MB. Supported formats: PNG, JPG, JPEG</small>
        </div>

        {error && <div className="error-message">{error}</div>}
        {message && <div className="success-message">{message}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Image'}
        </button>
      </form>

      <style jsx>{`
        .submission-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }

        input[type="text"] {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
        }

        input[type="file"] {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
        }

        .file-hint {
          display: block;
          margin-top: 5px;
          color: #666;
          font-size: 14px;
        }

        button {
          background-color: #4CAF50;
          color: white;
          padding: 12px 24px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
          width: 100%;
          transition: background-color 0.3s;
        }

        button:hover:not(:disabled) {
          background-color: #45a049;
        }

        button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }

        .error-message {
          color: #ff0000;
          margin: 10px 0;
          padding: 10px;
          background-color: #ffebee;
          border-radius: 4px;
          border: 1px solid #ffcdd2;
        }

        .success-message {
          color: #4CAF50;
          margin: 10px 0;
          padding: 10px;
          background-color: #e8f5e9;
          border-radius: 4px;
          border: 1px solid #c8e6c9;
        }
      `}</style>
    </div>
  );
};

export default Submission; 