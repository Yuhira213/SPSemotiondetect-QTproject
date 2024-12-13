import librosa
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import requests
import numpy as np
import sounddevice as sd
import wavio
from scipy.io import wavfile
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg


class EdgeImpulseUploader:
    """Class to handle uploads to Edge Impulse."""
    def __init__(self, api_key="ei_5a81f1842d9c1695f732b852fd542df24b3205c235cd2186", 
                 api_url="https://ingestion.edgeimpulse.com/api/training/files"):
        self.api_key = api_key
        self.api_url = api_url
        self.label = "suara knalpot motor"  # Default label

    def upload_audio_to_edge_impulse(self, audio_filename):
        try:
            with open(audio_filename, "rb") as f:
                response = requests.post(
                    self.api_url,
                    headers={
                        "x-api-key": self.api_key,
                        "x-label": self.label,
                    },
                    files={"data": (os.path.basename(audio_filename), f, "audio/wav")}, 
                    timeout=30
                )
                if response.status_code == 200:
                    return True, "Uploaded successfully!"
                else:
                    return False, f"Failed: {response.status_code}, {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {e}"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # Layout setup
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # Title Label
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setText("<h3 align='center'>Audio Recorder Connected Edge Impulse Database</h3>")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 1)

        # Group Box for Parameters
        self.groupBox = QtWidgets.QGroupBox("Parameters", self.centralwidget)
        self.gridLayout_parameters = QtWidgets.QGridLayout(self.groupBox)

        # Input Fields
        self.label_sampling_rate = QtWidgets.QLabel("Sampling Rate:")
        self.lineEdit_sampling_rate = QtWidgets.QLineEdit("16000")
        self.label_update_interval = QtWidgets.QLabel("Update Interval (ms):")
        self.lineEdit_update_interval = QtWidgets.QLineEdit("50")
        self.label_label = QtWidgets.QLabel("Label:")
        self.lineEdit_label = QtWidgets.QLineEdit("recording")
        
        # Buttons
        self.pushButton_record = QtWidgets.QPushButton("Start Recording")
        self.pushButton_replay = QtWidgets.QPushButton("Replay Audio")
        self.pushButton_upload = QtWidgets.QPushButton("Upload to Edge Impulse")
        self.pushButton_analyze = QtWidgets.QPushButton("Analyze Audio")
        self.pushButton_emotion = QtWidgets.QPushButton("Detect Emotion")  # Button for emotion detection
        self.pushButton_replay.setEnabled(False)
        self.pushButton_upload.setEnabled(False)
        self.pushButton_analyze.setEnabled(False)

        # Layout for Parameters
        self.gridLayout_parameters.addWidget(self.label_sampling_rate, 0, 0)
        self.gridLayout_parameters.addWidget(self.lineEdit_sampling_rate, 0, 1)
        self.gridLayout_parameters.addWidget(self.label_update_interval, 1, 0)
        self.gridLayout_parameters.addWidget(self.lineEdit_update_interval, 1, 1)
        self.gridLayout_parameters.addWidget(self.label_label, 2, 0)
        self.gridLayout_parameters.addWidget(self.lineEdit_label, 2, 1)
        self.gridLayout_parameters.addWidget(self.pushButton_record, 3, 0, 1, 2)
        self.gridLayout_parameters.addWidget(self.pushButton_replay, 4, 0, 1, 2)
        self.gridLayout_parameters.addWidget(self.pushButton_upload, 5, 0, 1, 2)
        self.gridLayout_parameters.addWidget(self.pushButton_analyze, 6, 0, 1, 2)
        self.gridLayout_parameters.addWidget(self.pushButton_emotion, 7, 0, 1, 2)  # Add emotion detection button
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        # Plot Widgets for Time and Frequency Domain
        self.plot_widget_time = pg.PlotWidget(self.centralwidget)
        self.plot_widget_time.setBackground('w')
        self.plot_widget_time.setTitle("Time Domain Signal")
        self.plot_widget_time.setLabel('bottom', 'Time', units='s')  # Label for x-axis
        self.plot_widget_time.setLabel('left', 'Amplitude')  # Label for y-axis
        self.plot_widget_time.showGrid(x=True, y=True)
        self.gridLayout.addWidget(self.plot_widget_time, 2, 0, 1, 1)

        self.plot_widget_freq = pg.PlotWidget(self.centralwidget)
        self.plot_widget_freq.setBackground('w')
        self.plot_widget_freq.setTitle("Frequency Domain (DFT)")
        self.plot_widget_freq.setLabel('bottom', 'Frequency', units='Hz')  # Label for x-axis
        self.plot_widget_freq.setLabel('left', 'Amplitude')  # Label for y-axis
        self.plot_widget_freq.showGrid(x=True, y=True)
        self.gridLayout.addWidget(self.plot_widget_freq, 3, 0, 1, 1)

        # Initialize plot data
        self.plot_data_time = self.plot_widget_time.plot(pen=pg.mkPen(color='red', width=1))
        self.plot_data_freq = self.plot_widget_freq.plot(pen=pg.mkPen(color='black', width=1))

        MainWindow.setCentralWidget(self.centralwidget)

        # Initialize parameters
        self.is_recording = False
        self.audio_data = []
        self.audio_file_path = "recorded_audio.wav"
        self.uploader = EdgeImpulseUploader()

        # Timer for real-time updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        # Connect buttons to functions
        self.pushButton_record.clicked.connect(self.toggle_recording)
        self.pushButton_replay.clicked.connect(self.replay_audio)
        self.pushButton_upload.clicked.connect(self.upload_to_edge_impulse)
        self.pushButton_analyze.clicked.connect(self.analyze_audio)
        self.pushButton_emotion.clicked.connect(self.detect_emotion)  # Connect emotion detection

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.pushButton_record.setText("Stop Recording")
            self.start_recording()
        else:
            self.is_recording = False
            self.pushButton_record.setText("Start Recording")
            self.stop_recording()

    def start_recording(self):
        self.sampling_rate = int(self.lineEdit_sampling_rate.text())
        self.audio_data = []
        try:
            self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.sampling_rate)
            self.stream.start()
            self.timer.start(int(self.lineEdit_update_interval.text()))
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Error", f"Failed to start recording: {e}")
            self.is_recording = False
            self.pushButton_record.setText("Start Recording")

    def stop_recording(self):
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        self.timer.stop()
        self.save_audio()
        self.pushButton_replay.setEnabled(True)
        self.pushButton_upload.setEnabled(True)
        self.pushButton_analyze.setEnabled(True)

    def save_audio(self):
        if self.audio_data:
            audio_data_np = np.concatenate(self.audio_data)
            wavio.write(self.audio_file_path, audio_data_np, self.sampling_rate, sampwidth=2)

    def replay_audio(self):
        if os.path.exists(self.audio_file_path):
            _, data = wavfile.read(self.audio_file_path)
            sd.play(data, self.sampling_rate)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data.append(indata.copy())

    def update_plot(self):
        if self.audio_data:
            # Update Time Domain Plot
            time_data = np.concatenate(self.audio_data)[:, 0]
            time_axis = np.arange(len(time_data)) / self.sampling_rate  # Time axis in seconds
            self.plot_data_time.setData(time_axis, time_data)

            # Update Frequency Domain Plot
            fft_data = np.fft.fft(time_data)
            freqs = np.fft.fftfreq(len(fft_data), 1/self.sampling_rate)
            positive_freqs = freqs[:len(freqs)//2]  # Only positive frequencies
            positive_fft_data = np.abs(fft_data[:len(fft_data)//2])  # Magnitude of FFT
            self.plot_data_freq.setData(positive_freqs, positive_fft_data)

    def upload_to_edge_impulse(self):
        label = self.lineEdit_label.text()
        if not label:
            QtWidgets.QMessageBox.warning(None, "Error", "Label cannot be empty!")
            return
        self.uploader.label = label
        success, message = self.uploader.upload_audio_to_edge_impulse(self.audio_file_path)
        if success:
            QtWidgets.QMessageBox.information(None, "Success", message)
        else:
            QtWidgets.QMessageBox.warning(None, "Error", message)

    def analyze_audio(self):
        if os.path.exists(self.audio_file_path):
            analyze_audio(self.audio_file_path)

    def detect_emotion(self):
        if os.path.exists(self.audio_file_path):
            y, sr = librosa.load(self.audio_file_path, sr=16000)
            rms = np.sqrt(np.mean(librosa.feature.rms(y=y)**2))
            if rms > 0.06:  # Arbitrary threshold; tune as needed
                QtWidgets.QMessageBox.information(None, "Emotion Detected", "Detected Emotion: MARAH")
            else:
                QtWidgets.QMessageBox.information(None, "Emotion Detected", "Detected Emotion: NETRAL")


def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch = pitches[pitches > 0]
    mean_pitch = np.mean(pitch) if len(pitch) > 0 else 0
    pitch_range = np.max(pitch) - np.min(pitch) if len(pitch) > 0 else 0
    rms = librosa.feature.rms(y=y)[0]
    mean_intensity = np.mean(rms)
    max_intensity = np.max(rms)

    # Handle tempo to ensure it's a scalar
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]  # Use the first value if tempo is an array
    tempo = float(tempo)  # Ensure tempo is a float

    duration = librosa.get_duration(y=y, sr=sr)

    analysis_message = (
        f"Analysis Results for {file_path}:\n"
        f"  Mean Pitch: {mean_pitch:.2f} Hz\n"
        f"  Pitch Range: {pitch_range:.2f} Hz\n"
        f"  Mean RMS Intensity: {mean_intensity:.4f}\n"
        f"  Max RMS Intensity: {max_intensity:.4f}\n"
        f"  Tempo: {tempo:.2f} BPM\n"
        f"  Duration: {duration:.2f} seconds"
    )

    print(analysis_message)  # Print to terminal
    return analysis_message



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
