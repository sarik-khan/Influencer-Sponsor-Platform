from app import app, db, login_manager
from flask import render_template, redirect, url_for, flash, request
from forms import RegistrationForm, LoginForm, SponsorProfileForm, CampaignForm, NegotiationForm, ProfileForm
from models import User, InfluencerProfile, SponsorProfile, Campaign, Negotiation, AdminProfile
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    IsNewUser = 'unknown'
    username = None
    
    user = User.query.filter_by(username=form.username.data).first()
    if user:
        IsNewUser = 'false'
        username = form.username.data
    else:
        if form.validate_on_submit():
            IsNewUser = 'true'
            user = User(username=form.username.data, password=form.password.data, role=form.role.data)
            db.session.add(user)
            db.session.commit()
            username = form.username.data
    return render_template('register.html', form=form, IsNewUser=IsNewUser, username=username, role=form.role.data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    validuser = 'true'
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
        if user:
            login_user(user)
            if user.role == 'influencer':
                return redirect(url_for('influencer_dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            validuser = 'false'
    return render_template('login.html', form=form, validuser=validuser, username=form.username.data)


@app.route('/influencer_dashboard', methods=['GET', 'POST'])
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        return redirect(url_for('index'))

    profile = InfluencerProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if profile:
            profile.photo = request.form['photo']
            profile.niche = request.form['niche']
            profile.followers = request.form['followers']
            profile.bio = request.form['bio']
        else:
            profile = InfluencerProfile(
                user_id=current_user.id,
                photo=request.form['photo'],
                niche=request.form['niche'],
                followers=request.form['followers'],
                bio=request.form['bio']
            )
            db.session.add(profile)
        db.session.commit()

    return render_template('influencer_dashboard.html', profile=profile, username=current_user.username)




@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Example logic for editing profile
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))

    form.username.data = current_user.username
    
    return render_template('edit_profile.html', form=form)







@app.route('/sponsor_dashboard', methods=['GET', 'POST'])
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))

    profile = SponsorProfile.query.filter_by(user_id=current_user.id).first()
    form = SponsorProfileForm()

    if form.validate_on_submit():
        if profile:
            profile.company_name = form.company_name.data
            profile.industry = form.industry.data
            profile.budget = form.budget.data
        else:
            profile = SponsorProfile(
                user_id=current_user.id,
                company_name=form.company_name.data,
                industry=form.industry.data,
                budget=form.budget.data
            )
            db.session.add(profile)
        db.session.commit()

    if profile:
        form.company_name.data = profile.company_name
        form.industry.data = profile.industry
        form.budget.data = profile.budget

    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()

    return render_template('sponsor_dashboard.html', form=form, profile=profile, campaigns=campaigns)


@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if current_user.role != 'sponsor':
        flash('Only sponsors can create campaigns.', 'danger')
        return redirect(url_for('home'))

    form = CampaignForm()
    if form.validate_on_submit():
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            sponsor_id=current_user.id,
            influencer_username=form.influencer_username.data if form.visibility.data == 'private' else None
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('create_campaign.html', form=form)


@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.role != 'sponsor':
        flash('Only sponsors can edit campaigns.', 'danger')
        return redirect(url_for('home'))

    form = CampaignForm(obj=campaign)
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.influencer_username = form.influencer_username.data if form.visibility.data == 'private' else None
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('edit_campaign.html', form=form, campaign=campaign)


