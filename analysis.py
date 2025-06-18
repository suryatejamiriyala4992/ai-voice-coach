from collections import Counter
import whisper
import librosa
import nltk
import parselmouth
import string

nltk.download('punkt')

def analyze_speech(audio_path):
    print("🛠 Inside analyze_speech()")
    print("🔍 Trying to open:", audio_path)

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"]

    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    word_count = len(transcript.split())
    words_per_min = (word_count / duration) * 60

    snd = parselmouth.Sound(audio_path)
    pitch = snd.to_pitch()
    frequencies = pitch.selected_array['frequency']
    nonzero_frequencies = frequencies[frequencies > 0]
    mean_pitch = nonzero_frequencies.mean() if len(nonzero_frequencies) > 0 else 0

    tokens = nltk.word_tokenize(transcript.lower())
    filler_words = ['um', 'uh', 'like', 'you know']
    filler_count = {word: tokens.count(word) for word in filler_words}

    # Filter and count meaningful words
    tokens = [word for word in tokens if word.isalnum() and word not in filler_words]
    full_freq = Counter(tokens)
    word_freq = {word: count for word, count in full_freq.items() if count > 2}

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

    print("✅ Analysis complete. Returning results.")
    return feedback, transcript, word_freq, filler_count
