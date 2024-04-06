#uvicorn main:app
#uvicorn main:app --reload

# Main imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from pydantic import BaseModel

# Custom function imports
from functions.text_to_speech import convert_text_to_speech
from functions.openai_requests import next_qns, feedback_fn
from functions.google_stt import gtts

# Initiate
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]


# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##############################################################
#                                                            #
#                       DONT TOUCH                           #
#                                                            #
##############################################################

curr_ques_pair = { 'question': 'Wie heißen Sie?', 
                 'answer': '', 'fixed_start': 'Wie heißen Sie?'
                 }

backend = {'next_question':''}

message_input ="Generate a follow up question for this question and answer pair."

# Check health (API)
@app.get("/health")
async def check_health():
    return {"response": "healthy"}

#Reset Message
@app.get("/reset-text/")
async def reset_conversation():
    return curr_ques_pair["fixed_start"]


#initalize voice
@app.get("/reset-voice/")
async def send_starter_voice():
    text = curr_ques_pair["fixed_start"]
    audio_output = convert_text_to_speech('Bruno',text)
    #Guard: Ensure message decoded
    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get chat response")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")


#application/octet-stream
#audio/mpeg

##############################################################
#####################Simulated Conversation###################
##############################################################

#conversation preamble
@app.get("/conversation-preamble")
async def send_preamble():
    return {"text": "You will be revising your lessons on introducing yourself in this session."}

#conversation starter by edubot
@app.get("/start-question-text/")
async def send_starter_text():
    return {"text":curr_ques_pair["question"]}

#initalize voice
@app.get("/start-question-voice/")
async def send_starter_voice():
    text = curr_ques_pair["question"]
    audio_output = convert_text_to_speech('Bruno',text)
    #Guard: Ensure message decoded
    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get chat response")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")

#Getting user input 
@app.post("/get-user-audio/")
async def get_audio(file: UploadFile = File(...)):
    
   
    
    # Save file from frontend using the unique filename
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")

    # Decode audio
    message_decode = gtts(file.filename)
    backend['transcription'] = message_decode

    # Guard: Ensure decoded
    if not message_decode:
        return "Error"
    # HTTPException(status_code=400, detail="Failed to decode audio")
    return message_decode 

# get feedback 
@app.post("/feedback/")
async def get_audio(request: Request):
    
    form = await request.form()
    message_decode = "Wie heißen Sie?"
    curr_ques_pair["answer"] = message_decode

    #Get ChatGPT Response
    chat_reponse = feedback_fn(curr_ques_pair["question"],message_decode)
    
    #Guard: Ensure message decoded
    if not chat_reponse:
        return HTTPException(status_code=400, detail="Failed to get chat response")
    else:
        if chat_reponse['grammar_score'] + chat_reponse['appropriateness_score'] >= 9:
            chat_reponse['Next'] = "Next Level"
            curr_ques_pair["question"] = next_qns(message_input + "Question: "+ curr_ques_pair["question"] + "Answer:" + curr_ques_pair["answer"])
        else:
            chat_reponse['Next'] = "Try Again"
    #Store Messages
    #store_messages(message_decode, chat_reponse)

    
    return chat_reponse

##file: UploadFile = File(...)

# audio response for suggested answer
@app.post("/suggested-answer/")
async def get_audio2(request: Request):
    
    form = await request.form()
    chat_response = form.get("chat_response")
    
    #convert chat response to audio
    audio_output = convert_text_to_speech('Bruno',chat_response)
    #print(chat_response.split("###"))

    #Guard: Ensure message decoded
    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get chat response")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")


#Next Question
@app.get("/next-text/")
async def next_conversation():
    return curr_ques_pair["question"]


#initalize voice
@app.get("/next-voice/")
async def send_starter_voice():
    text = curr_ques_pair["question"]
    audio_output = convert_text_to_speech('Bruno',text)
    #Guard: Ensure message decoded
    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get chat response")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")