import os
import logging
import tracemalloc
import asyncio
import aiohttp
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

import requests
import logging
import os

async def upload_to_instagram(access_token, media_file_path):
    user_id = 'vamshik_nayak'  # Replace with your Instagram user ID
    url = f"https://graph-video.facebook.com/v12.0/{user_id}/media"
    
    with open(media_file_path, 'rb') as media_file:
        payload = {
            'access_token': access_token,
            'media_type': 'IMAGE',  # or 'IMAGE' for posts
            'IMAGE': media_file
        }
        
        response = requests.post(url, files=payload)
        if response.status_code == 200:
            logging.info("Upload successful: %s", response.json())
        else:
            logging.error("Error uploading: %s", response.json())

async def main():
    access_token = 'your_access_token'  # Replace with your actual access token
    media_file_path = 'videos/video1.mp4'  # Path to the video you want to upload

    await upload_to_instagram(access_token, media_file_path)

# Ensure to run the main function in an async context
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Directory to monitor
VIDEO_DIR = 'C:/Users/vamsh/Desktop/video-bot/videos/'

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.mp4'):
            print(f'New video detected: {event.src_path}')  # Added print statement
            logging.info(f'New video detected: {event.src_path}')
            asyncio.run(upload_video(event.src_path))

async def upload_video(file_path: str):
    logging.info(f'Starting upload for video: {file_path} (type: {type(file_path)})')
    retries = 3
    for attempt in range(retries):
        try:
            # Get upload URL
            upload_url = await get_upload_url()
            # Upload video
            await upload_to_server(upload_url, file_path)
            # Delete local file after upload
            os.remove(file_path)
            logging.info(f'Successfully uploaded and deleted local file: {file_path}')
            break  # Exit the loop if upload is successful
        except aiohttp.ClientError as e:
            logging.error(f'Network error occurred: {e}. Attempt {attempt + 1} of {retries}.')
            if attempt < retries - 1:
                logging.info(f'Retrying upload... (Attempt {attempt + 2}/{retries})')
        except FileNotFoundError:
            logging.error(f'File not found: {file_path}')
            break  # Exit the loop if the file is not found
        except Exception as e:
            logging.error(f'Error uploading video: {e}')
            break

async def get_upload_url():
    flic_token = os.getenv('FLIC_TOKEN')
    if not flic_token:
        logging.error('Flic-Token is not set. Please set the FLIC_TOKEN environment variable.')
        raise Exception('Flic-Token is not set.')

    logging.info(f'Obtaining upload URL...')
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.socialverseapp.com/posts/generate-upload-url', headers={
            "Flic-Token": flic_token,
            "Content-Type": "application/json"
        }) as response:
            if response.status != 200:
                logging.error(f'Failed to get upload URL: {response.status}')
                raise Exception('Failed to get upload URL')
            response_text = await response.text()
            logging.info(f'Raw response from upload URL API: {response_text}')
            upload_url = str(response_text)
            logging.info(f'Upload URL obtained: {upload_url}')
            if not isinstance(upload_url, str):
                logging.error(f'Upload URL is not a string: {upload_url} (type: {type(upload_url)})')
                raise Exception('Upload URL must be a string')
            return upload_url

async def upload_to_server(upload_url, file_path):
    logging.info(f'Uploading video to URL: {upload_url} (type: {type(upload_url)})')
    logging.info(f'File path: {file_path} (type: {type(file_path)})')
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            async with session.put(upload_url, data=f) as response:
                logging.info(f'Response status: {response.status}')
                if response.status == 200:
                    logging.info(f'Successfully uploaded {file_path}')
                elif response.status == 400:
                    logging.error(f'Bad Request: {response.status}. Check the file size or upload URL.')
                elif response.status == 401:
                    logging.error(f'Unauthorized: {response.status}. Check your authentication token.')
                elif response.status == 403:
                    logging.error(f'Forbidden: {response.status}. You do not have permission to upload.')
                elif response.status == 404:
                    logging.error(f'Not Found: {response.status}. The upload URL may be incorrect.')
                elif response.status == 500:
                    logging.error(f'Internal Server Error: {response.status}. There may be an issue with the server.')
                else:
                    response_text = await response.text()
                    logging.error(f'Failed to upload {file_path}: {response.status}, Response: {response_text}')

async def monitor_directory():
    print("Monitoring directory for new video files...")  # Added print statement
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, VIDEO_DIR, recursive=False)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)  # Ensure this is awaited
    except KeyboardInterrupt:
        logging.info("Stopping directory monitoring...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    tracemalloc.start()
    logging.info("Memory tracking started.")
    asyncio.run(monitor_directory())  # Await the monitor_directory function
