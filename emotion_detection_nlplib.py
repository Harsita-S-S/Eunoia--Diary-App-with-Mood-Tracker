import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER Lexicon (only needed once)
nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

# Expanded Emotion Dictionary with 27 Distinct Emotions
EMOTION_KEYWORDS = {
    "angry": ["angry", "mad", "furious", "irritated", "annoyed", "pissed", "raging", "frustrated"],
    "shame": ["ashamed", "guilty", "embarrassed", "humiliated", "disgraced", "regretful"],
    "anxiety": ["anxious", "worried", "nervous", "stressed", "overthinking", "panic", "restless", "uneasy"],
    "satisfaction": ["satisfied", "content", "pleased", "fulfilled", "grateful", "relieved", "proud"],
    "fear": ["afraid", "scared", "terrified", "frightened", "worried", "panicked"],
    "surprise": ["surprised", "shocked", "amazed", "astonished", "startled"],
    "disgust": ["disgusted", "revolted", "grossed", "nauseated"],
    "excitement": ["excited", "thrilled", "elated", "eager", "ecstatic"],
    "love": ["love", "loving", "affection", "romantic", "kissed", "hug", "caring", "adore", "crush"],
    "joy": ["joy", "delighted", "cheerful", "gleeful", "merry", "overjoyed"],
    "hope": ["hopeful", "optimistic", "encouraged", "positive"],
    "loneliness": ["lonely", "isolated", "abandoned", "alone"],
    "boredom": ["bored", "uninterested", "apathetic", "listless"],
    "jealousy": ["jealous", "envious", "covetous", "resentful"],
    "guilt": ["guilty", "regretful", "remorseful"],
    "pride": ["proud", "accomplished", "successful", "confident"],
    "hurt": ["hurt", "wounded", "offended", "betrayed"],
    "calm": ["calm", "peaceful", "tranquil", "relaxed"],
    "determined": ["determined", "driven", "persistent", "motivated"],
    "grief": ["grieving", "mourning", "heartbroken", "devastated"],
    "relief": ["relieved", "assured", "secure", "comforted"],
    "trust": ["trusting", "faithful", "reliable", "dependable"],
    "curiosity": ["curious", "inquiring", "questioning", "interested"],
    "gratitude": ["grateful", "thankful", "appreciative"],
    "embarrassment": ["embarrassed", "awkward", "self-conscious"],
    "compassion": ["compassionate", "sympathetic", "kind-hearted"]
}

# Common Negation Words
NEGATION_WORDS = {"not", "never", "no", "none", "nobody", "nowhere", "nothing", "hardly", "barely", 
                  "doesn't", "isn't", "wasn't", "shouldn't", "can't", "won't", "don't"}

def preprocess_text(text):
    """Cleans and tokenizes text for better processing."""
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower().strip())
    return text.split()

def detect_emotion(words):
    """Detects emotions based on keyword matching."""
    return next((emotion for emotion, keywords in EMOTION_KEYWORDS.items() if any(word in keywords for word in words)), None)
def get_sentiment_score(text):
    return sia.polarity_scores(text)
def analyze_mood(text):
    """Performs sentiment analysis with expanded emotion detection using VADER."""
    words = preprocess_text(text)
    if not words:
        return "😶 Unable to determine mood (Empty or unclear input)"

    sentiment_scores = get_sentiment_score(text)
    compound = sentiment_scores['compound']
    detected_emotion = detect_emotion(words)
    
    if detected_emotion:
        return f"{detected_emotion.capitalize()} "
    
    if compound >= 0.6:
        return "😁 Very Happy!"
    elif 0.2 <= compound < 0.6:
        return "😊 Slightly Happy"
    elif -0.2 <= compound < 0.2:
        return "😐 Neutral / Mixed Feelings"
    elif -0.6 <= compound < -0.2:
        return "😔 Slightly Sad"
    else:
        return "😭 Very Sad!"

