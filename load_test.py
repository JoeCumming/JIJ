from youtube_video_upload import upload_from_options

upload_from_options({    
    "secrets_path" : "./instance/client_secrets.json",
    "credentials_path" : "./instance/credentials.json",    
    "videos" :[ {
            "title":  "Sample",
            "file":  "./img/sample.mp4",
            "description": "sdf",
            "category": 22,
            "privacy": "private"
    }]
})