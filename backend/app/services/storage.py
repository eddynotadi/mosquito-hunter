from datetime import datetime
import threading

class Storage:
    def __init__(self):
        self._lock = threading.Lock()  # Thread-safe operations
        self.users = {}  # Store user data
        self.submissions = []  # Store all submissions
        self.next_submission_id = 1

    def add_submission(self, username, image_path, coins):
        with self._lock:
            submission = {
                'id': self.next_submission_id,
                'username': username,
                'image_path': image_path,
                'coins': coins,
                'date': datetime.now().isoformat()
            }
            self.submissions.append(submission)
            self.next_submission_id += 1

            # Create or update user profile
            if username not in self.users:
                self.users[username] = {
                    'username': username,
                    'balance': 0,
                    'submissions': [],
                    'totalKills': 0,
                    'rank': len(self.users) + 1
                }

            user = self.users[username]
            user['balance'] += coins
            user['totalKills'] += 1
            user['submissions'].append(submission)

            # Update ranks for all users
            self._update_ranks()

            return submission

    def get_user_profile(self, username):
        with self._lock:
            if username not in self.users:
                self.users[username] = {
                    'username': username,
                    'balance': 0,
                    'submissions': [],
                    'totalKills': 0,
                    'rank': len(self.users) + 1
                }
            return self.users[username]

    def get_leaderboard(self, limit=10):
        with self._lock:
            # Sort users by balance (coins) in descending order
            sorted_users = sorted(
                self.users.values(),
                key=lambda x: (x['balance'], x['totalKills']),
                reverse=True
            )
            
            # Return top users with rank
            leaderboard = [{
                'id': idx + 1,
                'username': user['username'],
                'coins': user['balance'],
                'kills': user['totalKills']
            } for idx, user in enumerate(sorted_users[:limit])]
            
            return leaderboard

    def _update_ranks(self):
        # Sort users by balance and update their ranks
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: (x['balance'], x['totalKills']),
            reverse=True
        )
        
        for idx, user in enumerate(sorted_users):
            user['rank'] = idx + 1

# Global storage instance
storage = Storage() 