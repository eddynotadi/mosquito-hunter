from app import db
from datetime import datetime

class MosquitoImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    verification_status = db.Column(db.String(20), nullable=False)  # 'pending', 'verified', 'rejected'
    feedback = db.Column(db.Text)
    coins_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'verification_status': self.verification_status,
            'feedback': self.feedback,
            'coins_awarded': self.coins_awarded,
            'created_at': self.created_at.isoformat(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        } 