@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash(f'Campaign {campaign.name} has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))








@app.route('/search_campaigns', methods=['GET'])
def search_campaigns():
    search_by = request.args.get('search_by')
    return render_template('search_campaigns.html', search_by=search_by)

@app.route('/search_by_budget', methods=['GET'])
def search_by_budget():
    min_budget = request.args.get('min_budget')
    campaigns = Campaign.query.filter(Campaign.budget >= min_budget).all()
    return render_template('campaign_results.html', campaigns=campaigns)

@app.route('/search_by_industry', methods=['GET'])
def search_by_industry():
    industry = request.args.get('industry')
    campaigns = Campaign.query.filter_by(visibility='public', industry=industry).all()
    return render_template('campaign_results.html', campaigns=campaigns)






@app.route('/campaigns/<int:campaign_id>/negotiate', methods=['GET', 'POST'])
@login_required
def negotiate_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.role != 'influencer':
        flash('Only influencers can negotiate campaigns.', 'danger')
        return redirect(url_for('home'))

    form = NegotiationForm(campaign_id=str(campaign_id))
    if form.validate_on_submit():
        negotiation = Negotiation(
            campaign_id=campaign.id,
            influencer_id=current_user.id,
            message=form.message.data,
            status='pending'
        )
        db.session.add(negotiation)
        db.session.commit()
        flash('Negotiation proposal sent.', 'success')
        return redirect(url_for('influencer_dashboard'))

    return render_template('negotiation.html', form=form, campaign=campaign)


@app.route('/campaigns/<int:campaign_id>/accept', methods=['POST'])
@login_required
def accept_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.role == 'influencer':
        campaign.influencer_username = current_user.username
        db.session.commit()
        flash('You have accepted the campaign.', 'success')
    elif current_user.role == 'sponsor':
        negotiation = Negotiation.query.filter_by(campaign_id=campaign.id, status='pending').first()
        if negotiation:
            negotiation.status = 'accepted'
            db.session.commit()
            flash('You have accepted the negotiation.', 'success')
    return redirect(url_for('sponsor_dashboard' if current_user.role == 'sponsor' else 'influencer_dashboard'))


@app.route('/approve_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def approve_campaign(campaign_id):
    # Ensure that only sponsors can approve campaigns
    if current_user.role != 'sponsor':
        flash('Only sponsors can approve campaigns', 'error')
        return redirect(url_for('dashboard'))

    # Fetch the campaign from the database
    campaign = Campaign.query.get_or_404(campaign_id)

    # Ensure that the current user is the sponsor of the campaign
    if campaign.sponsor_id != current_user.id:
        flash('You are not authorized to approve this campaign', 'error')
        return redirect(url_for('dashboard'))

    # Update the status of the campaign to 'Approved'
    campaign.status = 'Approved'
    db.session.commit()

    flash('Campaign approved successfully!', 'success')
    return redirect(url_for('dashboard'))




@app.route('/campaigns/<int:campaign_id>/reject', methods=['POST'])
@login_required
def reject_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.role == 'influencer':
        campaign.influencer_username = None
        db.session.commit()
        flash('You have rejected the campaign.', 'danger')
    elif current_user.role == 'sponsor':
        negotiation = Negotiation.query.filter_by(campaign_id=campaign.id, status='pending').first()
        if negotiation:
            negotiation.status = 'rejected'
            db.session.commit()
            flash('You have rejected the negotiation.', 'danger')
    return redirect(url_for('sponsor_dashboard' if current_user.role == 'sponsor' else 'influencer_dashboard'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    form = AdminProfile(id=current_user.id)
    admin = AdminProfile.query.filter_by(username=current_user.username).first()
    username=current_user.username
    sponsors = SponsorProfile.query.all()
    influencers = InfluencerProfile.query.all()
    campaigns = Campaign.query.all()

    return render_template('admin_dashboard.html',form=form, username=username, admin=admin, sponsors=sponsors, influencers=influencers, campaigns=campaigns)

@app.route('/flag_sponsor/<int:sponsor_id>', methods=['POST'])
@login_required
def flag_sponsor(sponsor_id):
    sponsor = SponsorProfile.query.get_or_404(sponsor_id)
    sponsor.flagged = True
    db.session.commit()
    flash(f'Sponsor {sponsor.username} has been flagged.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/flag_influencer/<int:influencer_id>', methods=['POST'])
@login_required
def flag_influencer(influencer_id):
    influencer = InfluencerProfile.query.get_or_404(influencer_id)
    influencer.flagged = True
    db.session.commit()
    flash(f'Influencer {influencer.username} has been flagged.', 'success')
    return redirect(url_for('admin_dashboard'))