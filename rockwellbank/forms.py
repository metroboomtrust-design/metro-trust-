from django import forms
from .models import Transactions, Portfolio
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserPortfolioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class PortfolioForm(forms.ModelForm):

    class Meta:
        model = Portfolio
        fields = [
            'first_name', 'last_name', 'gender', 'nationality', 'tin',
            'occupation', 'address',  'government_id'
        ]


class TransactionsForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ('beneficiary_name', 'account_number', 'branch_name', 'bank_address', 'bank_name', 'amount_to_transfer', 'beneficiary_email', 'senders_phone_number', 'bank_swift_code', 'purpose_of_the_transfer', 'transfer_pin' ) 





