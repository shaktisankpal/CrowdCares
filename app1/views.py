from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import UserRegistrationForm, FundraisingProjectForm, NGODonationPostForm
from .models import User, FundraisingProject, NGODonationPost, Investment, Donation, Transaction, FundraiserProfile, NGOWelfareProfile
from decimal import Decimal, InvalidOperation

# User Registration View
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Error! Please check the form and try again.")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})

# Home Page View
def index(request):
    return render(request, 'index.html')

# User Login View
def login(request):
    if request.method == "POST":
        email = request.POST.get('username')  # Using email as username
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            if user.user_type == 'investor':
                return redirect('investor-dashboard')
            elif user.user_type == 'fundraiser':
                return redirect('fundraiser-dashboard')
            elif user.user_type == 'ngo':
                return redirect('ngo-dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Wrong Email or Password")
    return render(request, 'login.html')

# NGO Dashboard View
@login_required
def ngoDashboard(request):
    if request.user.user_type != 'ngo':
        return redirect('login')
    posts = NGODonationPost.objects.filter(creator=request.user)
    return render(request, 'ngoDashboard.html', {
        'user': request.user,
        'posts': posts
    })

# Fundraiser Dashboard View
@login_required
def fundraiserDashboard(request):
    if request.user.user_type != 'fundraiser':
        return redirect('login')
    projects = FundraisingProject.objects.filter(creator=request.user)
    return render(request, 'fundraiserDashboard.html', {'user': request.user, 'projects': projects})

# Fundraiser Create Post View
@login_required
def fundraiserCreatePost(request):
    if request.user.user_type != 'fundraiser':
        return redirect('login')
    if request.method == 'POST':
        form = FundraisingProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            messages.success(request, "Post created successfully!")
            return redirect('fundraiser-dashboard')
        else:
            messages.error(request, "Error! Please check the form and try again.")
    else:
        form = FundraisingProjectForm()
    return render(request, 'fundraiserCreatePost.html', {'form': form})

# User Logout View
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request, "User logged out successfully")
    return redirect('login')

# Investor Dashboard View
@login_required
def investorDashboard(request):
    if request.user.user_type != 'investor':
        return redirect('login')
    
    # Fetch projects with fundraiser profile
    projects = FundraisingProject.objects.select_related('creator__fundraiser_profile').all()
    
    # Fetch donation posts with NGO profile
    donation_posts = NGODonationPost.objects.select_related('creator__ngo_profile').all()
    
    return render(request, 'investorDashboard.html', {
        'projects': projects,
        'donation_posts': donation_posts,
        'user': request.user
    })

# Project Detail View
@login_required
def project_detail(request, pk):
    project = get_object_or_404(FundraisingProject, pk=pk)
    creator = project.creator
    try:
        creator_name = creator.fundraiser_profile.full_name
    except (AttributeError, FundraiserProfile.DoesNotExist):
        creator_name = creator.username or creator.email
    remaining_amount = project.goal_amount - project.collected_amount
    return render(request, 'projectDetail.html', {
        'project': project,
        'creator_name': creator_name,
        'remaining_amount': remaining_amount,
    })

# Donation Post Detail View
@login_required
def donation_post_detail(request, pk):
    post = get_object_or_404(NGODonationPost, pk=pk)
    creator = post.creator
    try:
        creator_name = creator.ngo_profile.organization_name
    except (AttributeError, NGOWelfareProfile.DoesNotExist):
        creator_name = creator.username or creator.email
    remaining_amount = post.target_amount - post.collected_amount
    is_creator = request.user == post.creator
    return render(request, 'donationPostDetail.html', {
        'post': post,
        'creator_name': creator_name,
        'remaining_amount': remaining_amount,
        'is_creator': is_creator,
    })

# Invest View
@login_required
def invest(request, pk):
    if request.user.user_type != 'investor':
        return redirect('login')
    project = get_object_or_404(FundraisingProject, pk=pk)
    remaining_amount = project.goal_amount - project.collected_amount
    if remaining_amount <= 0:
        messages.error(request, "This project has already reached its funding goal.")
        return redirect('project_detail', pk=pk)
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
            elif amount > remaining_amount:
                messages.error(request, f"You can only invest up to ₹{remaining_amount}.")
            else:
                with transaction.atomic():
                    investment = Investment.objects.create(
                        investor=request.user,
                        project=project,
                        amount=amount
                    )
                    project.collected_amount += amount
                    project.save()
                    Transaction.objects.create(
                        user=request.user,
                        transaction_type='investment',
                        amount=amount,
                        status='completed',
                        investment=investment
                    )
                messages.success(request, "Payment Done Successfully")
                return redirect('investor-dashboard')
        except InvalidOperation:
            messages.error(request, "Invalid amount.")
    return redirect('project_detail', pk=pk)

# Donate View
@login_required
def donate(request, pk):
    if request.user.user_type != 'investor':
        messages.error(request, "Only investors can donate.")
        return redirect('login')
    post = get_object_or_404(NGODonationPost, pk=pk)
    remaining_amount = post.target_amount - post.collected_amount
    if remaining_amount <= 0:
        messages.error(request, "This donation post has already reached its funding goal.")
        return redirect('donation_post_detail', pk=pk)
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
            elif amount > remaining_amount:
                messages.error(request, f"You can only donate up to ₹{remaining_amount}.")
            elif post.min_contribution and amount < post.min_contribution:
                messages.error(request, f"Minimum contribution is ₹{post.min_contribution}.")
            else:
                with transaction.atomic():
                    donation = Donation.objects.create(
                        donor=request.user,
                        post=post,
                        amount=amount
                    )
                    post.collected_amount += amount
                    post.save()
                    Transaction.objects.create(
                        user=request.user,
                        transaction_type='donation',
                        amount=amount,
                        status='completed',
                        donation=donation
                    )
                messages.success(request, "Donation successful!")
                return redirect('investor-dashboard')
        except InvalidOperation:
            messages.error(request, "Invalid amount.")
    return redirect('donation_post_detail', pk=pk)

# NGO Create Post View
@login_required
def ngo_create_post(request):
    if request.user.user_type != 'ngo':
        messages.error(request, "You are not authorized to create donation posts.")
        return redirect('login')
    if request.method == 'POST':
        form = NGODonationPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            messages.success(request, "Donation post created successfully!")
            return redirect('ngo-dashboard')
        else:
            messages.error(request, "Error! Please check the form and try again.")
    else:
        form = NGODonationPostForm()
    return render(request, 'ngoCreatePost.html', {'form': form})


# Static Pages
def success_stories(request):
    return render(request, 'success_stories.html')

def our_mission(request):
    return render(request, 'our_mission.html')

def careers(request):
    return render(request, 'careers.html')

def team(request):
    return render(request, 'team.html')