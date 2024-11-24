from django.shortcuts import render, redirect
from .forms import BankDetailsForm
from .models import BankDetails
import pandas as pd
from django.core.cache import cache  # Import Django's cache system
import json
from django.http import JsonResponse
from .models import BankMapping  # Ensure this model exists
import re
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BankMapping
import re



# Precompiled regex patterns for efficiency
remove_square_brackets = re.compile(r'\[.*?\]')  # Remove content within square brackets
remove_unwanted_chars = re.compile(r'[^\w]')  # Remove anything that's not a word character (alphanumeric or underscore)

def clean_column_name(column_name):
    """
    Cleans the given column name by removing content in square brackets and unwanted characters.
    - Removes anything between square brackets (e.g., [example]).
    - Removes non-alphanumeric characters and underscores from the name.
    - Strips leading and trailing whitespace or unwanted characters.
    """
    # Remove content within square brackets
    column_name = remove_square_brackets.sub('', column_name)
    # Remove unwanted characters (./,\,_, etc.)
    column_name = remove_unwanted_chars.sub('', column_name)
    # Strip leading and trailing whitespace or characters
    return column_name.strip()


def add_bank_details(request):
    if request.method == 'POST':
        form = BankDetailsForm(request.POST)
        if form.is_valid():
            bank_details = form.save(commit=False)
            bank_details.bank_rule_mapping = None  # Initially null
            bank_details.save()
            return redirect('bank_details_list')  # Redirect to a list view or a success page
    else:
        form = BankDetailsForm()
    
    return render(request, 'add_bank_details.html', {'form': form})




def bank_details_list(request):
    bank_details = BankDetails.objects.all()  # Fetch all bank details for the table
    # bank_names = BankDetails.objects.values_list('bank_name', flat=True).distinct()  # Get all unique bank names
    bank_names = BankDetails.objects.values_list('bank_name', flat=True).distinct()  # Get all unique bank names
    bank_ids = BankDetails.objects.values_list('bank_id', flat=True).distinct()  # Get all unique bank IDs
    transaction_types = BankDetails.objects.values_list('transaction_type', flat=True).distinct()  # Get all unique transaction types


    # Try to fetch column names and total columns from cache
    column_names = cache.get('column_names')
    total_columns = cache.get('column_total', 0)  # Default total_columns to 0 if not cached

    if request.method == 'POST' and 'uploaded_file' in request.FILES:
        uploaded_file = request.FILES['uploaded_file']

        # Use pandas to read the file temporarily and extract column headers
        try:
            # Check the file extension to determine the appropriate pandas reader
            file_extension = uploaded_file.name.split('.')[-1].lower()

            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xls', 'xlsx', 'ods']:
                df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else None)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            column_names = df.columns.tolist()
            total_columns = len(column_names)  # Calculate total columns

            # Cache the column names and total column count for 2 minutes (120 seconds)
            cache.set('column_names', column_names, timeout=120)
            cache.set('column_total', total_columns, timeout=120)
        except Exception as e:
            column_names = [f"Error reading file: {e}"]
            total_columns = 0

    return render(request, 'bank_details_list.html', {
        'bank_details': bank_details,
        'column_names': column_names,  # Pass cached column names to the template
        'total_columns': total_columns,  # Pass cached total column count to the template
        'bank_names': bank_names,  # Pass the list of bank names
        'bank_ids': bank_ids,  # Pass bank IDs
        'transaction_types': transaction_types,  # Pass transaction types
    })

@csrf_exempt
def save_mappings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bank_name = data.get('bank_name')
            bank_id = data.get('bank_id')
            mappings = data.get('mappings')
            transaction_type = data.get('transaction_type')  # Get transaction type from the request

            # Debug logs
            print(f"Received Data: {data}")

            if not bank_name or not bank_id or not mappings or not transaction_type:
                return JsonResponse({'error': 'Bank Name, Bank ID, transaction type, and mappings are required.'}, status=400)

            if BankMapping.objects.filter(bank_id=bank_id).exists():
                return JsonResponse({'error': f'Bank {bank_name} is already mapped!'}, status=400)

            # Add transaction type to the headers as a key
            headers_with_transaction = []
            for mapping in mappings:
                headers = mapping.get('fileColumn')
                # For each header, wrap it with the transaction type key
                headers_with_transaction.append({transaction_type: headers})

            # Save directly without json.dumps
            BankMapping.objects.create(
                bank_id=bank_id,
                bank_name=bank_name,
                headers=headers_with_transaction  # Store headers with the transaction type key
            )
            return JsonResponse({'success': 'Mappings saved successfully!'})
        except Exception as e:
            print(f"Error: {e}")  # Log the error for debugging
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
