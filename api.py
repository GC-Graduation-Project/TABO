from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import io
import demucs,demucs.api

app = FastAPI()

#start command : uvicorn api:app 
#--reload 태그 추가하면 변경사항 감지되면 서버 재시작
# --workers {숫자} 옵션을 통해서 멀티프로세싱 가능

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/getSeparatedWav")
async def separateMp3(file: UploadFile = File(...)):
    # Check if the uploaded file is an MP3 file
    if not file.filename.endswith(".mp3"):
        return {"error": "Only MP3 files are allowed"}

   # Read the contents of the file

    print('sent file '+file.filename) 
    contents = await file.read()

    # Specify the directory where you want to save the MP3 file
    save_path = f"./uploaded_mp3/{file.filename}"
    

    # Save the contents to the specified path
    print('start save file')
    with open(save_path, "wb") as f:
        f.write(contents)
        print(file.filename+' saved')

    print('separation start')
    # Use another model and segment:
    separator = demucs.api.Separator(model='htdemucs_6s')

    print(save_path)
    # Separating an audio file
    origin, separated = separator.separate_audio_file(save_path)


    # Remember to create the destination folder before calling `save_audio`
    # Or you are likely to recieve `FileNotFoundError`
    for file in separated:
        source = separated.get(file)
        # print(source)
        print(f"fileName: {file}")
        demucs.api.save_audio(source,f"./separated/{file}.wav",samplerate=separator.samplerate)

    print('separation finished')    
    wav_file_path = "./separated/guitar.wav"


    # Read the WAV file and get its binary data
    print('convert wav file to binary')
    wav_data = read_wav_file(wav_file_path)

    print('sending wav to client')

    # Return the WAV data as a StreamingResponse

    return StreamingResponse(io.BytesIO(wav_data), media_type="audio/wav", headers={"Content-Disposition": "inline; filename=guitar.wav"})
    
def read_wav_file(file_path):
    with open(file_path, "rb") as wav_file:
        wav_data = wav_file.read()
    return wav_data  