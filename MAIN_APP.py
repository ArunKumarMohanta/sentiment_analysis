import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox
from Modulated1 import YouTubeAnalyzer, SentimentAnalyzer, combine_files, find_overall_tone
from PIL import Image, ImageTk
import sys
import ctypes
#import os

class TextRedirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)  # Scroll to the end of the text box

    def flush(self):
        pass

class YouTubeEmotionAnalyzerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.video_title = ""

        # Configure customtkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Open the window in full screen
        #self.state("zoomed")  # or self.attributes("-fullscreen", True)


        # Get the screen's dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Get the taskbar height using ctypes
        taskbar_handle = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        taskbar_rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(taskbar_handle, ctypes.byref(taskbar_rect))
        taskbar_height = taskbar_rect.bottom - taskbar_rect.top

        # Set the window's geometry (leaving space for the taskbar)
        self.geometry(f"{screen_width - 100}x{screen_height - taskbar_height - 50}+50+{taskbar_height + 50}")

        # GUI Components
        self.title("YouTube Emotion Analyzer")
        #self.geometry("800x600")

        # Add title icon
        self.iconbitmap('icon.ico')  # Replace 'icon.ico' with the path to your icon file


        #self.geometry("1920x1080")

        # URL Label and Entry (covering full window length)
        url_frame = tk.Frame(self, bg="#2b2b2b")
        url_frame.pack(fill=tk.X, pady=10)

        # Search Bar and Button Frame (horizontal layout)
        search_frame = tk.Frame(self, bg="#2b2b2b")
        search_frame.pack(fill=tk.X, pady=10)

        self.url_label = ctk.CTkLabel(search_frame, text="YouTube Video URL:", font=("Arial", 15))
        self.url_label.pack(side=tk.LEFT, padx=10)



        self.url_entry = ctk.CTkEntry(search_frame, width=300, font=("Arial", 15))
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        # Button with Image (above search bar, extreme right end)
        button_frame = tk.Frame(self, bg="#2b2b2b")
        button_frame.pack(fill=tk.X, pady=(0, 10))  # Adjusted pady to reduce gap

        # Load button image (ensure it's in the same directory as the script)
        button_image_path = "button_image.png"  # Replace with your image file
        button_image = Image.open(button_image_path)
        button_image = button_image.resize((52, 52))  # Resize the image to a fixed size (adjust as needed)
        tk_button_image = ImageTk.PhotoImage(button_image)

        self.analyze_button = ctk.CTkButton(search_frame, image=tk_button_image, text="", compound=tk.TOP,
                                            command=self.analyze_video, width=30, height=30)
        self.analyze_button.image = tk_button_image  # Keep a reference to prevent garbage collection
        self.analyze_button.pack(side=tk.RIGHT, padx=10, pady=5)

        #self.analyze_button = ctk.CTkButton(self, text="Analyze Emotions", command=self.analyze_video)
        #self.analyze_button.pack(pady=10)

        # Graph Frames
        '''self.creator_graph_frame = tk.Frame(self, bg="#2b2b2b")
        self.creator_graph_frame.pack(pady=10)

        self.viewer_graph_frame = tk.Frame(self, bg="#2b2b2b")
        self.viewer_graph_frame.pack(pady=10)'''

        # Graph Frames (packed horizontally)
        graph_container_frame = tk.Frame(self, bg="#2b2b2b")
        graph_container_frame.pack(pady=(10, 20))

        self.creator_graph_frame = tk.Frame(graph_container_frame, bg="#2b2b2b")
        self.creator_graph_frame.pack(side=tk.LEFT, padx=10)

        self.viewer_graph_frame = tk.Frame(graph_container_frame, bg="#2b2b2b")
        self.viewer_graph_frame.pack(side=tk.LEFT, padx=10)

        # Terminal-like Text Box (for program output)
        self.output_text_box = tk.Text(self, height=6, width=120, bg="#2b2b2b", fg="#FFFFFF")
        self.output_text_box.config(font=("Courier new", 20))  # Increase font size to 14
        self.output_text_box.pack(fill=tk.BOTH, expand=True, pady=(10, 10))


        # Status Bar (Bottom)
        self.status_bar = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.overall_tone_label = ctk.CTkLabel(self.status_bar, text="", font=("Arial", 15))
        self.overall_tone_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Redirect program output to the text box
        sys.stdout = TextRedirect(self.output_text_box)

        self.status_bar_separator = ctk.CTkLabel(self.status_bar, text="|", font=("Arial", 10), fg_color="#2b2b2b",
                                                 text_color="#AAAAAA")
        self.status_bar_separator.pack(side=tk.LEFT, padx=5, pady=5)

        # Load images (ensure they are in the same directory as the script)
        image_path = "path_to_your_image.png"
        image = Image.open('view.png')
        #self.view_image = tk.PhotoImage(file='view.png')  # Replace 'view.png' with your image file
        #self.view_image = self.view_image.subsample(2, 2)  # Resize the image to a smaller size (adjust as needed)
        # Resize the image to a fixed size to prevent distorting the status bar width
        image = image.resize((50, 50))  # Adjust the size as needed
        # Convert the PIL image to a format usable by tkinter (and thus customtkinter)
        tk_image = ImageTk.PhotoImage(image)

        # Buttons to display file contents
        self.view_buttons_frame = tk.Frame(self.status_bar, bg="#2b2b2b")
        self.view_buttons_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.view_read_txt_button = ctk.CTkButton(self.view_buttons_frame,image=tk_image, text="", compound=tk.TOP, command=self.display_read_txt,
                                                  width=30, height=30)
        self.view_read_txt_button.image = tk_image  # Keep a reference to prevent garbage collection
        self.view_read_txt_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Load images (ensure they are in the same directory as the script)
        # Load your image using PIL (Python Imaging Library)
        image_path1 = "content.png"
        image1 = Image.open(image_path1)
        #self.content_image = tk.PhotoImage(file='content.png')  # Replace 'content.png' with your image file
        #self.content_image = self.content_image.subsample(2, 2)  # Resize the image to a smaller size (adjust as needed)
        # Resize the image to a fixed size to prevent distorting the status bar width
        image1 = image1.resize((50, 50))  # Adjust the size as needed
        # Convert the PIL image to a format usable by tkinter (and thus customtkinter)
        tk_image = ImageTk.PhotoImage(image1)

        self.view_read1_txt_button = ctk.CTkButton(self.view_buttons_frame,image=tk_image,  text="",compound=tk.TOP, command=self.display_read1_txt,
                                                   width=30, height=30)
        self.view_read_txt_button.image = tk_image  # Keep a reference to prevent garbage collection
        self.view_read1_txt_button.pack(side=tk.LEFT, padx=2, pady=2)



        self.status_bar_copyright = ctk.CTkLabel(self.status_bar, text="© 2024 YouTube Emotion Analyzer",
                                                 font=("Arial", 15), fg_color="#2b2b2b", text_color="#AAAAAA")
        self.status_bar_copyright.pack(side=tk.RIGHT, padx=10, pady=5)

    def display_read_txt(self):
        try:
            with open('read.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                file.close()

            # Create a new window to display the content
            read_txt_window = tk.Toplevel(self)
            read_txt_window.title("Viewers'")
            read_txt_window.geometry("1000x800")

            # Create a text widget to display the content
            text_widget = tk.Text(read_txt_window, font=("Arial", 30))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.INSERT, content)
            text_widget.config(state="disabled")  # Make the text widget read-only
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_read1_txt(self):
        try:
            with open('read1.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                file.close()

            # Create a new window to display the content
            read1_txt_window = tk.Toplevel(self)
            read1_txt_window.title("Creator's")
            read1_txt_window.geometry("1000x800")

            # Create a text widget to display the content
            text_widget = tk.Text(read1_txt_window, font=("Arial", 30))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.INSERT, content)
            text_widget.config(state="disabled")  # Make the text widget read-only
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def graph_plot(self, frame, emotions, label, whose):
        for widget in frame.winfo_children():
            widget.destroy()

        # Calculate total emotions to convert counts to percentages
        total_count = sum(emotions.values())
        percentages = {k: (v / total_count) * 100 for k, v in emotions.items() if total_count!= 0}

        if not percentages:  # Check if percentages is empty
            # Handle the case where there's no data to plot
            label_no_data = tk.Label(frame, text=f"{whose} Emotions\nNo Emotion Data Available", font=('Helvetica', 20))
            label_no_data.pack()
            return  # Exit the function to avoid further errors

        # Create the bar graph (no change in figure size)
        figure = Figure(figsize=(12, 10), dpi=100)
        ax = figure.add_subplot(111)
        figure.patch.set_facecolor('#121212')  # Dark figure background
        ax.set_facecolor('#1E1E1E')  # Slightly lighter axes background

        # Plot bars with emotion percentages
        bars = ax.bar(percentages.keys(), percentages.values(), color='#FF8C00')  # Vibrant Orange Bars

        # Adjust y-limit to provide space for the labels above the bars
        ax.set_ylim(0, max(percentages.values()) * 1.2)

        # Customize axis lines with Light Gray (#B0B0B0)
        for spine in ax.spines.values():
            spine.set_color('#B0B0B0')  # Light Gray for axis lines
            spine.set_linewidth(1.5)

        # Customize grid lines
        ax.grid(True, which='major', color='#444444', linestyle='--', linewidth=0.7)  # Major grid lines
        ax.grid(True, which='minor', color='#2E2E2E', linestyle=':', linewidth=0.5)  # Minor grid lines
        ax.minorticks_on()  # Enable minor ticks for better granularity

        # Customize tick labels and axis labels
        ax.tick_params(axis='x', colors='#00FA9A', labelsize=17)  # Mint Green X-axis tick labels(15)
        ax.tick_params(axis='y', colors='#00FA9A', labelsize=17)  # Mint Green Y-axis tick labels(15)
        # Set X-axis label with padding
        ax.set_xlabel("Emotion Type-->", fontsize=16.5, color='#FFD700', labelpad=10)  # 10 points of padding(15)(#00FA9A)

        # Set Y-axis label with padding
        ax.set_ylabel("Percentage-->", fontsize=16.5, color='#FFD700', labelpad=10)  # 10 points of padding(15)

        #ax.xaxis.label.set_color('#00FA9A')  # Mint Green X-axis label
        #ax.yaxis.label.set_color('#00FA9A')  # Mint Green Y-axis label

        # Add percentage labels on top of each bar
        for idx, bar in enumerate(bars):
            height = bar.get_height()
            offset = 8 if idx % 2 == 0 else 15  # Alternate the label offset

            ax.annotate(f"{round(height, 1)}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),  # Centered on bar
                        xytext=(0, offset),  # Staggered offsets
                        textcoords="offset points",
                        ha='center', va='bottom', color='#FFD700', fontsize=12)  # Golden Yellow

        # Add title and sentiment label
        ax.text(-0.145, 1.12, self.video_title, transform=ax.transAxes, fontsize=18.0,
                bbox=dict(facecolor='#8A7F8D', alpha=0.5, edgecolor='none'), color='#FFD700')
        ax.set_title("\n" + whose + " Emotions", color='white',fontsize=20)

        # Adjust layout to prevent any overlap or cropping
        plt.subplots_adjust(top=0.85, bottom=0.2)
        figure.autofmt_xdate()  # Rotate x-axis labels if necessary

        # Add sentiment label at the bottom of the graph
        ax.text(0.5, -0.25, "Overall Sentiment[NLTK]: " + label,
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=20,
                bbox=dict(facecolor='#8A7F8D', alpha=0.5, edgecolor='none'),  # Muted Purple box
                color='#FFD700')  # Golden Yellow text

        # Embed the graph into the GUI
        canvas = FigureCanvasTkAgg(figure, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def analyze_video(self):
        # Clear the terminal (cross-platform)
        #os.system('cls' if os.name == 'nt' else 'clear')

        # Clear the terminal box
        self.output_text_box.delete(1.0, tk.END)  # For tk.Text or CTkTextbox

        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube video URL")
            return

        # Initialize analyzers
        youtube_analyzer = YouTubeAnalyzer()
        sentiment_analyzer = SentimentAnalyzer()

        # Analyze video (simplified for brevity)
        youtube_analyzer.vid = youtube_analyzer.extract_video_id(url)
        youtube_analyzer.get_creators()
        youtube_analyzer.get_viewers()

        #to print status pn terminal
        print('# STATUS #' + f' ({youtube_analyzer.get_title()})')

        # Save data to files (assuming your original script's functionality)
        youtube_analyzer.save_viewers_comments()
        youtube_analyzer.save_creators_data()

        # to print where comments,title,description,tags and transcript can be seen
        print('Click on eye button on status bar to see comments')
        print('Click on play button on status bar to see title,description,tags and transcript')
        # Get video title
        self.video_title = youtube_analyzer.get_title()  # Assign video title to the attribute

        # Combine files
        combine_files('read.txt', 'read1.txt', 'Combined.txt')

        # Find overall tone
        overall_tone = find_overall_tone('Combined.txt')
        if isinstance(overall_tone, list):
            overall_tone_str = ", ".join(overall_tone)
        else:
            overall_tone_str = overall_tone

        # finding polarity score of combined text
        score = sentiment_analyzer.polarity_score('Combined.txt')

        #finding percentage of polarity score
        percent_score=sentiment_analyzer.convert_scores_to_percent(score)


        self.overall_tone_label.configure(text=f"Overall Tone: {overall_tone_str}  Positive Score:{percent_score['pos']}(%) Negative Score:{percent_score['neg']}(%) Neutral Score:{percent_score['neu']}(%) Compound Score:{percent_score['compound']}(%)")

        # Plot graphs
        creator_emotions = sentiment_analyzer.emotions_from_emotions_txt('read1.txt')
        viewer_emotions = sentiment_analyzer.emotions_from_emotions_txt('read.txt')
        #Finding label
        label1=sentiment_analyzer.sentiment_analyse('read1.txt')
        label2 = sentiment_analyzer.sentiment_analyse('read.txt')

        ''''# Create a frame to hold both graphs horizontally
        graph_frame = tk.Frame(self, bg="#2b2b2b")
        graph_frame.pack(pady=10)

        # Create frames for each graph within the horizontal frame
        self.creator_graph_frame = tk.Frame(graph_frame, bg="#2b2b2b")
        self.creator_graph_frame.pack(side=tk.LEFT, padx=10)

        self.viewer_graph_frame = tk.Frame(graph_frame, bg="#2b2b2b")
        self.viewer_graph_frame.pack(side=tk.LEFT, padx=10)'''

        self.graph_plot(self.creator_graph_frame, creator_emotions, label1, "Creator's")
        self.graph_plot(self.viewer_graph_frame, viewer_emotions, label2, "Viewer's")


if __name__ == "__main__":
    app = YouTubeEmotionAnalyzerGUI()

    app.mainloop()