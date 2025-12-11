import os
from typing import List, Optional

from .config import settings


def list_images() -> List[str]:
    folder = settings.image_folder

    # تأكد أن المجلد موجود
    if not os.path.isdir(folder):
        print("Image folder NOT FOUND:", folder)
        return []

    # نضيف كل الامتدادات المطلوبة بما فيها JFIF
    VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".jfif")

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(VALID_EXTENSIONS)
    ]

    files.sort()
    return files


class ImageCursor:
    def __init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        """إعادة تحميل الصور من المجلد في حال تمت الإضافة."""
        self.images = list_images()
        self.index = -1

    def next(self) -> Optional[str]:
        """إرجاع الصورة التالية."""
        if not self.images:
            return None
        self.index = (self.index + 1) % len(self.images)
        return self.images[self.index]

    def current(self) -> Optional[str]:
        """إرجاع الصورة الحالية بدون تغيير الفهرس."""
        if not self.images or self.index < 0:
            return None
        return self.images[self.index]
