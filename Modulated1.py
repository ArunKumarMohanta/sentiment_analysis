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

# Constants
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
DEVELOPER_KEY = "YOR API KEY HERE"

class YouTubeAnalyzer:
    def __init__(self, api_key=DEVELOPER_KEY):
        self.youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, developerKey=api_key)
        self.vid = None
        self.response_c = None
        self.response_v = None

    def extract_video_id(self, url):
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
        #... (same implementation)

    def get_creators(self):
        request = self.youtube.videos().list(
            part="snippet",
            id=self.vid
        )
        self.response_c = request.execute()
        return self.response_c

    def get_title(self):
        return self.response_c['items'][0]['snippet']['title']

    def get_viewers(self):
        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=self.vid,
            maxResults=100
        )
        self.response_v = request.execute()
        return self.response_v

    def save_viewers_comments(self, filename='read.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in self.response_v['items']:
                f.write(item['snippet']['topLevelComment']['snippet']['textDisplay'] + '\n')
            f.close()
        print("Comments fetched")

    def save_creators_data(self, filename='read1.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\ntitle\n")
            f.write(self.response_c['items'][0]['snippet']['title'] + '\n')
            f.close()
        print('Title fetched')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write("\ntags\n")
            l = self.response_c['items'][0]['snippet'].get('tags', [])
            for tags in l:
                f.write(tags + '\n')
            f.close()
        print('tags fetched')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write("\ndescription\n")
            for item in self.response_c['items']:
                f.write(item['snippet']['description'] + '\n')
            f.close()
        print('Description fetched')

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.vid)

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
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f"\nFetching subtitles in {transcript_to_use.language} ({transcript_to_use.language_code})...\n")
                    transcript_data = transcript_to_use.fetch()

                    for entry in transcript_data:
                        f.write(f"{entry['text']}" + '\n')
                print(f"Subtitles fetched in {transcript_to_use.language}")
            else:
                print("No available subtitles for this video.")

        except Exception as e:
            print(f"An error occurred: {e}")

class SentimentAnalyzer:
    def __init__(self, video_title=None):
        self.video_title = video_title
    def cleaning_text(self, rt_text):
        text = open(rt_text, encoding='utf-8').read()
        lower_case = text.lower()
        cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))
        return cleaned_text
        #... (same implementation)

    def emotions_from_emotions_txt(self, rt_text):
        cleaned_text = self.cleaning_text(rt_text)
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
        #print(emotion_list)
        w = Counter(emotion_list)
        #print(w)
        return w
        #... (same implementation)

    def polarity_score(self, app_text):
        sentiment_text = self.cleaning_text(app_text)
        score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
        return score
        #... (same implementation)

    def convert_scores_to_percent(self,scores):
        """Convert sentiment scores to percentages, handling negative compound scores."""
        percent_scores = {}

        # Convert 'neg', 'neu', and 'pos' scores to percentages
        for key in ['neg', 'neu', 'pos']:
            percent_scores[key] = round(scores[key] * 100, 2) # Round to 2 decimal places


        # Handle the 'compound' score separately
        compound_score = scores['compound']
        if compound_score < 0:
            percent_scores['compound'] = 0.0  # Set to 0% for negative scores
        else:
            percent_scores['compound'] = round(((compound_score + 1) / 2) * 100, 2)  # Absolute percentage conversion

        return percent_scores

    def sentiment_analyse(self,app_text):
        score=self.polarity_score(app_text)
        if score['neg'] > score['pos']:
            return "Negative Sentiment"
        elif score['neg'] < score['pos']:
            return "Positive Sentiment"
        else:
            return "Neutral Sentiment"

    def graph_plot(self, file_path, label, whose):
        emotions = self.emotions_from_emotions_txt(file_path)
        if whose == "Viewers'":
            global viw
            viw = emotions
        else:
            global cre
            cre = emotions

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
        for idx, bar in enumerate(bars):
            height = bar.get_height()

            # Alternate the label offset (8 for even, 15 for odd)
            offset = 8 if idx % 2 == 0 else 15

            ax.annotate(f"{round(height, 1)}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),  # Centered on bar
                        xytext=(0, offset),  # Use staggered offsets
                        textcoords="offset points",
                        ha='center', va='bottom', color='#00FF00', fontsize=7)

        # Add title and sentiment label
        ax.text(-0.145, 1.12, self.video_title, transform=ax.transAxes, fontsize=9.0,
                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'), color='#00FF00')
        ax.set_title("\n" + whose + " Emotions", color='white')

        # Adjust layout to prevent any element from overlapping or getting cropped
        plt.subplots_adjust(top=0.85, bottom=0.2)

        fig.autofmt_xdate()  # Rotate x-axis labels if necessary

        # Add sentiment label at the bottom of the graph
        ax.text(0.5, -0.25, "Overall Sentiment[NLTK]: " + label,
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'),
                color='#00FF00')

        # Save the plot as PNG without cropping any elements
        plt.savefig('graph_' + whose.lower() + '.png', bbox_inches='tight')
        #... (same implementation)

def combine_files(file1, file2, output_file):
    text = ''
    with open(output_file, 'w', encoding='utf-8') as f:
        with open(file1, 'r', encoding='utf-8') as f1:
            text = f1.read()
            f1.close()
        with open(file2, 'r', encoding='utf-8') as f2:
            text = text + f2.read()
            f2.close()
        f.write(text)
        f.close()

def find_overall_tone(file_path):
    combo = SentimentAnalyzer().emotions_from_emotions_txt(file_path)
    max_count = max(combo.values())
    oelist = []
    for k, v in combo.items():
        if v == max_count:
            oelist.append(k)
    if len(oelist) == 1:
        oe = oelist[0].upper()
    else:
        oe = ",".join(oelist).upper()
    return oe

# Example Usage
if __name__ == "__main__":
    url = input("Enter a valid Youtube video link: ")
    analyzer = YouTubeAnalyzer()
    analyzer.vid = analyzer.extract_video_id(url)
    analyzer.get_creators()
    analyzer.get_viewers()
    analyzer.save_viewers_comments()
    analyzer.save_creators_data()

    video_title = analyzer.get_title()
    sentiment_analyzer = SentimentAnalyzer( video_title)
    viewers_sentiment_label = sentiment_analyzer.sentiment_analyse('read.txt')
    sentiment_analyzer.graph_plot('read.txt', viewers_sentiment_label, r"Viewers'")
    creators_sentiment_label = sentiment_analyzer.sentiment_analyse('read1.txt')
    sentiment_analyzer.graph_plot('read1.txt', creators_sentiment_label, r"Creator's")

    combine_files('read.txt', 'read1.txt', 'Combined.txt')
    oe = find_overall_tone('Combined.txt')
    print("THE OVERALL TONE OF THE VIDEO (COMBINED EMOTIONS OF BOTH VIEWERS' AND CREATOR's): ", oe)
    plt.show()