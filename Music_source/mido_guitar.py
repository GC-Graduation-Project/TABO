from mido import MidiFile
import sys
import numpy as np
np.set_printoptions(threshold=np.inf)

mid = MidiFile('guitar_basic_pitch.mid')
mididict = []
output = []

# Put all note on/off in midinote as dictionary.
for i in mid:
    if i.type in ('note_on', 'note_off', 'time_signature'):
        mididict.append(i.dict())
# change time values from delta to relative time.
mem1=0
for i in mididict:
    time = i['time'] + mem1
    i['time'] = time
    mem1 = i['time']
# make every note_on with 0 velocity note_off
    if i['type'] == 'note_on' and i['velocity'] == 0:
        i['type'] = 'note_off'
# put note, starttime, stoptime, as nested list in a list. # format is [type, note, time, channel]
    mem2=[]
    if i['type'] in ('note_on', 'note_off'):
        mem2.append(i['type'])
        mem2.append(i['note'])
        mem2.append(i['time'])
        mem2.append(i['channel'])
        output.append(mem2)
# put timesignatures
    if i['type'] == 'time_signature':
        mem2.append(i['type'])
        mem2.append(i['numerator'])
        mem2.append(i['denominator'])
        mem2.append(i['time'])
        output.append(mem2)

clean_midi = []
on_air = [] 
for i in range(len(output)):
    event_type, note, time, channel = output[i]
    if event_type == 'note_on':
        on_air.append({'note': note, 'time': time, 'index': i }) 
        clean_midi.append(output[i])
    elif event_type == 'note_off':
        dirty_found = False

        for entry in on_air:
            if entry['note'] == note:
                if entry['time'] == time:
                    for j in range(len(clean_midi)):
                        if clean_midi[j][0] == 'note_on' and clean_midi[j][1] == note and clean_midi[j][2] == time:
                            clean_midi.pop(j)
                            dirty_found = True
                            break
                
                if not dirty_found:
                    clean_midi.append(output[i])
                
                on_air.remove(entry)
                break

print(mid.ticks_per_beat)
print(len(output))
print(len(clean_midi))


def midi_note_to_name(midi_note):
    if midi_note is None:
        return "Rest"  # Adjust this based on your preference for representing rests
    else:
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note_index = midi_note % 12
        note_name = note_names[note_index]
        return f"{note_name}{octave}"
    #return f"{note_name}{octave}" if (midi_note >= 40 and midi_note <= 77) else None  # 베이스 기타 음 범위를 확인

def duration_to_rhythmic_name(duration):
    rhythmic_names = {
        0.125: 'Sixteen Note',
        0.25: 'Eight Note',
        0.375: 'Dotted Eight Note',
        0.5: 'Quarter Note',
        0.75: 'Dotted Quarter Note',
        1: 'Half Note',
        1.5: 'Dotted Half Note',
        2: 'Whole Note'
    }

    closest_duration = min(rhythmic_names.keys(), key=lambda x: abs(x - duration))
    return rhythmic_names[closest_duration]

def rest_duration_to_rhythmic_name(rest_duration):
    if rest_duration is not None and rest_duration < 0.05: 
        return ''



    if rest_duration is not None:
        rhythmic_names = {
            0.125: 'Sixteenth rest',
            0.25: 'Eight rest',
            0.375: 'Dotted Eighth rest',
            0.5: 'Quarter rest',
            0.75: 'Dotted Quarter rest',
            1: 'Half rest',
            1.5: 'Dotted Half rest',
            2: 'Whole rest'
        }

        closest_duration = min(rhythmic_names.keys(), key=lambda x: abs(x - rest_duration))
        return rhythmic_names[closest_duration]
    else:
        return 'Unknown rest'




def is_guitar_note(note):
    return 40 <= note <= 84


def group_list(input_list, group_size):
    # 각 그룹을 생성합니다.
    result = [input_list[i:i + group_size] for i in range(0, len(input_list), group_size)]

    # 각 그룹의 시작 부분에 ['Treble', 'B4']를 삽입합니다.
    for group in result:
        group.insert(0, ['Treble', 'B4'])

    return result

bass_notes = []

