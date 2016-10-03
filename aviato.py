"""
Main file in which the Aviato application is run.
Functionality of this GitHUB version limited because necessary API keys
and functionalities have been removed for privacy reasons.
"""

__author__ = "Abhishek Tumuluru"
__credits__ = ["Abhishek Tumuluru", "Mohit Chauhan"]
__version__ = "1.1"
__maintainer__ = "Abhishek Tumuluru"
__email__ = "abhishek.tumuluru@gatech.edu"


import json
import pyaudio
import wave
from watson_developer_cloud import AlchemyLanguageV1
import speech_recognition as sr
from os import path
import subprocess
from twilio.rest import TwilioRestClient
from tkinter import *


def check_valid_flight_number(string_numbers_said):
    """Checks if the spoken flight number is valid

    Args:
        string_numbers_said (str): Checks if all text is a number

    Returns:
        csv_num_and_name (list): a list of the flight number and name of client
    """
    numbers = {"zero": 0, "one": 1, "two": 2, "three": 3,
               "four": 4, "five": 5, "six": 6,
               "seven": 7, "eight": 8, "nine": 9}
    nums = string_numbers_said.split(" ")
    boolean_valid = False
    csv_num_and_name = []
    for num in nums:
        if num not in numbers:
            boolean_valid = False
        else:
            boolean_valid = True
    if boolean_valid:
        database_numbers = ""
        for anum in nums:
            try:
                database_numbers += str(numbers[anum])
            except ValueError:
                boolean_valid = False
        csv_num_and_name.append(database_numbers)
        print(database_numbers)
        play_to_client("full_name_ask.wav")
        record_flight_number("full_name.wav")
        name = speech_to_text("full_name.wav")
        csv_num_and_name.append(name)
        print(name)
        play_to_client("both_right.wav")
        record_flight_number("output.wav")
    else:
        play_to_client("invalid_flight_number.wav")
        return []
    return csv_num_and_name


def play_to_client(filename):
    """Plays audio to the client

    Args:
        filename (str): the audio file in the directory that is played
    """
    CHUNK = 1024
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()


def record_flight_number(string_file_name):
    """Records the client's audio and saves it in a file

    Args:
        string_file_name (str): the file in which the audio is saved

    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = string_file_name
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def speech_to_text(string_file_name):
    """Takes in a filename and converts the contents of it into a string

    Args:
        string_file_name (str): name of the file to transcribe

    Returns:
        final_speech_to_text (str): the transcribed string
    """
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), string_file_name)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source) # read the entire audio file

    # recognize speech using Sphinx
    try:
        final_speech_to_text = r.recognize_sphinx(audio)
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
    finally:
        final_speech_to_text = r.recognize_sphinx(audio)
    return final_speech_to_text


def analyze():
    """Obtains a json file from an IBM Watson AlechemyAPI REST call
    with the sentiment rating and keywords in the text. API Key hidden.

    Returns:
        jsonStr (str): a string representation of the json file obtained from
                        passing the complaint in the speech_to_text function
                        and then parsing it with Watson.
    """
    alchemy_language = AlchemyLanguageV1(api_key='')
    jsonStr = json.dumps(
        alchemy_language.combined(
        text = speech_to_text("output.wav"),
        extract='keywords',
        sentiment=1,
        max_items=10),
        indent=2)
    return jsonStr

#record audio clip


def make_csv():
    """Makes a csv file after parsing through the json and performing required
    calculations and operations. Writes the csv data to data.txt.

    Returns:
        csv_str (str): a csv of all details of the customer:
                    the flight number and name, the sentiment score,
                    the keywords, and the conversation itself.
    """
    csv_str = ""
    speech = speech_to_text("passenger_flight_number.wav")
    num_and_name = check_valid_flight_number(speech)
    num_and_name.append(speech_to_text("output.wav"))
    jsonStr = analyze()
    jsonFile = json.loads(jsonStr)
    total_sentiment = 0.0
    count = 0
    keywords = []
    length = len(keywords)
    for item in jsonFile["keywords"][length]:
        if item == "text":
            keywords.append(jsonFile["keywords"][0]["text"])
        elif item == "sentiment":
            total_sentiment += (float(jsonFile["keywords"][count]["sentiment"]["score"])
                                * float(jsonFile["keywords"][count]["relevance"]))
        count += 1
    average_sentiment = total_sentiment/count * 100
    average_sentiment = (average_sentiment + 100) / 20
    average_sentiment = average_sentiment * 1.5 if average_sentiment > 5 else average_sentiment * 0.7
    average_sentiment_str = str(average_sentiment)

    num_and_name.append(keywords)
    num_and_name.append(average_sentiment_str)
    for item in num_and_name:
        if type(item) == list:
            csv_str += (item[0] + ";")
        else:
            csv_str += (item + ";")
    f = open("data.txt", "w")
    f.write("Flight Number: " + csv_str)
    return csv_str


def main():
    """The main function which is executed when the start button on the GUI is
    clicked. This plays and records all the necessary audio, makes calls to
    AlchemyAPI, Twilio, and the make_csv function. A subprocess call is made to
    the node.js file (author: Mohit Chauhan) which appends the csv data to a
    firebase database by flight number.
    """
    play_to_client("flight_number_ask.wav")
    check_valid_flight_number(speech_to_text("passenger_flight_number.wav"))
    record_flight_number("passenger_flight_number.wav")
    make_csv()
    print(analyze())
    subprocess.call("node firebase.js")
    negative_response = make_csv().split(";")[-1] <= 5
    if negative_response:
        twilio_call("+12674750425", "+12674607556",
                    "Thank you for your feedback.\n We are sorry you had this issue."
                    "We value our customers and are looking into this matter.\n"
                    "Thank you! \n")
    else:
        twilio_call("+12674750425", "+12674607556",
                    "Thank you for your feedback!\n We are glad that your experience was enjoyable."
                    "The people responsible will be thanked on our behalf\n"
                    "Thank you! \n")


#twilioNumber +12674607556
def twilio_call(to_number, from_number, message_body=""):
    """Makes a REST call to the Twilio API to send an apologetic or thankful SMS

    Args:
        to_number (str): the number to which the SMS is sent
        from_number (str): the registered twilio number
                       from which the SMS is sent
        message_body: The message body. Defaults to str with length 0

    Returns:
        final_speech_to_text (str): the transcribed string
    """
    ACCOUNT_SID = "hidden for GITHUB"
    AUTH_TOKEN = "hidden for GITHUB"
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(
        to = to_number,
        from_ = from_number,
        body = message_body,
    )


def gui():
    """
    Creates a GUI interface for the application using Tkinter
    """
    app = Tk()
    app.configure(background = "white")
    app.title("Customer Experience")
    photo = PhotoImage(file="deltalogo.png")
    label2 = Label(app, image=photo, bg = "white")
    label = Label(app, text="Customer Experience Improvement", font=("Corbel", 35), bg = "white")

    label3 = Label(app, text="IBM Watson Keyword & Sentiment Analyzer", font=("Corbel", 28), bg = "white")

    logo = PhotoImage(file="Aviato_Logo.png")

    logo_label = Label(app, image=logo)
    button = Button(text="Start", command=main, height = 1, width = 6, font = ("Corbel", 30), bg = "white")
    logo_label.pack()
    label2.pack()
    label.pack()
    label3.pack()
    button.pack(padx=5, pady=10)

    mainloop()
if __name__ == "__main__":
    gui()
