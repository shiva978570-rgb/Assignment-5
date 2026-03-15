"""
ReviewPredict - Flipkart Sentiment Analyzer
Author : Shivam yogi | B.Tech CSE 2nd Year | Data Science
Email  : yogishivam2003@gmail.com
Phone  : +91 9785704626

HOW TO RUN:
  1. pip install flask nltk scikit-learn
  2. Keep tfidf.pkl and model.pkl in same folder as app.py
  3. python app.py
  4. Open http://localhost:5000
"""



from flask import Flask, render_template, request, redirect, url_for, session
import pickle, re, os
from datetime import date
from collections import Counter
import nltk

# --- NLTK setup ---
# Flask app ke andar hi ek folder ban jayega 'nltk_data' taaki baar-baar download na ho
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
nltk_path = os.path.join(BASE_DIR, 'nltk_data')
if not os.path.exists(nltk_path):
    os.makedirs(nltk_path)
nltk.data.path.append(nltk_path)

def download_nltk():
    packages = ['stopwords', 'punkt', 'wordnet', 'omw-1.4', 'punkt_tab']
    for pkg in packages:
        try:
            nltk.download(pkg, download_dir=nltk_path, quiet=True)
        except Exception as e:
            print(f"Error downloading {pkg}: {e}")

download_nltk()

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

# --- Flask App ---
app = Flask(__name__)
app.secret_key = 'reviewpredict_secret_key_2024'

# --- Load Saved Model & TF-IDF ---
try:
    tfidf_path = os.path.join(BASE_DIR, 'tfidf.pkl')
    model_path = os.path.join(BASE_DIR, 'model.pkl')
    
    if os.path.exists(tfidf_path) and os.path.exists(model_path):
        with open(tfidf_path, 'rb') as f:
            tfidf = pickle.load(f)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        MODEL_LOADED = True
        print("[INFO] Model and TF-IDF loaded successfully.")
    else:
        MODEL_LOADED = False
        print("[WARNING] .pkl files missing. Running in DEMO mode.")
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    MODEL_LOADED = False
    tfidf = None
    model = None

# --- NLP Functions ---
STOP_WORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
NEGATIONS = ["not", "no", "never", "n't"]
EMOJI_MAP = {
    "😍": "love", "😊": "happy", "😡": "angry", "😢": "sad",
    "👌": "great", "👍": "good", "👎": "bad", "🤩": "amazing",
    "😤": "frustrated", "💔": "disappointed", "🥰": "love", "😠": "angry",
}

def replace_emojis(text):
    for emoji, word in EMOJI_MAP.items():
        text = text.replace(emoji, word)
    return text

def clean_text(text):
    text = replace_emojis(str(text))
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(words)

def handle_negation(text):
    words = text.split()
    result = []
    for i in range(len(words) - 1):
        if words[i] in NEGATIONS:
            result.append(words[i] + "_" + words[i + 1])
        else:
            result.append(words[i])
    if words:
        result.append(words[-1])
    return " ".join(result)

def lemmatize_text(text):
    return " ".join(lemmatizer.lemmatize(w) for w in text.split())

def preprocess(text):
    text = clean_text(text)
    text = handle_negation(text)
    text = lemmatize_text(text)
    return text

def predict_review(review_text):
    if not MODEL_LOADED:
        return {
            'sentiment': 'Positive', 'confidence': 91.5,
            'sentences': [review_text], 'sentence_preds': ['Positive'], 'demo': True,
        }

    sentences = sent_tokenize(review_text)
    clean_sents = [preprocess(s) for s in sentences]
    vectors = tfidf.transform(clean_sents)
    preds = model.predict(vectors)

    final = Counter(preds).most_common(1)[0][0]
    
    label_map = {'positive': 'Positive', 'neutral': 'Neutral', 'negative': 'Negative'}
    final_label = label_map.get(str(final).lower(), str(final).capitalize())
    sent_labels = [label_map.get(str(p).lower(), str(p).capitalize()) for p in preds]

    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(vectors)
        classes = [str(c).lower() for c in model.classes_]
        tgt = str(final).lower()
        idx = classes.index(tgt) if tgt in classes else 0
        confidence = round(float(proba[:, idx].mean()) * 100, 1)
    else:
        confidence = 85.0

    return {
        'sentiment': final_label, 'confidence': confidence,
        'sentences': sentences, 'sentence_preds': sent_labels, 'demo': False,
    }

# --- Data Store & Routes ---
reviews_store = {}

def get_user_reviews():
    return reviews_store.get(session.get('username', ''), [])

def get_stats():
    rv = get_user_reviews()
    return {
        'total': len(rv),
        'positive': sum(1 for r in rv if r['sentiment'] == 'Positive'),
        'neutral': sum(1 for r in rv if r['sentiment'] == 'Neutral'),
        'negative': sum(1 for r in rv if r['sentiment'] == 'Negative'),
    }

@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'username' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username and password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    result, error = None, None
    if request.method == 'POST':
        review_text = request.form.get('review', '').strip()
        if not review_text:
            error = 'Please enter review text.'
        else:
            result = predict_review(review_text)
            u = session['username']
            if u not in reviews_store: reviews_store[u] = []
            reviews_store[u].append({
                'id': len(reviews_store[u]),
                'product': request.form.get('product_name', 'General').strip(),
                'category': request.form.get('category', 'Electronics').strip(),
                'text': review_text,
                'sentiment': result['sentiment'],
                'confidence': result['confidence'],
                'date': date.today().strftime('%d %b %Y'),
            })
    
    return render_template('dashboard.html', 
                           result=result, error=error, stats=get_stats(), 
                           recent=list(reversed(get_user_reviews()[-5:])),
                           username=session['username'], model_loaded=MODEL_LOADED)

@app.route('/myreviews')
def myreviews():
    if 'username' not in session: return redirect(url_for('login'))
    grouped = {}
    for r in get_user_reviews():
        grouped.setdefault(r['product'], []).append(r)
    return render_template('myreviews.html', grouped=grouped, stats=get_stats(), username=session['username'])

@app.route('/delete_review/<int:index>', methods=['POST'])
def delete_review(index):
    rv = reviews_store.get(session.get('username'), [])
    if 0 <= index < len(rv): rv.pop(index)
    return redirect(url_for('myreviews'))

@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username'), model_loaded=MODEL_LOADED)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