for i, event in enumerate(clean_midi[:-1]):
    event_type, note, time, channel = event

    if event_type == 'note_on' and is_guitar_note(note):
        bass_notes.append({
            'note': note,
            'start_time': time,
            'end_time':None,
            'duration': None,
            'rhythmic_name': None
        })

        for j in range(i + 1, len(clean_midi)):
            if clean_midi[j][0] == 'note_off' and clean_midi[j][1] == note and clean_midi[j][3] == channel:
                end_time = clean_midi[j][2]
                duration = end_time - time
                rhythmic_name = duration_to_rhythmic_name(duration)

                bass_notes[-1]['end_time'] = end_time
                bass_notes[-1]['duration'] = duration
                bass_notes[-1]['rhythmic_name'] = rhythmic_name

                break

# 시작 시간이 중복된 경우에는 뒤의 배열을 삭제
bass_notes = [bass_notes[0]] + [bass_note for i, bass_note in enumerate(bass_notes[1:]) if bass_note['start_time'] != bass_notes[i]['start_time']]


for i, bass_note in enumerate(bass_notes[:-1]):
    note = bass_note['note']
    next_note = bass_notes[i + 1]['note']
    current_start_time = bass_note['start_time']
    current_note = bass_notes[i]

    # 다음 노트의 시작 시간 찾기
    next_start_time = None
    rest_duration = None
    for j in range(i + 1, len(clean_midi)):
        if clean_midi[j][0] == 'note_on' and clean_midi[j][1] == next_note and clean_midi[j][3] == clean_midi[i][3]:
            candidate_next_start_time = clean_midi[j][2]

            # 다음 노트의 시작 시간이 현재 노트의 시작 시간보다 큰 경우에만 설정
            if candidate_next_start_time > current_start_time:
                if next_start_time is None or candidate_next_start_time <= next_start_time:
                    next_start_time = candidate_next_start_time
    
    # 다음 노트의 시작 시간이 존재하면 설정, 없으면 None으로 설정
    bass_note['next_start_time'] = next_start_time
    rest_duration = next_start_time - bass_note['end_time'] if next_start_time is not None else None
    bass_note['rest_duration'] = rest_duration


output_notes = []

# 마지막 베이스 노트에 대한 처리
last_bass_note = bass_notes[-1]
last_bass_note['next_start_time'] = None
last_bass_note['rest_duration'] = None

for i, bass_note in enumerate(bass_notes[:-1]):
    rest_duration = bass_note['rest_duration']
    next_start_time = bass_notes[i + 1]['start_time']

    # 추가된 부분: rest_duration이 0.0이 아닌 경우에만 배열에 추가
    if rest_duration is not None and rest_duration != 0.0:
        note_name = midi_note_to_name(bass_note['note'])
        rhythmic_name = bass_note['rhythmic_name']
        output_notes.append([note_name, rhythmic_name])

        # 추가된 부분: 다음 노트의 시작 시간이 현재 노트의 종료 시간과 같으면 B4를 추가하지 않음
        if next_start_time != bass_note['end_time']:
            rhythmic_name = rest_duration_to_rhythmic_name(rest_duration)
            # 추가된 부분: Rhythmic Name이 빈 문자열이 아닌 경우에만 B4 추가
            if rhythmic_name != '':
                output_notes.append(['B4', rhythmic_name])

# 마지막 노트 처리
last_note = bass_notes[-1]
last_rest_duration = last_note['rest_duration']

if last_rest_duration is not None and last_rest_duration != 0.0:
    last_note_name = midi_note_to_name(last_note['note'])
    last_rhythmic_name = last_note['rhythmic_name']
    output_notes.append([last_note_name, last_rhythmic_name])

    # 마지막 노트의 다음 시작 시간이 없으면 B4 추가하지 않음
    if last_note['next_start_time'] is not None:
        rhythmic_name = rest_duration_to_rhythmic_name(last_rest_duration)
        # 추가된 부분: Rhythmic Name이 빈 문자열이 아닌 경우에만 B4 추가
        if rhythmic_name != '':
            output_notes.append(['B4', rhythmic_name])
        
