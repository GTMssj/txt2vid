import os

def time_to_sec(time_str):
    hour, minute, second = map(float, time_str.split(':'))
    return hour * 3600 + minute * 60 + second

def sec_to_hms(seconds):
    hour = int(seconds // 3600)
    minute = int((seconds % 3600) // 60)
    second = str(round(seconds % 60, 3))
    s1, s2 = map(int, second.split('.'))
    s1 = str(s1)
    if len(s1) == 1: s1 = "0"+s1
    s2 = str(s2)
    return f"{hour:02d}:{minute:02d}:{s1},{s2}"

os.system("cls")

with open("test.srt", "r", encoding="utf-8") as infile:
    lines = infile.readlines()

subtitles = []
current_subtitle = None

for line in lines:
    line = line.strip()
    
    if not line: continue
    if current_subtitle is None: current_subtitle = []
    current_subtitle.append(line)
    
    if len(current_subtitle) == 3:
        subtitles.append(current_subtitle)
        current_subtitle = None

with open("temp.srt", "w", encoding="utf-8") as outfile:
    lines = []
    for subtitle in subtitles:
        times = subtitle[1].split(" --> ")
        start_time, end_time = times[0], times[1]
        start_time = start_time.replace(',', '.')
        end_time = end_time.replace(',', '.')
        start_time = time_to_sec(start_time)
        end_time = time_to_sec(end_time)
        duration = end_time - start_time
        content = subtitle[2].split()
        num_segments = len(content)
        duration_segments = duration/num_segments
        current_time = start_time
        for segment in content:
            new_subtitle = [
                sec_to_hms(current_time), 
                sec_to_hms(current_time + duration_segments), 
                segment]
            lines.append(new_subtitle)
            current_time += duration_segments
        
    for i, line in enumerate(lines):
        outfile.write(str(i+1)+"\n"+
                      f"{line[0]} --> {line[1]}"+"\n"+
                      line[2]+"\n\n")
