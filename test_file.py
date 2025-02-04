from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import cv2
import os


# Authenticate and create a GoogleDrive instance
# def authenticate_drive():
#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth()  # Authenticates via browser
#     return GoogleDrive(gauth)

def authenticate_drive():
    gauth = GoogleAuth(settings_file='/mnt/c/Users/mrvag/Downloads/settings.yaml')
    # gauth.LocalWebserverAuth(port_numbers=[8080])  # Use a valid port
    gauth.CommandLineAuth()  # This will prompt the user to authenticate via the terminal
    drive = GoogleDrive(gauth)
    return drive
    # gauth.CommandLineAuth()
    # gauth.LoadClientConfigFile("C:\Users\mrvag\Downloads\client_secret.json")  # Use the correct path here
    # gauth.LoadClientConfigFile( '/mnt/c/Users/mrvag/Downloads/client_secret_753561154903-mrvhjq1fdb3kjfdn048upatdlun3lu2p.apps.googleusercontent.com.json')
    # gauth.CommandLineAuth( '/mnt/c/Users/mrvag/Downloads/client_secret_753561154903-mrvhjq1fdb3kjfdn048upatdlun3lu2p.apps.googleusercontent.com.json')
    # gauth.LoadClientConfigFile()  # Authenticates via browser

# Download video from Google Drive
def download_video(drive, file_id, output_path):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(output_path)
    print(f"Video downloaded to: {output_path}")


# Play video using OpenCV
def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Video Player", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    # Authenticate with Google Drive
    drive = authenticate_drive()

    # Replace 'your_file_id' with the actual Google Drive file ID
    file_id = 'your_file_id_here'
    video_path = "video.mp4"

    # Download the video
    download_video(drive, file_id, video_path)

    # Play the video
    play_video(video_path)

    # Clean up the downloaded file
    os.remove(video_path)
    print("Temporary video file deleted.")


if __name__ == "__main__":
    main()
