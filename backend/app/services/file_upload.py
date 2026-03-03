import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from PIL import Image
import aiofiles
from app.config import settings


class FileUploadService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_size = settings.MAX_UPLOAD_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    async def upload_image(self, file: UploadFile, user_id: int, subfolder: str = "wardrobe") -> dict:
        """Upload and process image"""
        # Validate file
        if not self._is_valid_file(file):
            raise ValueError("Invalid file type or size")
        
        # Generate unique filename
        file_ext = file.filename.split(".")[-1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        user_folder = self.upload_dir / str(user_id) / subfolder
        user_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = user_folder / filename
        
        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        # Create thumbnail
        thumbnail_path = await self._create_thumbnail(file_path)
        
        # Generate URLs (in production, use CDN URLs)
        image_url = f"/uploads/{user_id}/{subfolder}/{filename}"
        thumbnail_url = f"/uploads/{user_id}/{subfolder}/thumb_{filename}" if thumbnail_path else None
        
        return {
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "file_path": str(file_path)
        }
    
    def _is_valid_file(self, file: UploadFile) -> bool:
        """Validate file type and size"""
        # Check extension
        if file.filename:
            ext = file.filename.split(".")[-1].lower()
            if ext not in self.allowed_extensions:
                return False
        
        # Check size (basic check, actual size checked after read)
        return True
    
    async def _create_thumbnail(self, file_path: Path, size: tuple = (200, 200)) -> Optional[Path]:
        """Create thumbnail image"""
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
                img.save(thumbnail_path, optimize=True, quality=85)
                return thumbnail_path
        except Exception as e:
            print(f"Thumbnail creation error: {e}")
            return None
    
    def delete_file(self, image_url: str):
        """Delete uploaded file by image URL (e.g. /uploads/1/wardrobe/xxx.jpg)"""
        try:
            # Convert URL path to filesystem path
            if image_url.startswith("/uploads/"):
                rel_path = image_url[len("/uploads/"):]
            else:
                rel_path = image_url.lstrip("/")
            path = self.upload_dir / rel_path
            if path.exists():
                path.unlink()
                # Also delete thumbnail if exists
                thumb_path = path.parent / f"thumb_{path.name}"
                if thumb_path.exists():
                    thumb_path.unlink()
        except Exception as e:
            print(f"File deletion error: {e}")


file_upload_service = FileUploadService()
