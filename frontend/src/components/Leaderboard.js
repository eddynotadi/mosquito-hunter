import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/leaderboard');
        // Ensure the response data is an array
        setLeaderboard(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        setError('Failed to fetch leaderboard data');
        console.error('Error fetching leaderboard:', err);
        setLeaderboard([]); // Set empty array on error
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-neon-blue text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-neon-red text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-black/50 border border-neon-blue/30 rounded-2xl p-8 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">
            <span className="text-neon-blue">🏆</span> Leaderboard
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neon-blue/30">
                  <th className="text-left py-4 px-6 text-white">Rank</th>
                  <th className="text-left py-4 px-6 text-white">Username</th>
                  <th className="text-left py-4 px-6 text-white">Coins</th>
                  <th className="text-left py-4 px-6 text-white">Kills</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(leaderboard) && leaderboard.map((user, index) => (
                  <tr key={user.id} className="border-b border-neon-blue/10 hover:bg-black/30 transition-colors duration-200">
                    <td className="py-4 px-6 text-white font-bold">#{index + 1}</td>
                    <td className="py-4 px-6 text-white">{user.username}</td>
                    <td className="py-4 px-6 text-white">
                      <span className="text-neon-pink">{user.coins}</span> 🪙
                    </td>
                    <td className="py-4 px-6 text-white">
                      <span className="text-neon-green">{user.kills}</span> 🦟
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Leaderboard; 