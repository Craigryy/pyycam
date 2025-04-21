from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Updates the Site domain to match production settings'

    def handle(self, *args, **options):
        site_domain = getattr(settings, 'SITE_DOMAIN', 'pyycam.onrender.com')
        site_name = getattr(settings, 'SITE_NAME', 'PyyCam')

        # Update the default site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': site_domain,
                'name': site_name
            }
        )

        if not created:
            site.domain = site_domain
            site.name = site_name
            site.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated site to {site_domain}'))
