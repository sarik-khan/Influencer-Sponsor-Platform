from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    influencer_profile = db.relationship('InfluencerProfile', backref='user', uselist=False)
    sponsor_profile = db.relationship('SponsorProfile', backref='user', uselist=False)


class InfluencerProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    niche = db.Column(db.String(100), nullable=True)
    followers = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.Boolean, default=False)
    campaigns_accepted = db.Column(db.Integer, default=0)
    # Remove the redundant relationship since it's already defined in the User model
    # user = db.relationship('User', backref=db.backref('profile', uselist=False))

class SponsorProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    # The User relationship is now defined in the User model
    # user = db.relationship('User', backref=db.backref('sponsor_profile', uselist=False))


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public' or 'private'
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor_profile.user_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    influencer_username = db.Column(db.String(80), nullable=True)  # Only for private campaigns
    status = db.Column(db.String(150), default='Pending')
    sponsor = db.relationship('SponsorProfile', backref=db.backref('campaigns', lazy=True))


class Negotiation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'pending', 'accepted', 'rejected'

    campaign = db.relationship('Campaign', backref=db.backref('negotiations', lazy=True))
    influencer = db.relationship('User', backref=db.backref('negotiations', lazy=True))


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False)

    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True))
    influencer = db.relationship('User', backref=db.backref('ad_requests', lazy=True))



class AdminProfile(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)