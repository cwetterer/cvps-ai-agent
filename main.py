
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech_text = request.form.get("SpeechResult")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a warm, professional receptionist for Carson Valley Psychological Services. Greet callers, answer simple questions, and refer emergencies to 911 or 988."},
            {"role": "user", "content": speech_text}
        ]
    )
    reply_text = response.choices[0].message["content"]

    twiml = VoiceResponse()
    twiml.say(reply_text, voice="Polly.Joanna", language="en-US")
    return Response(str(twiml), mimetype="text/xml")

@app.route("/")
def index():
    return "AI Voice Agent is running."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
