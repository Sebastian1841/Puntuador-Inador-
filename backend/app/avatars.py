"""Validate and normalize profile pictures before storing them in SQLite."""
import base64
import binascii
import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError


def normalize_avatar(value):
    if not value:
        return ''
    try:
        prefix, encoded = value.split(',', 1)
        if prefix not in ('data:image/png;base64', 'data:image/jpeg;base64', 'data:image/webp;base64'):
            raise ValueError()
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError()
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as source:
                if source.format not in ('PNG', 'JPEG', 'WEBP') or source.width * source.height > 16_000_000:
                    raise ValueError()
                picture = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'), (256, 256))
                output = io.BytesIO()
                picture.save(output, format='JPEG', quality=85)
        return 'data:image/jpeg;base64,' + base64.b64encode(output.getvalue()).decode('ascii')
    except (ValueError, OSError, binascii.Error, UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ValueError('Usa una imagen JPG, PNG o WebP válida de hasta 2 MB.') from error
