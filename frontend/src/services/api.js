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

export const submitImage = async (imageFile) => {
    try {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('username', localStorage.getItem('username'));

        const response = await fetch(`${API_URL}/submit`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to submit image');
        }

        return data;
    } catch (error) {
        console.error('Error submitting image:', error);
        throw error;
    }
}; 