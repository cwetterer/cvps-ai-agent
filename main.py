
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech_text = request.form.get("SpeechResult")
    if not speech_text:
        speech_text = "Hello?"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Melissa, a warm and efficient virtual receptionist for Carson Valley Psychological Services. "
                    "Keep replies brief—1 to 2 sentences max—and speak clearly. Your job is to answer general questions about psychological assessment services, "
                    "and gather caller information. Make it clear the practice does not offer psychotherapy and does not accept insurance. "
                    "Let callers know that Dr. Wetterer and Dr. Anderson are not accepting therapy clients. "
                    "Encourage prospective patients to use the website inquiry form at www.carsonpsychological.com or email info@carsonpsychological.com "
                    "to reach a live assistant for scheduling and follow-up. Always ask what type of assessment they are seeking or how they were referred."
                )
            },
            {"role": "user", "content": speech_text}
        ]
    )
    reply_text = response.choices[0].message["content"]

    twiml = VoiceResponse()
    gather = Gather(input='speech', action='/voice', method='POST', timeout=5)
    gather.say(reply_text, voice="Polly.Joanna", language="en-US")
    twiml.append(gather)
    twiml.say("We didn't catch that. Please call again if you need help.", voice="Polly.Joanna")
    twiml.hangup()

    return Response(str(twiml), mimetype="text/xml")

@app.route("/")
def index():
    return "AI Voice Agent is running."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

