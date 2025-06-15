import os
import whisper
import librosa
import nltk
import parselmouth
from collections import Counter
from pydub import AudioSegment

nltk.download('punkt')

def analyze_speech(audio_path):
    print("🛠 Inside analyze_speech()")
    print("🔍 Trying to open:", audio_path)
    print("🔍 File exists:", os.path.exists(audio_path))

    # 🔄 Convert to .wav if not already
    if not audio_path.lower().endswith('.wav'):
        print("🔁 Converting to WAV format")
        audio = AudioSegment.from_file(audio_path)
        audio_path_wav = audio_path.rsplit('.', 1)[0] + "_converted.wav"
        audio.export(audio_path_wav, format="wav")
        audio_path = audio_path_wav
        print("✅ Converted path:", audio_path)

    # 🔊 Transcription
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"]
    print("📜 Transcript extracted")

    # 🎯 Pace analysis
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    word_count = len(transcript.split())
    words_per_min = (word_count / duration) * 60

    # 🎵 Pitch analysis
    snd = parselmouth.Sound(audio_path)
    pitch = snd.to_pitch()
    frequencies = pitch.selected_array['frequency']
    nonzero_frequencies = frequencies[frequencies > 0]
    mean_pitch = nonzero_frequencies.mean() if len(nonzero_frequencies) > 0 else 0

    # 🤖 Filler word detection
    tokens = nltk.word_tokenize(transcript.lower())
    filler_words = ['um', 'uh', 'like', 'you know']
    filler_count = {word: tokens.count(word) for word in filler_words}

    # 📈 Feedback generation
    feedback = []

    if words_per_min > 160:
        feedback.append("You're speaking a bit fast. Aim for 130–150 words per minute.")
    elif words_per_min < 100:
        feedback.append("Your pace is a little slow. Try speaking more energetically.")
    else:
        feedback.append("Your speaking pace is well-balanced.")

    for word, count in filler_count.items():
        if count > 3:
            feedback.append(f"Try reducing the use of filler word '{word}' — used {count} times.")

    if mean_pitch < 120:
        feedback.append("Your tone seems flat. Add more vocal variety.")
    elif mean_pitch > 200:
        feedback.append("Strong vocal energy! Keep it up.")
    else:
        feedback.append("Your tone sounds balanced and natural.")

    return feedback, transcript
