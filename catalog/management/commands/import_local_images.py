from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Product


class Command(BaseCommand):
    help = "Attach local images from assets/product_images to products by slugified name"

    def add_arguments(self, parser):
        parser.add_argument('--dir', default='assets/product_images', help='Directory with product images')

    def handle(self, *args, **options):
        assets_dir = Path(options['dir'])
        if not assets_dir.exists():
            self.stdout.write(self.style.WARNING(f"Directory {assets_dir} does not exist. Create it and add images."))
            return

        supported_exts = {'.jpg', '.jpeg', '.png', '.webp'}
        files = [p for p in assets_dir.iterdir() if p.suffix.lower() in supported_exts]
        if not files:
            self.stdout.write(self.style.WARNING("No image files found. Supported: .jpg .jpeg .png .webp"))
            return

        attached = 0
        skipped = 0
        for product in Product.objects.all():
            slug = slugify(product.name)
            match = next((p for p in files if p.stem.lower() == slug), None)
            if not match:
                skipped += 1
                continue
            with match.open('rb') as fh:
                product.image.save(match.name, File(fh), save=True)
                attached += 1

        self.stdout.write(self.style.SUCCESS(f"Attached {attached} images. Skipped {skipped} (no matching file)."))


