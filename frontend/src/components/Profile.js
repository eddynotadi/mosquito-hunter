import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserProfile, submitImage } from '../services/api';

const Profile = () => {
    const [userData, setUserData] = useState({
        username: localStorage.getItem('username') || 'Hunter',
        balance: 0,
        submissions: [],
        rank: 0,
        totalKills: 0
    });
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            const data = await getUserProfile();
            if (data) {
                setUserData(data);
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

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

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedFile) {
            setUploadStatus('Please select an image first!');
            return;
        }

        try {
            setUploadStatus('Uploading...');
            const result = await submitImage(selectedFile);
            if (result) {
                setUploadStatus('Success! Image submitted successfully.');
                setSelectedFile(null);
                setPreview(null);
                fetchUserData(); // Refresh user data
            }
        } catch (error) {
            console.error('Submission error:', error);
            setUploadStatus(`Error: ${error.message || 'Failed to submit image. Please try again.'}`);
        }
    };

    const stats = [
        { label: 'Total Coins', value: userData.balance },
        { label: 'Mosquitoes Caught', value: userData.totalKills },
        { label: 'Global Rank', value: `#${userData.rank}` },
        { label: 'Submissions', value: userData.submissions.length }
    ];

    return (
        <div className="min-h-screen bg-black text-white p-6">
            {/* Profile Header */}
            <div className="max-w-4xl mx-auto bg-gradient-to-r from-purple-900 to-pink-900 rounded-xl p-6 mb-8"
                style={{
                    boxShadow: '0 0 20px #ff00ff',
                }}>
                <h1 className="text-4xl font-bold mb-2"
                    style={{
                        textShadow: '0 0 10px #ff00ff',
                    }}>
                    {userData.username}'s Profile
                </h1>
                <p className="text-purple-300">Legendary Mosquito Hunter</p>
            </div>

            {/* Stats Grid */}
            <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {stats.map((stat, index) => (
                    <div key={index} 
                        className="bg-gray-900 rounded-lg p-6 transform hover:scale-105 transition-all duration-300"
                        style={{
                            boxShadow: '0 0 10px #00ff00',
                        }}>
                        <h3 className="text-xl text-gray-400 mb-2">{stat.label}</h3>
                        <p className="text-3xl font-bold text-green-400">{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Image Submission Section */}
            <div className="max-w-4xl mx-auto bg-gray-900 rounded-xl p-6 mb-8"
                style={{
                    boxShadow: '0 0 15px #00ff00',
                }}>
                <h2 className="text-2xl font-bold mb-4 text-purple-400">Submit Mosquito Image</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex flex-col items-center space-y-4">
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileSelect}
                            className="hidden"
                            id="image-upload"
                        />
                        <label
                            htmlFor="image-upload"
                            className="w-full max-w-md px-6 py-3 bg-purple-600 rounded-lg hover:bg-purple-700 transition-all duration-300 cursor-pointer text-center"
                            style={{ boxShadow: '0 0 10px rgba(255,0,255,0.5)' }}>
                            {selectedFile ? 'Change Image' : 'Select Image'}
                        </label>
                        {preview && (
                            <div className="mt-4">
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="max-w-xs rounded-lg shadow-lg"
                                />
                            </div>
                        )}
                        <button
                            type="submit"
                            disabled={!selectedFile}
                            className={`w-full max-w-md px-6 py-3 rounded-lg transition-all duration-300 ${
                                selectedFile
                                    ? 'bg-green-600 hover:bg-green-700'
                                    : 'bg-gray-600 cursor-not-allowed'
                            }`}
                            style={{ boxShadow: '0 0 10px rgba(0,255,0,0.5)' }}>
                            Submit Image
                        </button>
                        {uploadStatus && (
                            <p className={`text-sm ${
                                uploadStatus.includes('Success') ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {uploadStatus}
                            </p>
                        )}
                    </div>
                </form>
            </div>

            {/* Recent Activity */}
            <div className="max-w-4xl mx-auto bg-gray-900 rounded-xl p-6"
                style={{
                    boxShadow: '0 0 15px #00ff00',
                }}>
                <h2 className="text-2xl font-bold mb-4 text-purple-400">Recent Activity</h2>
                {userData.submissions.length > 0 ? (
                    <div className="space-y-4">
                        {userData.submissions.map((submission, index) => (
                            <div key={index} className="bg-gray-800 rounded-lg p-4 flex justify-between items-center">
                                <div>
                                    <p className="text-green-400">+{submission.coins} coins earned</p>
                                    <p className="text-sm text-gray-400">{new Date(submission.date).toLocaleDateString()}</p>
                                </div>
                                <div className="text-purple-400">#{submission.id}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-500">No activity yet. Start hunting!</p>
                )}
            </div>

            {/* Action Buttons */}
            <div className="max-w-4xl mx-auto mt-8 flex gap-4">
                <button
                    onClick={() => navigate('/home')}
                    className="flex-1 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition-all duration-300"
                    style={{
                        boxShadow: '0 0 10px #ff00ff',
                    }}>
                    Back to Hunting 🎯
                </button>
                <button
                    onClick={() => navigate('/leaderboard')}
                    className="flex-1 py-3 rounded-lg bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 transition-all duration-300"
                    style={{
                        boxShadow: '0 0 10px #00ff00',
                    }}>
                    View Leaderboard 🏆
                </button>
            </div>
        </div>
    );
};

export default Profile; 