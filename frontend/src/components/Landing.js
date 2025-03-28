import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const funnyQuotes = [
    "Time to turn those buzzing pests into digital trophies! 🦟",
    "Join the elite squad of mosquito hunters! 🎯",
    "Making the world better, one squashed mosquito at a time! 💪",
    "Your mission: Save humanity from tiny vampires! 🧛‍♂️",
    "Because someone has to be the mosquito's worst nightmare! 😈"
];

const Landing = () => {
    const [currentQuote, setCurrentQuote] = useState(funnyQuotes[0]);
    const [username, setUsername] = useState('');
    const [showError, setShowError] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Rotate quotes every 5 seconds
        const interval = setInterval(() => {
            const randomQuote = funnyQuotes[Math.floor(Math.random() * funnyQuotes.length)];
            setCurrentQuote(randomQuote);
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const playMosquitoSound = () => {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Create oscillators for a more complex sound
        const mainOscillator = audioContext.createOscillator();
        const modulatorOscillator = audioContext.createOscillator();
        const hummingOscillator = audioContext.createOscillator();
        const subOscillator = audioContext.createOscillator();
        
        const gainNode = audioContext.createGain();
        const modulatorGain = audioContext.createGain();
        const hummingGain = audioContext.createGain();
        const subGain = audioContext.createGain();

        // Configure the modulator (creates the "whining" effect)
        modulatorOscillator.frequency.setValueAtTime(6, audioContext.currentTime);
        modulatorGain.gain.setValueAtTime(100, audioContext.currentTime);
        
        // Configure the main oscillator (high-pitched buzz)
        mainOscillator.type = 'sawtooth';
        mainOscillator.frequency.setValueAtTime(700, audioContext.currentTime);
        
        // Configure humming oscillator (lower frequency component)
        hummingOscillator.type = 'sine';
        hummingOscillator.frequency.setValueAtTime(180, audioContext.currentTime);
        hummingGain.gain.setValueAtTime(0.15, audioContext.currentTime);
        
        // Configure sub oscillator (adds body to the sound)
        subOscillator.type = 'triangle';
        subOscillator.frequency.setValueAtTime(350, audioContext.currentTime);
        subGain.gain.setValueAtTime(0.1, audioContext.currentTime);
        
        // Set constant gain without fade
        gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
        
        // Add random variations to simulate movement
        const addRandomVariations = () => {
            const now = audioContext.currentTime;
            // Random frequency variations
            const freqVariation = Math.random() * 50 - 25; // ±25 Hz
            mainOscillator.frequency.linearRampToValueAtTime(700 + freqVariation, now + 0.1);
            
            // Random amplitude variations
            const ampVariation = 0.02 * Math.random();
            gainNode.gain.setValueAtTime(0.15 + ampVariation, now + 0.1);
            
            if (now < audioContext.currentTime + 6) {
                setTimeout(addRandomVariations, 100);
            }
        };
        
        // Connect the modulation
        modulatorOscillator.connect(modulatorGain);
        modulatorGain.connect(mainOscillator.frequency);
        
        // Connect all oscillators to the main gain node
        mainOscillator.connect(gainNode);
        hummingOscillator.connect(hummingGain);
        hummingGain.connect(gainNode);
        subOscillator.connect(subGain);
        subGain.connect(gainNode);
        
        // Connect to output
        gainNode.connect(audioContext.destination);
        
        // Start all oscillators
        mainOscillator.start(audioContext.currentTime);
        modulatorOscillator.start(audioContext.currentTime);
        hummingOscillator.start(audioContext.currentTime);
        subOscillator.start(audioContext.currentTime);
        addRandomVariations();
        
        // Stop all oscillators after 6 seconds
        const stopTime = audioContext.currentTime + 6;
        mainOscillator.stop(stopTime);
        modulatorOscillator.stop(stopTime);
        hummingOscillator.stop(stopTime);
        subOscillator.stop(stopTime);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (username.trim().length < 3) {
            setShowError(true);
            return;
        }
        localStorage.setItem('username', username);
        navigate('/profile');
    };

    return (
        <div className="min-h-screen bg-black text-white p-6">
            <div className="max-w-4xl mx-auto text-center space-y-8">
                {/* Header */}
                <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-500 to-pink-500 text-transparent bg-clip-text"
                    style={{ textShadow: '0 0 20px rgba(255,0,255,0.5)' }}>
                    Mosquito Hunter
                </h1>

                {/* Funny Quote */}
                <div className="text-2xl font-semibold mb-8 h-20 flex items-center justify-center">
                    <p className="animate-pulse">{currentQuote}</p>
                </div>

                {/* Sound Button */}
                <button
                    onClick={playMosquitoSound}
                    className="px-6 py-3 bg-purple-600 rounded-full hover:bg-purple-700 transition-all duration-300 transform hover:scale-105"
                    style={{ boxShadow: '0 0 15px rgba(255,0,255,0.5)' }}>
                    Why to Kill? 💀
                </button>

                {/* Username Form */}
                <form onSubmit={handleSubmit} className="mt-12 space-y-4">
                    <div>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => {
                                setUsername(e.target.value);
                                setShowError(false);
                            }}
                            placeholder="Choose your hunter name"
                            className="w-full max-w-md px-4 py-2 bg-gray-800 rounded-lg border-2 border-purple-500 focus:border-pink-500 focus:outline-none"
                        />
                        {showError && (
                            <p className="text-red-500 mt-2">Username must be at least 3 characters long!</p>
                        )}
                    </div>
                    <button
                        type="submit"
                        className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105"
                        style={{ boxShadow: '0 0 15px rgba(255,0,255,0.5)' }}>
                        Start Hunting! 🎯
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Landing; 