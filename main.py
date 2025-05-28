from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Set OpenAI key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def is_during_business_hours():
    pacific = pytz.timezone("US/Pacific")
    now = datetime.now(pacific)
    return now.weekday() < 5 and 9 <= now.hour < 17  # Mon–Fri, 9am–5pm

@app.route("/voice", methods=["POST"])
def voice():
    if not is_during_business_hours():
        twiml = VoiceResponse()
        twiml.say("You’ve reached Carson Valley Psychological Services. Our office is currently closed.", voice="Polly.Salli", language="en-US")
        twiml.say("If you are experiencing a psychiatric emergency, please call 911 or go to the nearest emergency room. "
                  "If you need to speak with someone immediately, please dial 9-8-8 to reach a trained crisis worker.", voice="Polly.Salli", language="en-US")
        twiml.say("Otherwise, please leave a message with your name, phone number, and the reason for your call. Someone will get back to you during business hours.", voice="Polly.Salli", language="en-US")
        twiml.record(
            maxLength=120,
            action="/handle-recording",
            transcribe=True,
            transcribeCallback="/save-transcript"
        )
        twiml.hangup()
        return Response(str(twiml), mimetype="text/xml")

    speech_text = request.form.get("SpeechResult")
    if not speech_text:
        speech_text = "Hello?"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Melissa, a warm, professional, and efficient virtual receptionist for Carson Valley Psychological Services. "
                    "Begin all responses with: 'Carson Valley Psychological Services, this is Melissa. I am a virtual assistant, what can I help you with today?' "
                    "Keep replies brief—1 to 2 sentences max—and speak clearly and politely. "
                    "Your job is to answer questions about the services offered and gather key caller information. "
                    "Let the caller know that Carson Valley provides forensic, neuropsychological, and general psychological evaluations. "
                    "Politely explain that the practice is very busy and only accepts limited insurance. Do not offer psychotherapy. "
                    "Inform the caller that the best way to book an appointment is to submit an inquiry through the website: www.carsonpsychological.com. "
                    "You must ask the caller what type of evaluation they are seeking and who referred them. "
                    "Be sure to gather the following: the caller’s full name, phone number, and email address (if they are willing), as well as the type of evaluation requested. "
                    "Let them know that Dr. Wetterer will respond in a timely manner."
                )
            },
            {
                "role": "user",
                "content": speech_text
            }
        ]
    )

    reply_text = response.choices[0].message["content"]

    twiml = VoiceResponse()
    gather = Gather(input='speech', action='/voice', method='POST', timeout=5)
    gather.say(reply_text, voice="Polly.Salli", language="en-US")
    twiml.append(gather)
    twiml.say("We didn't catch that. Please call again if you need help.", voice="Polly.Salli")
    twiml.hangup()

    return Response(str(twiml), mimetype="text/xml")

@app.route("/handle-recording", methods=["POST"])
def handle_recording():
    return Response("Recording received.", mimetype="text/plain")

@app.route("/save-transcript", methods=["POST"])
def save_transcript():
    return Response("Transcript saved.", mimetype="text/plain")

@app.route("/")
def index():
    return "AI Voice Agent is running."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

