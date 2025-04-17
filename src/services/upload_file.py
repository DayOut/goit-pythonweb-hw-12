import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initializing the service for uploading files to Cloudinary.

        Arguments:
            cloud_name: The name of the cloud in Cloudinary.
            api_key: API key to access Cloudinary.
            api_secret: API secret to access Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads a file to Cloudinary and generates a URL to access the image.

        Generates a unique identifier for the user and uploads the file to the server.
        After successful upload, returns the URL of the image with certain parameters (size, cropping).

        Arguments:
            file: The file to upload.
            username: The username to generate a unique public_id.

        Returns:
            str: URL of the image available on Cloudinary.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url