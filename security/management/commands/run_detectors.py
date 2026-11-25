from django.core.management.base import BaseCommand
from security.anomaly_engine import run_anomaly_detectors

class Command(BaseCommand):
    help = "Run BhuRaksha rule-based anomaly & fraud detection engine."

    def handle(self, *args, **options):
        self.stdout.write("Scanning cadastral database for anomalous activity...")
        alerts = run_anomaly_detectors()
        self.stdout.write(self.style.SUCCESS(f"Scan complete. {len(alerts)} new security alerts generated."))
