const API_URL = 'http://localhost:5000/api';

export const getUserProfile = async () => {
    try {
        const response = await fetch(`${API_URL}/user/profile`, {
            method: 'GET',
            headers: {
                'X-Username': localStorage.getItem('username')
            }
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch profile');
        }

        return data;
    } catch (error) {
        console.error('Error fetching profile:', error);
        throw error;
    }
};

export const submitImage = async (file, userId) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('user_id', userId);

    try {
        const response = await fetch(`${API_URL}/submit`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to submit image');
        }

        return await response.json();
    } catch (error) {
        console.error('Error submitting image:', error);
        throw error;
    }
};

export const getSubmissions = async (userId) => {
    try {
        const response = await fetch(`${API_URL}/submissions/${userId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch submissions');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching submissions:', error);
        throw error;
    }
};

export const getLeaderboard = async () => {
    try {
        const response = await fetch(`${API_URL}/leaderboard`);
        if (!response.ok) {
            throw new Error('Failed to fetch leaderboard');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        throw error;
    }
}; 