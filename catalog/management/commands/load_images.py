import io
from pathlib import Path

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Product


class Command(BaseCommand):
    help = "Download and attach relevant placeholder images to products using keyword queries"

    def add_arguments(self, parser):
        parser.add_argument('--size', default='800x800', help='Image size WxH, default 800x800')
        parser.add_argument('--force', action='store_true', help='Replace existing images')

    def _tags_for_product(self, product: Product) -> str:
        name = product.name.lower()
        category = (product.category.name if product.category_id else '').lower()

        # Electronics
        if 'iphone' in name or 'phone' in name:
            return 'smartphone,apple,device'
        if 'samsung' in name or 'galaxy' in name:
            return 'smartphone,android,device'
        if 'laptop' in name or 'xps' in name or 'dell' in name:
            return 'laptop,computer,ultrabook'

        # Fashion
        if 'shirt' in name:
            return 'mens,shirt,clothing,apparel'
        if 'pants' in name or 'chinos' in name:
            return 'mens,pants,trousers,clothing'
        if 'shoes' in name or 'sneakers' in name:
            return 'mens,shoes,footwear'
        if 'hoodie' in name:
            return 'mens,hoodie,apparel'

        # Home & Kitchen
        if 'air fryer' in name or 'fryer' in name:
            return 'air,fryer,kitchen,appliance'

        # Fallback by category
        if 'electronics' in category:
            return 'electronics,gadget,tech'
        if 'fashion' in category:
            return 'fashion,apparel,clothing'
        if 'home' in category:
            return 'home,kitchen,appliance'

        return 'product,retail,store'

    def handle(self, *args, **options):
        width, height = (int(x) for x in options['size'].lower().split('x'))
        force = options['force']

        media_dir = Path('media') / 'products'
        media_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for product in Product.objects.all():
            if product.image and not force:
                continue

            seed = slugify(product.name) or 'product'
            tags = self._tags_for_product(product)
            # Use Unsplash source (no API key) with keyword queries
            query = tags.replace(',', ',')
            url = f'https://source.unsplash.com/{width}x{height}/?{query}'

            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"Failed to fetch image for {product.name}: {exc}"))
                continue

            image_bytes = io.BytesIO(resp.content)
            filename = f"{seed}.jpg"
            product.image.save(filename, ContentFile(image_bytes.getvalue()), save=True)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Attached/updated images for {count} products"))


