# signals.py is invoked by app.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from bereikbaarheid.resources.utils import refresh_materialized

from .models import Lastbeperking, VerkeersBord, Verrijking


@receiver(post_save, sender=Lastbeperking)
@receiver(post_save, sender=VerkeersBord)
@receiver(post_save, sender=Verrijking)
def import_post_save(sender, instance, **kwargs):
    """When add/change by admin-panel: Refresh materialized views"""

    if hasattr(instance, "dry_run"):
        # existence of dry_run is signal that instance is created by import-export
        # refresh materialized views are handled in resource
        if instance.dry_run:
            # dry_run true -> doesn't need save
            return

    else:
        # instance is created by add/change
        refresh_materialized("bereikbaarheid_out_vma_undirected")
        refresh_materialized("bereikbaarheid_out_vma_directed")
        refresh_materialized("bereikbaarheid_out_vma_node")
