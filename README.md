# Video Bot

## Overview
This bot downloads videos from Instagram and TikTok and uploads them to a server using provided APIs.

## Requirements
- Python 3.x
- Install dependencies using `pip install -r requirements.txt`

## Usage
1. Place your videos in the `/videos` directory.
2. Run the bot using `python main.py`.
3. The bot will monitor the directory for new `.mp4` files and upload them automatically.

## API Integration
- **Get Upload URL**:
  - **Method**: GET
  - **Endpoint**: `https://api.socialverseapp.com/posts/generate-upload-url`
  - **Headers**:
    - `Flic-Token`: `<YOUR_TOKEN>`
    - `Content-Type`: `application/json`
  
- **Upload Video**:
  - **Method**: PUT
  - **Description**: Use the pre-signed URL obtained from the previous step to upload the video.

- **Create Post**:
  - **Method**: POST
  - **Endpoint**: `https://api.socialverseapp.com/posts`
  - **Headers**:
    - `Flic-Token`: `<YOUR_TOKEN>`
    - `Content-Type`: `application/json`
  - **Body**:
    ```json
    {
      "title": "<video title>",
      "hash": "<hash from Step 1>",
      "is_available_in_public_feed": false,
      "category_id": <category_id>
    }
    ```
