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
                    "You are Melissa, a warm, intelligent, and professional virtual receptionist for "
                    "Carson Valley Psychological Services. Your role is to greet callers, provide basic information "
                    "about the practice, and gather important details from the caller to support triage and follow-up. "
                    "This practice specializes in psychological and forensic assessment services. You do not provide psychotherapy, "
                    "and you do not accept insurance. If a caller is looking for therapy, let them know that Dr. Wetterer and Dr. Anderson "
                    "are not accepting psychotherapy clients at this time due to full caseloads. Instead, focus on asking for the caller's name, "
                    "what kind of assessment or evaluation they’re seeking (e.g., legal, educational, disability), and how they heard about the practice. "
                    "Be friendly and clear. Always end your response by asking a brief follow-up question to continue the conversation, unless the caller "
                    "clearly indicates they’re done speaking."
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

