from django.core.management.base import BaseCommand
from payment.models import SubscriptionCode
import os

class Command(BaseCommand):
    help = 'Load hex codes from .txt files and add them to the database.'

    def handle(self, *args, **kwargs):
        # Define file paths and their corresponding subscription lengths
        files_with_lengths = [
            ("C:\\Users\\bdrkh\\Downloads\\1month.txt", 1),
            ("C:\\Users\\bdrkh\\Downloads\\6month.txt", 6),
            ("C:\\Users\\bdrkh\\Downloads\\1year.txt", 12)
        ]

        for file_path, length in files_with_lengths:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    codes = file.readlines()
                    # Iterate through each code and add it to the database
                    for code in codes:
                        code = code.strip()  # Remove any extra whitespace/newline characters
                        if len(code) == 16:  # Ensure it's a valid 16-character hex code
                            SubscriptionCode.objects.create(
                                hex_code=code,
                                subscription_length=length
                            )
                self.stdout.write(self.style.SUCCESS(f"Successfully loaded codes from {file_path}"))
            else:
                self.stdout.write(self.style.ERROR(f"File {file_path} does not exist"))
