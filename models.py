
from django.db import models
from django.contrib.postgres.fields import ArrayField  # Optional if you're using PostgreSQL
import json
import logging

logger = logging.getLogger(__name__)



class BankDetails(models.Model):
    bank_name = models.CharField(max_length=100)
    bank_id = models.CharField(max_length=20, unique=True)  # Make bank_id unique
    mid = models.CharField(max_length=50, unique=True)  # Make mid unique
    merchant_name = models.CharField(max_length=100)

    
    TRANSACTION_TYPES = [
        ('SALE', 'SALE'),
        ('REFUND', 'REFUND'),
        ('NET SETTLED', 'NET SETTLED'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    bank_rule_mapping = models.TextField(null=True, blank=True)  # Nullable field

    class Meta:
        unique_together = ('bank_id', 'mid')  # Unique together constraint to ensure combination is unique

    def __str__(self):
        return f"{self.bank_name} ({self.bank_id})"



class BankMapping(models.Model):
    bank_id = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    headers = models.JSONField()  # Handles serialization/deserialization automatically

    # Ensure combination of bank_id, bank_name, and headers is unique
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bank_id', 'bank_name', 'headers'], name='unique_bank_mapping')
        ]

    def set_headers(self, headers):
        """
        Preprocesses headers to group them by transaction type.
        Example: 
        [
            {"NET SETTLED": "BANK BOOKING REF.NO."},
            {"NET SETTLED": "REFUND AMOUNT"},
            {"NET SETTLED": "REFUND DATE"}
        ]
        Becomes:
        [
            {"NET SETTLED": ["BANK BOOKING REF.NO.", "REFUND AMOUNT", "REFUND DATE"]}
        ]
        """
        if isinstance(headers, str):
            import json
            headers = json.loads(headers)  # Convert JSON string to Python list
        
        # Process headers to group by transaction type
        grouped_headers = {}
        for header in headers:
            for transaction_type, column_name in header.items():
                if transaction_type not in grouped_headers:
                    grouped_headers[transaction_type] = []
                grouped_headers[transaction_type].append(column_name)
        
        self.headers = grouped_headers

    def get_headers(self):
        if isinstance(self.headers, str):
            import json
            return json.loads(self.headers)  # Convert back if serialized accidentally
        return self.headers

    def save(self, *args, **kwargs):
        # Before saving, preprocess headers to group them
        if isinstance(self.headers, list):  # If headers are passed as a list of dicts
            self.set_headers(self.headers)

        # Custom logic to ensure that headers are unique per bank_id and bank_name
        if BankMapping.objects.filter(bank_id=self.bank_id, bank_name=self.bank_name, headers=self.headers).exists():
            raise ValueError(f"Mapping with bank_id {self.bank_id}, bank_name {self.bank_name}, and these headers already exists.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bank_name} - {self.bank_id}"



class Transaction(models.Model):
    # Fields for transaction data
    Merchant_Name = models.CharField(max_length=50, blank=True, null=True)
    MID = models.CharField(max_length=50, blank=True)
    Transaction_Id = models.CharField(max_length=50, blank=True, null=True)
    Order_Id = models.CharField(max_length=50, blank=True, null=True)
    Transaction_Date = models.DateField(blank=True, null=True)
    Settlement_Date = models.DateField()
    Refund_Request_Date = models.DateField(blank=True, null=True)
    Transaction_type = models.CharField(max_length=50, blank=True)
    Gross_Amount = models.FloatField(blank=True, null=True)
    Aggregator_Com = models.FloatField(blank=True, null=True)
    Acquirer_Comm = models.FloatField(blank=True, null=True)
    Payable_Merchant = models.FloatField(blank=True)
    Payout_from_Nodal = models.FloatField(blank=True, null=True)
    BankName_Receive_Funds = models.CharField(max_length=50, blank=True, null=True)
    Nodal_Account_No = models.CharField(max_length=50, blank=True, null=True)
    Aggregator_Name = models.CharField(max_length=50, blank=True, null=True)
    Acquirer_Name = models.CharField(max_length=50, blank=True, null=True)
    Refund_Flag = models.CharField(max_length=10, blank=True, null=True)
    Payments_Type = models.CharField(max_length=50, blank=True, null=True)
    MOP_Type = models.CharField(max_length=50, blank=True, null=True)
    Credit_Debit_Date = models.DateField(blank=True, null=True)
    Bank_Name = models.CharField(max_length=15, blank=True, null=True)
    Refund_Order_Id = models.CharField(max_length=50, blank=True, null=True)
    Acq_Id = models.CharField(max_length=125, blank=True, null=True)
    Approve_code = models.CharField(max_length=50, blank=True, null=True)
    Arn_No = models.CharField(max_length=150, blank=True, null=True)
    Card_No = models.CharField(max_length=150, blank=True, null=True)
    Tid = models.CharField(max_length=125, blank=True, null=True)
    Remarks = models.CharField(max_length=50, blank=True, null=True)
    Bank_Ref_id = models.CharField(max_length=125, blank=True, null=True)
    File_upload_Date = models.DateTimeField(blank=True, null=True)
    User_name = models.CharField(max_length=25, blank=True, null=True)
    Recon_Status = models.CharField(max_length=25, blank=True, null=True)
    Mpr_Summary_Trans = models.CharField(max_length=10, blank=True, null=True)
    Merchant_code = models.CharField(max_length=50, blank=True, null=True)
    Rec_Fmt = models.CharField(max_length=50, blank=True, null=True)
    Card_type = models.CharField(max_length=100, blank=True, null=True)
    Intl_Amount = models.FloatField(blank=True, null=True)
    Domestic_Amount = models.FloatField(blank=True, null=True)
    UDF1 = models.CharField(max_length=300, blank=True, null=True)
    UDF2 = models.CharField(max_length=300, blank=True, null=True)
    UDF3 = models.CharField(max_length=300, blank=True, null=True)
    UDF4 = models.CharField(max_length=300, blank=True, null=True)
    UDF5 = models.CharField(max_length=300, blank=True, null=True)
    UDF6 = models.CharField(max_length=300, blank=True, null=True)
    GST_Number = models.CharField(max_length=50, blank=True, null=True)
    Credit_Debit_Amount = models.CharField(max_length=6, blank=True, null=True) 


    class Meta:
        indexes = [
            models.Index(fields=['Order_Id', 'Transaction_Id']), 
            # Retain this index if it's useful for query performance but note it does not enforce uniqueness.
        ]

    def __str__(self):
        return self.Order_Id

    # def clean(self):
    #     # Add your validation logic if needed
    #     pass

    # @classmethod
    # def bulk_create_transactions(cls, transactions):
    #     # Previous duplicate checking and exclusion logic based on Order_Id is removed.
        
    #     if transactions:
    #         batch_size = 1000
    #         try:
    #             for i in range(0, len(transactions), batch_size):
    #                 cls.objects.bulk_create(
    #                     [cls(**transaction) for transaction in transactions[i:i + batch_size]],
    #                     batch_size=batch_size,
    #                     ignore_conflicts=True
    #                 )
    #         except Exception as ex:
    #             logger.error(f"Error during bulk create: {str(ex)}")
    #             raise

    #     return len(transactions)

