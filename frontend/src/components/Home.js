import React, { useState } from 'react';
import axios from 'axios';

function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [balance, setBalance] = useState(100); // Mock balance for now

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setMessage('Please select an image first');
      return;
    }

    setIsLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      console.log('Starting upload...');
      console.log('File:', selectedFile);
      console.log('FormData:', formData);

      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json',
        },
        timeout: 10000,
        withCredentials: true,
      });

      console.log('Upload response:', response.data);
      setMessage(response.data.message);
      if (response.data.success) {
        setSelectedFile(null);
        setPreview(null);
        setBalance(prev => prev + response.data.coins_earned);
      }
    } catch (error) {
      console.error('Upload error details:', {
        message: error.message,
        code: error.code,
        response: error.response,
        request: error.request
      });

      if (error.code === 'ECONNREFUSED') {
        setMessage('Could not connect to the server. Please make sure the backend is running on http://localhost:5000');
      } else if (error.code === 'ETIMEDOUT') {
        setMessage('Request timed out. Please try again.');
      } else if (error.response) {
        setMessage(`Server error: ${error.response.data.message || error.response.statusText}`);
      } else if (error.request) {
        setMessage('No response received from server. Please check if the server is running.');
      } else {
        setMessage(`Error: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-black/50 border border-neon-blue/30 rounded-2xl p-8 shadow-[0_0_15px_rgba(0,255,255,0.1)] mb-8">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-white">
              <span className="text-neon-blue">Mosquito</span> Coin
            </h1>
            <div className="bg-black/50 border border-neon-pink/30 rounded-full px-6 py-3 shadow-[0_0_15px_rgba(255,0,255,0.1)]">
              <span className="text-white font-bold text-xl">
                {balance} <span className="text-neon-pink">🪙</span>
              </span>
            </div>
          </div>
          <p className="text-white text-xl mb-8 text-center">
            Upload a picture of a dead mosquito to earn coins!
          </p>

          <div className="bg-black/50 border border-neon-blue/30 rounded-xl p-6 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
            <h2 className="text-2xl font-bold mb-6 text-white">Upload Mosquito Image</h2>
            <form onSubmit={handleUpload} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Select Image
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="mt-1 block w-full text-sm text-white
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-black/50 file:text-white
                    file:border file:border-neon-green/30
                    hover:file:bg-black/70
                    cursor-pointer"
                  required
                />
              </div>
              {preview && (
                <div>
                  <label className="block text-sm font-medium text-neon-green mb-2">
                    Preview
                  </label>
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-w-xs rounded-lg shadow-[0_0_15px_rgba(0,255,255,0.1)]"
                  />
                </div>
              )}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-black/50 hover:bg-black/70 text-neon-pink font-bold py-3 px-4 rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed border border-neon-pink/30 shadow-[0_0_15px_rgba(255,0,255,0.1)]"
              >
                {isLoading ? 'Uploading...' : 'Upload Image'}
              </button>
            </form>
            {message && (
              <div className={`mt-4 p-4 rounded-lg ${
                message.includes('Error') || message.includes('Could not connect') 
                  ? 'bg-red-500/20 text-neon-red border border-neon-red/30' 
                  : 'bg-green-500/20 text-neon-green border border-neon-green/30'
              }`}>
                {message}
              </div>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-black/50 border border-neon-blue/30 rounded-xl p-6 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
            <h3 className="text-xl font-bold mb-4 text-neon-blue">Upload Images</h3>
            <p className="text-neon-green">Take pictures of dead mosquitoes and upload them for verification.</p>
          </div>
          <div className="bg-black/50 border border-neon-blue/30 rounded-xl p-6 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
            <h3 className="text-xl font-bold mb-4 text-neon-blue">Earn Coins</h3>
            <p className="text-neon-green">Get rewarded with Mosquito Coins for each verified kill.</p>
          </div>
          <div className="bg-black/50 border border-neon-blue/30 rounded-xl p-6 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
            <h3 className="text-xl font-bold mb-4 text-neon-blue">Compete</h3>
            <p className="text-neon-green">Climb the leaderboard and compete with other users.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home; 