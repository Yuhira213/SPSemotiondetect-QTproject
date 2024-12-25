![Project UI](https://github.com/user-attachments/assets/04f62db9-193c-4529-8ae9-c358e06006f3)
# Voice Recorder with Audio Analyzer and Emotion Detector. Connected to EdgeImpulse

This project demonstrates how to build a PyQt6 application for voice recording Audio Analyzer and Emotion Detector, which can upload the recorded audio to EdgeImpulse for Audio Training.

## Authors
1. Yudhistira Ananda Kuswantoro (2042231015)
2. Aireka Maulana Erawan (2042231047)
3. M Daffi Aryatama (2042231075)

## Features
1. **Voice Recording and Replay** : You can record audio from your audio input device using a simple intuitive GUI, and then you can replay your recorded audio.
2. **Edge Impulse Integration** : Upload your recorded audio to Edge Impulse for deep learning audio models.
3. **Analyze Audio** : Analyze the details of the audio that has been recorded.
4. **Detect Emotion** : Detect a person's emotions from recorded audio.

## Requirements

### Software
1. Python V3.8+
2. PyQt6
3. Edge Impulse Website Ingestion API Key

  ### Hardware
    1. Audio Input Device, e.g. Laptop Microphone

## Installation
### 1. Clone the repository 
```bash
git clone https://github.com/Yuhira213/SPSemotiondetect-QTproject
```

### 2. Open the File named QTProject.py

### 3. Prepare the Edge Impulse Account that want to be integrated to Programs.
```bash
> After creating an account, open the keys page
> Then click Add New API Key > Make sure to change the role to 'Ingestion'
> Then Click 'Create API Key' (make sure to copy the API Key)
```

### 4. Change the API Key of the EdgeImpulse ingestion
**Check the Line 15 of the QTProject.py**
```bash
class EdgeImpulseUploader:
    """Class to handle uploads to Edge Impulse."""
    def __init__(self, api_key="ei_5a81f1842d9c1695f732b852fd542df24b3205c235cd2186", 
                 api_url="https://ingestion.edgeimpulse.com/api/training/files"):
        self.api_key = api_key
        self.api_url = api_url
        self.label = "Recorded Sound"  # Default label
```
**Change the api_key="ei_5a....** to your own Ingestion API Key.


## Usage
### 1. Run the PyQt6 Application
Start the GUI application:
```bash
QTProject.py
```

### 2. Start Recording and Replay Audio
- Use the GUI to to record audio and replay the recorded audio

### 3. Upload to  Edge Impulse
- Use the GUI to Upload recorded audio to Edge Impulse Data Acquisition for Training

### 4. Analyze Audio
- Use the GUI to Analyze the detail of the recorded audio

### 5. Detect Emotion
- Use the GUI to detect a person's emotions from recorded audio.

### 6. Train the Model
- Train a model or Classify with MFCC and Clasifier on Edge Impulse using the uploaded data.

## Future Improvements
- Optimize the analization of the recorded audio.
- Optimize the synchronization between audio sample and detection result to get result that more significant.

## Contributions
Feel free to fork this repository and submit pull requests. Suggestions and improvements are welcome!
