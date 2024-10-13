#creator
import googleapiclient.discovery
import googleapiclient.errors
import string
from collections import Counter
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from youtube_transcript_api import YouTubeTranscriptApi
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyDhrhGBGYGk1qCkYfqSb3duMM3-bjt9OCk"
def extract_video_id(url):
    # Check if the URL is a short YouTube link
    if "youtu.be/" in url:
        # Split the URL by 'youtu.be/' and take the part after it
        return url.split("youtu.be/")[1][:11]
    # Check if the URL is a normal YouTube link
    if "youtube.com/watch?v=" in url:
        # Split the URL by 'v=' and take the part after it
        return url.split("v=")[1][:11]
    # In case of extra parameters in the URL, use '&' as a delimiter
    if "&" in url:
        return url.split("v=")[1].split("&")[0]
    # Return None if the video ID couldn't be extracted
    print("invalid video link")
    return None
vid=extract_video_id(input("Enter a valid Youtube video link "))
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)
request = youtube.videos().list(
    part="snippet",
    id=vid
)
response = request.execute()
with open('read1.txt', 'w', encoding='utf-8') as f:
    f.write("\ntags\n")
    l=response['items'][0]['snippet']['tags']
    for tags in l:
        f.write(tags+'\n')
    f.close()
with open('read1.txt', 'a', encoding='utf-8') as f:
    f.write("\ntitle\n")
    for item in response['items']:
        f.write(item['snippet']['title']+'\n')
    f.close()
with open('read1.txt', 'a', encoding='utf-8') as f:
    f.write("\ndescription\n")
    for item in response['items']:
        f.write(item['snippet']['description']+'\n')
    f.close()
try:
    transcript = YouTubeTranscriptApi.get_transcript(vid)
    with open('read1.txt', 'a', encoding='utf-8') as f:
        f.write("\ntranscript\n")
        for entry in transcript:
            f.write(f"{entry['text']}"+'\n')
        f.close()
except Exception as e:
    print(f"An error occurred: {e}")
text = open('read1.txt', encoding='utf-8').read()
lower_case = text.lower()
cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))
# Using word_tokenize because it's faster than split()
tokenized_words = word_tokenize(cleaned_text, "english")
# Removing Stop Words
final_words = []
for word in tokenized_words:
    if word not in stopwords.words('english'):
        final_words.append(word)
# Lemmatization - From plural to single + Base form of a word (example better-> good)
lemma_words = []
for word in final_words:
    word = WordNetLemmatizer().lemmatize(word)
    lemma_words.append(word)
emotion_list = []
with open('emotion.txt', 'r') as file:
    for line in file:
        clear_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
        word, emotion = clear_line.split(':')
        if word in lemma_words:
            emotion_list.append(emotion)
print(emotion_list)
w = Counter(emotion_list)
print(w)
def sentiment_analyse1(sentiment_text):
    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
    if score['neg'] > score['pos']:
        print("Overall Creator sentiments : Negative Sentiment")
    elif score['neg'] < score['pos']:
        print("Overall Creator sentiments : Positive Sentiment")
    else:
        print("Overall Creator sentiments : Neutral Sentiment")
sentiment_analyse1(cleaned_text)
fig, ax1 = plt.subplots()
ax1.bar(w.keys(), w.values())
fig.autofmt_xdate()
plt.savefig('graph.png')
plt.show()