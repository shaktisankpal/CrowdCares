from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPES = [
        ('investor', 'Investor'),
        ('fundraiser', 'Fundraiser'),
        ('ngo', 'NGO/Welfare Organization'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.username or self.email} ({self.get_user_type_display()})"

class FundraisingProject(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('health', 'Health'),
        ('arts', 'Arts'),
        ('technology', 'Technology'),
        ('film', 'Film'),
        ('other', 'Other'),
    ]

    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name="projects", limit_choices_to={'user_type': 'fundraiser'})
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="General")
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    min_contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.01)])
    start_date = models.DateField()
    end_date = models.DateField()
    story_media_link = models.URLField()
    social_media_links = models.TextField(blank=True)
    reward_tiers = models.TextField(blank=True)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def percent_funded(self):
        if self.goal_amount > 0:
            percentage = (self.collected_amount / self.goal_amount) * 100
            return min(100, percentage)
        return 0.00

    def __str__(self):
        return f"{self.title}"

class NGODonationPost(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('health', 'Health'),
        ('environment', 'Environment'),
        ('women_empowerment', 'Women Empowerment'),
        ('other', 'Other'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ngo_posts", limit_choices_to={'user_type': 'ngo'})
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    beneficiaries = models.TextField()
    supporting_documents = models.URLField(blank=True, null=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    min_contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.01)])
    start_date = models.DateField()
    end_date = models.DateField()
    social_media_links = models.TextField(blank=True)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def percent_funded(self):
        if self.target_amount > 0:
            percentage = (self.collected_amount / self.target_amount) * 100
            return min(100, percentage)
        return 0.00

    def __str__(self):
        return f"{self.title} by {self.creator.username}"

class Investment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'investor'})
    project = models.ForeignKey(FundraisingProject, on_delete=models.CASCADE, related_name="investments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.username} invested {self.amount} in {self.project.title}"

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_made')
    post = models.ForeignKey(NGODonationPost, on_delete=models.CASCADE, related_name="donations", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated {self.amount} to {self.post.title}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('investment', 'Investment'),
        ('donation', 'Donation'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    investment = models.ForeignKey(Investment, on_delete=models.SET_NULL, null=True, blank=True)
    donation = models.ForeignKey(Donation, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} ({self.status})"

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    organization = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    govt_id = models.CharField(max_length=50, unique=True)
    bank_account_details = models.TextField()

    def __str__(self):
        return f"Investor Profile - {self.user.username}"

class FundraiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="fundraiser_profile")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    govt_id = models.CharField(max_length=50, unique=True)
    bank_account_details = models.TextField()

    def __str__(self):
        return f"Fundraiser Profile - {self.user.username}"

class NGOWelfareProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ngo_profile")
    organization_name = models.CharField(max_length=255)
    darpan_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    address = models.TextField()
    bank_account_details = models.TextField()

    def __str__(self):
        return f"NGO Profile - {self.user.username}"