import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-black/50 border-b border-neon-blue/30 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-white font-bold text-xl">
              <span className="text-neon-blue">🦟</span> Mosquito Coin
            </Link>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/"
              className="text-white hover:text-neon-blue px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            >
              Home
            </Link>
            <Link
              to="/leaderboard"
              className="text-white hover:text-neon-blue px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            >
              Leaderboard
            </Link>
            <Link
              to="/transactions"
              className="text-white hover:text-neon-blue px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            >
              Transactions
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 