rec_list = []
for note_info in output_notes:
    rec_list.append([note_info[1],note_info[0]])

# print(rec_list)

# # 결과 저장
# with open('bell_piano.txt', 'w') as file:
#     for note_info in output_notes:
#         # 파일에 output_notes의 정보를 기록
#         file.write(f"{note_info[1]}, {note_info[0]}\n")
#
# print('Result saved')

temp = group_list(rec_list,15)

print(temp)

def get_number(note):
    mapping = {
        'E4': '9/3',
        'F4': '10/3',
        'F#4': '11/3',
        'G♭4': '11/3',
        'G4': '12/3',
        'G#4': '13/3',
        'A♭4': '13/3',
        'A4': '14/3',
        'A#4': '15/3',
        'B♭4': '15/3',
        'B4': '16/3',
        'C5': '17/3',
        'C#5': '14/2',
        'D♭5': '14/2',
        'D5': '15/2',
        'D#5': '16/2',
        'E♭5': '16/2',
        'E5': '12/1',
        'F5': '13/1',
        'F#5': '14/1',
        'G♭5': '14/1',
        'G5': '15/1',
        'G#5': '16/1',
        'A♭5': '16/1',
        'A5': '17/1',
        'A#5': '18/1',
        'B♭5': '18/1',
        'B5': '19/1',
        'C6': '20/1',
        'C#6': '21/1',
        'D♭6': '21/1',
        'D6': '22/1',
        'B3': '0/2',
        'C4': '1/2',
        'C#4': '2/2',
        'D♭4': '2/2',
        'D4': '3/2',
        'D#4': '4/2',
        'E♭4': '4/2',
        'G3': '5/4',
        'G#3': '6/4',
        'A♭3': '6/4',
        'A3': '7/4',
        'A#3': '8/4',
        'B♭3': '8/4',
        'D3': '0/4',
        'D#3': '1/4',
        'E♭3': '1/4',
        'E3': '2/4',
        'F3': '3/4',
        'F#3': '9/5',
        'G♭3': '9/5',
        'A2': '0/5',
        'A#2': '1/5',
        'B♭2': '1/5',
        'B2': '2/5',
        'C3': '3/5',
        'C#3': '4/5',
        'D♭3': '4/5',
        'E2': '0/6',
        'F2': '1/6',
        'F#2': '2/6',
        'G♭2': '2/6',
        'G2': '3/6',
        'G#2': '4/6',
        'A♭2': '4/6'
    }
    return mapping.get(note, "해당 문자열에 대한 숫자가 없습니다.")

def convert_to_sentence(mapped_result_list):
    memorize_index = []
    sen = ""

    note_mapping = {
        'Treble': ('\ntabstave notation=true clef=treble\nnotes', 0),
        'Quarter Note': (' :q ', 0.25),
        'Half Note': (' :h ', 0.5),
        'Dotted Quarter Note': (' :qd ', 0.375),
        'Eight Note': (' :8 ', 0.125),
        'Eight rest': (' :8 ## ', 0.125),
        'Whole Note': (' :w ', 1),
        'Quarter rest': (' :4 ## ', 0.25),
        'Dotted Eight Note': (' :8d ', 0.1875),
        'Sixteen Note': (' :16 ', 0.0625),
        'Sixteenth rest': (' :16 ## ', 0.0625),
        'Dotted Half Note': (' :hd ', 0.75),
        'Half rest' : (' :h ## ', 0.5),
        'Dotted Eighth rest' : (' :8d ## ', 0.1875),
        'Dotted Quarter rest' : (' :4d ## ', 0.375),
        'Dotted Half rest' : (' :hd ## ', 0.75)
    }

    for result in mapped_result_list:
        print(result)
        k = 0  # 각 result 리스트마다 k 값을 초기화
        for i in range(len(result)):
            action, value = note_mapping.get(result[i][0], ('', 0))
            if k >= 1:
                memorize_index.append([i])
                sen += " |"
                k = 0
            sen += action
            if result[i][0] not in ['Treble', 'Quarter Rest']:
                sen += get_number(result[i][1])
            k += value

    sen += " =|="
    return sen

result = convert_to_sentence(temp)
print(result)