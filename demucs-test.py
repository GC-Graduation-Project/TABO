import demucs.api

# Use another model and segment:
separator = demucs.api.Separator(model='htdemucs_6s')

# Separating an audio file
origin, separated = separator.separate_audio_file("./uploaded_mp3/love.mp3")
print(separated)

# Remember to create the destination folder before calling `save_audio`
# Or you are likely to recieve `FileNotFoundError`
for file in separated:
    source = separated.get(file)
    # print(source)
    print(f"fileName: {file}")
    demucs.api.save_audio(source,f"./separated/{file}.wav",samplerate=separator.samplerate)

