from django.core.management.base import BaseCommand
from learning.models import Video

class Command(BaseCommand):
    help = 'Transcribe videos and populate the database'

    def handle(self, *args, **options):
        self.stdout.write("Starting to transcribe videos...")
        # Place your transcription logic here
        # For example, you can call a function defined in transcript.py
        from learning.transcript import main
        main()
        self.stdout.write("Finished transcribing videos.")
