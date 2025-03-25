class VideoMetadataStore:
    metadata = None  # Static variable to store metadata

    @classmethod
    def set_metadata(cls, data):
        cls.metadata = data

    @classmethod
    def get_metadata(cls):
        return cls.metadata