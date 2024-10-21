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
#Viewers
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "Enter Your Developer API Key"
''' 
You can get developer key from google cloud console
OR
Refer to the [How to extract YouTube Comments Using the YouTube API] by [Analytics with Adam] YouTube Video
'''
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)
def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1][:11]
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1][:11]
    if "youtube.com/shorts/" in url:
        return url.split("shorts/")[1][:11]
    if "&" in url:
        return url.split("v=")[1].split("&")[0]
    print("Invalid video link")
    return None
vid=extract_video_id(input("Enter a valid Youtube video link "))
def creators():
    request = youtube.videos().list(
        part="snippet",
        id=vid
    )
    res = request.execute()
    return res
response_c=creators()
def title():
    ti=response_c['items'][0]['snippet']['title']
    return ti
def viewers():
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=vid,
        maxResults=100
    )
    res = request.execute()
    return res
response_v=viewers()
with open('read.txt','w',encoding='utf-8') as f:
    for item in response_v['items']:
        f.write(item['snippet']['topLevelComment']['snippet']['textDisplay']+'\n')
    f.close()
def cleaning_text(rt_text):
    text = open(rt_text, encoding='utf-8').read()
    lower_case = text.lower()
    cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))
    return cleaned_text
def emotions_from_emotions_txt(rt_text):
    cleaned_text=cleaning_text(rt_text)
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
        file.close()
    print(emotion_list)
    w = Counter(emotion_list)
    print(w)
    return w
def sentiment_analyse(app_text):
    sentiment_text=cleaning_text(app_text)
    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
    if score['neg'] > score['pos']:
        return "Negative Sentiment"
    elif score['neg'] < score['pos']:
        return "Positive Sentiment"
    else:
        return "Neutral Sentiment"
def graph_plot(file_path, label, whose):
    emotions = emotions_from_emotions_txt(file_path)

    # Calculate total emotions to convert counts to percentages
    total_count = sum(emotions.values())
    percentages = {k: (v / total_count) * 100 for k, v in emotions.items()}

    # Create the bar graph (no change in figure size)
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('black')  # Figure background color
    ax.set_facecolor('black')

    # Plot bars with emotion percentages
    bars = ax.bar(percentages.keys(), percentages.values(), color='#00FF00')

    # Adjust y-limit to provide space for the labels above the bars
    ax.set_ylim(0, max(percentages.values()) * 1.2)  # Increase y-axis limit by 20%

    # Customize axis line colors using spines
    ax.spines['left'].set_color('white')  # Y-axis line color
    ax.spines['bottom'].set_color('white')  # X-axis line color
    ax.spines['top'].set_color('white')  # Optional: Top axis line
    ax.spines['right'].set_color('white')  # Optional: Right axis line

    # Customize axis line thickness (optional)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)

    ax.tick_params(axis='x', colors='#00FF00')  # X-axis tick labels
    ax.tick_params(axis='y', colors='#00FF00')  # Y-axis tick labels
    ax.xaxis.label.set_color('#00FF00')  # X-axis label color
    ax.yaxis.label.set_color('#00FF00')  # Y-axis label color

    # Add percentage labels on top of each bar
    for bar in bars:
        height = bar.get_height()  # Get the height of the bar
        ax.annotate(str(round(height, 1)) + '%',  # Format to 1 decimal point
                    xy=(bar.get_x() + bar.get_width() / 2, height),  # Centered on the bar
                    xytext=(0, 8),  # Offset text 8 points above the bar
                    textcoords="offset points",  # Use offset points for positioning
                    ha='center', va='bottom',color='#00FF00')  # Align center horizontally

    # Add title and sentiment label
    ax.text(-0.145, 1.12, title(), transform=ax.transAxes, fontsize=7.5,
            bbox=dict(facecolor='black', alpha=0.5,edgecolor='none'),color='#00FF00')
    ax.set_title("\n" + whose + " Emotions", color='white')

    # Adjust layout to prevent any element from overlapping or getting cropped
    plt.subplots_adjust(top=0.85, bottom=0.2)

    fig.autofmt_xdate()  # Rotate x-axis labels if necessary

    # Add sentiment label at the bottom of the graph
    ax.text(0.5, -0.25, "Overall Sentiment[NLTK]: " + label,
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='black', alpha=0.5,edgecolor='none'),color='#00FF00')

    # Save the plot as PNG without cropping any elements
    plt.savefig('graph_' + whose.lower() + '.png', bbox_inches='tight')

viewers_sentiment_label=sentiment_analyse('read.txt')
graph_plot('read.txt',viewers_sentiment_label,r"Viewers'")
#Creators
with open('read1.txt', 'w', encoding='utf-8') as f:
    f.write("\ntitle\n")
    f.write(response_c['items'][0]['snippet']['title']+ '\n')
    f.close()
with open('read1.txt', 'a', encoding='utf-8') as f:
    f.write("\ntags\n")
    l=response_c['items'][0]['snippet'].get('tags', [])
    for tags in l:
        f.write(tags+'\n')
    f.close()
with open('read1.txt', 'a', encoding='utf-8') as f:
    f.write("\ndescription\n")
    for item in response_c['items']:
        f.write(item['snippet']['description']+'\n')
    f.close()
try:
    transcript_list = YouTubeTranscriptApi.list_transcripts(vid)

    english_transcript = None
    other_transcript = None
    for transcript in transcript_list:
        if transcript.language_code == 'en' or transcript.language_code == 'en-US' or transcript.language_code == 'en-GB':
            english_transcript = transcript
            break
        else:
            other_transcript = transcript


    transcript_to_use = english_transcript if english_transcript else other_transcript

    if transcript_to_use:
        with open('read1.txt', 'a', encoding='utf-8') as f:
            f.write(f"\nFetching subtitles in {transcript_to_use.language} ({transcript_to_use.language_code})...\n")
            transcript_data = transcript_to_use.fetch()


            for entry in transcript_data:
                f.write(f"{entry['text']}" + '\n')
        print(f"Subtitles fetched in {transcript_to_use.language}")
    else:
        print("No available subtitles for this video.")

except Exception as e:
    print(f"An error occurred: {e}")
creators_sentiment_label=sentiment_analyse('read1.txt')
graph_plot('read1.txt',creators_sentiment_label,r"Creator's")
plt.show()



