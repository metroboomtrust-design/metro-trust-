from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
# Create your models here.




class Portfolio(models.Model):
    CURRENCY_CHOICES = [
    ('$', 'Dollar'),
    ('£', 'Pound Sterling'),
    ('€', 'Euro'),
    ('₣', 'Swiss Franc'),
    ('kr', 'Danish Krone'),
    ('kr', 'Swedish Krona'),
    ('kr', 'Norwegian Krone'),
    ('zł', 'Polish Zloty'),
    ('₴', 'Ukrainian Hryvnia'),
    ('лв', 'Bulgarian Lev'),
    ('Ft', 'Hungarian Forint'),
    ('lei', 'Romanian Leu'),
    ('₺', 'Turkish Lira'),
    ('руб', 'Russian Ruble'),
    ('Kč', 'Czech Koruna'),
    ('kn', 'Croatian Kuna'),
    ('RSD', 'Serbian Dinar'),
    ('MKD', 'Macedonian Denar'),
    ('ISK', 'Icelandic Krona'),
]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        
    ]

    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active (Normal Transactions)'),
        ('pending_review', 'Pending Review'),
        ('on_hold', 'On Hold (Limited Transactions)'),
        ('locked', 'Account Locked'),
        ('imf_locked', 'IMF Locked'),
    ]

    

    

    username= models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=500, blank= True, null = True)
    last_name = models.CharField(max_length=200, blank= True, null = True)
    account_number = models.CharField(max_length=200, blank= True, null = True)
    city = models.CharField(max_length=200, blank= True, null = True)
    Country = models.CharField(max_length=200, blank= True, null = True)
    state = models.CharField(max_length=200, blank= True, null = True)
    address = models.CharField(max_length=200, blank= True, null = True)
    phone_number = models.IntegerField( blank= True, null = True)
    zipcode = models.IntegerField( blank= True, null = True)
    tax_id = models.CharField(max_length=200, blank= True, null = True)
    client_email_address = models.CharField(max_length=200, blank= True, null = True)
    date_of_birth = models.CharField(max_length=200, blank= True, null = True)
    apartment = models.CharField(max_length=200, blank= True, null = True)
    profile_image = CloudinaryField('image', blank=True, null=True)
    account_total = models.IntegerField(blank= True, null = True)
    checking_total = models.IntegerField(blank= True, null = True)
    pin = models.IntegerField(null= True, blank= True)
    amount_sign = models.CharField(max_length=5, choices=CURRENCY_CHOICES, blank=True, null=True)
    total_income = models.IntegerField(blank= True, null = True)
    level_one = models.IntegerField(blank= True, null = True)
    level_two = models.IntegerField(blank= True, null = True)
    level_three = models.IntegerField(blank= True, null = True)
    level_four = models.IntegerField(blank= True, null = True)
    card_total_balance = models.CharField(max_length=200, blank= True, null = True)
    card_monthly_spend = models.CharField(max_length=200, blank= True, null = True)
    card_available_credit = models.CharField(max_length=200, blank= True, null = True)
    card_number_one = models.CharField(max_length=200, blank= True, null = True)
    card_name_one = models.CharField(max_length=200, blank= True, null = True)
    card_date_one = models.CharField(max_length=200, blank= True, null = True)
    card_number_two = models.CharField(max_length=200, blank= True, null = True)
    card_name_two = models.CharField(max_length=200, blank= True, null = True)
    card_date_two = models.CharField(max_length=200, blank= True, null = True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    tin = models.CharField(max_length=100, blank=True, null=True)  
    occupation = models.CharField(max_length=200, blank=True, null=True)
    government_id = models.FileField(upload_to='government_ids/', blank=True, null=True)
    account_status = models.CharField( max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active', blank=True, null=True)
    
    
    


    
    

    def __str__(self):
        return self.first_name if self.first_name else ''
    
    def get_image_name(self):
        return str(self.profile_image) if self.profile_image else ''
    
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
    
class Transactions(models.Model):

    DEBIT = 'Debit'
    CREDIT = 'Credit'
    PENDING = 'Pending'
    ON_HOLD = 'On Hold'
    ACCOUNT_LOCKED = 'Account Locked'
    IMF_LOCKED = 'Imf Locked'

    ACCOUNT_TYPE_CHOICES = [
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
        (PENDING, 'Pending'),
        (ON_HOLD, 'On Hold'),
        (ACCOUNT_LOCKED, 'Account Locked'),
        (IMF_LOCKED, 'Imf Locked')


    ]
    CURRENCY_CHOICES = [
    ('$', 'Dollar'),
    ('£', 'Pound Sterling'),
    ('€', 'Euro'),
    ('₣', 'Swiss Franc'),
    ('kr', 'Danish Krone'),
    ('kr', 'Swedish Krona'),
    ('kr', 'Norwegian Krone'),
    ('zł', 'Polish Zloty'),
    ('₴', 'Ukrainian Hryvnia'),
    ('лв', 'Bulgarian Lev'),
    ('Ft', 'Hungarian Forint'),
    ('lei', 'Romanian Leu'),
    ('₺', 'Turkish Lira'),
    ('руб', 'Russian Ruble'),
    ('Kč', 'Czech Koruna'),
    ('kn', 'Croatian Kuna'),
    ('RSD', 'Serbian Dinar'),
    ('MKD', 'Macedonian Denar'),
    ('ISK', 'Icelandic Krona'),
]

    username = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, blank= True, null = True)
    id = models.AutoField(primary_key=True)
    beneficiary_name = models.CharField(max_length=200, blank= True, null = True)
    account_number = models.CharField(max_length=200, blank= True, null = True)
    branch_name = models.CharField(max_length=200, blank= True, null = True)
    bank_address = models.CharField(max_length=200, blank= True, null = True)
    bank_name = models.CharField(max_length=200, blank= True, null = True)
    account_type = models.CharField(max_length=200, blank= True, null = True)
    amount_to_transfer = models.IntegerField()
    beneficiary_email = models.EmailField(max_length=200, blank= True, null = True)
    senders_phone_number = models.CharField(max_length=15, blank= True, null = True)
    bank_swift_code = models.CharField(max_length=200, blank= True, null = True)
    transfer_pin = models.IntegerField(null=True, blank=True)
    transaction_date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=200, choices=ACCOUNT_TYPE_CHOICES, null=True, blank=True)
    purpose_of_the_transfer = models.CharField(max_length=200, blank= True, null = True)
    amount_sign = models.CharField(max_length=5, choices=CURRENCY_CHOICES, blank=True, null=True, default='$',)
    profile_image = CloudinaryField('image', blank=True, null=True)
    

    def __str__(self):
        return f"Transaction {self.id} - {self.beneficiary_name or 'Unnamed'}"

    
    def get_image_name(self):
        return str(self.profile_image) if self.profile_image else ''
    
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
    


    


    



    