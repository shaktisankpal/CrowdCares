from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, FundraisingProject, Investment, Donation, Transaction, 
    InvestorProfile, FundraiserProfile, NGOWelfareProfile, NGODonationPost
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (('User Type', {'fields': ('user_type',)}),)
    
    def get_username(self, obj):
        return obj.username or obj.email
    get_username.short_description = 'Username'

@admin.register(FundraisingProject)
class FundraisingProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'goal_amount', 'collected_amount', 'created_at')
    search_fields = ('title', 'creator__email')
    list_filter = ('category', 'created_at')

@admin.register(NGODonationPost)
class NGODonationPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'target_amount', 'collected_amount', 'start_date', 'end_date')
    search_fields = ('title', 'creator__email')
    list_filter = ('category', 'start_date', 'end_date')

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('investor', 'project', 'amount', 'timestamp')
    search_fields = ('investor__email', 'project__title')
    list_filter = ('timestamp',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'post', 'amount', 'timestamp')
    search_fields = ('donor__email', 'post__title')
    list_filter = ('timestamp',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'timestamp')
    search_fields = ('user__email',)
    list_filter = ('transaction_type', 'status', 'timestamp')

@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'country', 'city')
    search_fields = ('user__email', 'full_name', 'phone_number', 'country', 'city')
    list_filter = ('country', 'city')

@admin.register(FundraiserProfile)
class FundraiserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'govt_id')
    search_fields = ('user__email', 'full_name', 'phone_number', 'govt_id')
    list_filter = ('user__user_type',)

@admin.register(NGOWelfareProfile)
class NGOWelfareProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name', 'darpan_id', 'phone_number')
    search_fields = ('user__email', 'organization_name', 'darpan_id')
    list_filter = ('organization_name',)