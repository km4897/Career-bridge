from django.core.management.base import BaseCommand
from django.utils import timezone

from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Marks opportunities as inactive once their posting duration has elapsed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be closed without actually changing anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        candidates = Opportunity.objects.filter(is_active=True)
        expired = [opp for opp in candidates if opp.is_expired]

        if not expired:
            self.stdout.write(self.style.SUCCESS("No expired opportunities found."))
            return

        for opp in expired:
            self.stdout.write(
                f"{'[DRY RUN] Would close' if dry_run else 'Closing'}: "
                f"'{opp.title}' (posted {opp.created_at:%Y-%m-%d}, "
                f"duration {opp.duration_weeks} weeks, expired {opp.expires_at:%Y-%m-%d})"
            )

        if not dry_run:
            ids = [opp.id for opp in expired]
            Opportunity.objects.filter(id__in=ids).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f"Closed {len(expired)} expired opportunity(ies)."))
        else:
            self.stdout.write(self.style.WARNING(f"{len(expired)} opportunity(ies) would be closed."))
