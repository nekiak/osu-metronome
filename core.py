import os
import shutil

from pydub import AudioSegment


def parse_timing_points(file_path):
    timing_points = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    in_timing_points = False
    for line in lines:
        line = line.strip()
        if line == "[TimingPoints]":
            in_timing_points = True
            continue
        if in_timing_points:
            if line == "" or line.startswith("["):
                break
            elements = line.split(',')
            if len(elements) >= 7 and elements[6] == '1':
                offset = float(elements[0])
                bpm = 60000 / float(elements[1])
                time_signature = int(elements[2])
                timing_points.append((offset, bpm, time_signature))
    return timing_points


def parse_general_section(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    in_general_section = False
    audio_filename = None
    for line in lines:
        line = line.strip()
        if line == "[General]":
            in_general_section = True
            continue
        if in_general_section:
            if line == "" or line.startswith("["):
                break
            if line.startswith("AudioFilename:"):
                audio_filename = line.split(":", 1)[1].strip()
                break
    if not audio_filename:
        raise ValueError("AudioFilename not found in the [General] section.")
    return audio_filename


def add_metronome_to_audio(osu_path, strong_beat_path, weak_beat_path, gain_db=0, music_db=0, progress_callback=None):
    timing_points = parse_timing_points(osu_path)
    audio_filename = parse_general_section(osu_path)

    osu_dir = os.path.dirname(osu_path)
    audio_path = os.path.join(osu_dir, audio_filename)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    create_backup(audio_path)

    audio = AudioSegment.from_file(audio_path).apply_gain(music_db)
    primary_tick = AudioSegment.from_file(strong_beat_path).apply_gain(gain_db)
    secondary_tick = AudioSegment.from_file(weak_beat_path).apply_gain(gain_db)

    total_duration = len(audio)
    metronome_events = []

    for i, (offset, bpm, time_signature) in enumerate(timing_points):
        interval = 60000 / bpm
        next_offset = timing_points[i + 1][0] if i + 1 < len(timing_points) else total_duration
        current_time = offset

        while current_time < next_offset:
            for beat in range(time_signature):
                beat_time = current_time + (beat * interval)
                if beat_time >= next_offset or beat_time >= total_duration:
                    break
                sound = primary_tick if beat == 0 else secondary_tick
                metronome_events.append((beat_time, sound))
            current_time += time_signature * interval

    metronome_events.sort(key=lambda x: x[0])

    total_events = len(metronome_events)
    processed_events = 0

    metronome_audio = AudioSegment.silent(duration=total_duration)
    for beat_time, sound in metronome_events:
        position = int(round(beat_time))
        metronome_audio = metronome_audio.overlay(sound, position=position)

        processed_events += 1
        if progress_callback:
            progress = processed_events / total_events
            progress_callback(progress)

    output_audio = audio.overlay(metronome_audio)

    temp_output_path = f"{audio_path}.temp"
    output_audio.export(temp_output_path, format="mp3")
    os.replace(temp_output_path, audio_path)


def create_backup(file_path):
    backup_path = file_path + ".backup1"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print(f"Backup already exists: {backup_path}")


def restore_backup(file_path):
    backup_path = file_path + ".backup1"
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"No backup found for: {file_path}")

    shutil.copy2(backup_path, file_path)
    print(f"Backup restored: {file_path}")
