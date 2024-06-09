import random, os, subprocess, json
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from skimage.filters import gaussian

def tts(path):
    def hms_to_sec(time_str):
        time_str = time_str.replace('.',':')
        hour, minute, second, milsec = map(str, time_str.split(':'))
        
        return int(hour) * 3600 + int(minute) * 60 + int(second) + int(milsec) * 0.001

    def sec_to_hms(seconds):
        hour = int(seconds // 3600)
        minute = int((seconds % 3600) // 60)
        second = str(round(seconds % 60, 3))
        s1, s2 = map(str, second.split('.'))
        for i in range(2-len(s1)):
            s1 = '0' + s1
        for i in range(3-len(s2)):
            s2 = s2 + '0'
        return f"{hour:02d}:{minute:02d}:{s1},{s2}"
    
    command = [
        "edge-tts", 
        "-f", 
        path+".txt", 
        "-v", 
        "zh-CN-YunJianNeural", 
        #"--rate=-15%", 
        "--rate=+35%", 
        "--write-media", 
        "tmp.mp3", 
        "--write-subtitles", 
        "tmp.srt"
    ]
    subprocess.run(command, encoding="utf-8")
    with open("tmp.srt", "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    subtitles = []
    current_subtitle = None

    for line in lines:
        line = line.strip()
        
        if not line: continue
        if line == "WEBVTT": continue
        if current_subtitle is None: current_subtitle = []
        current_subtitle.append(line)
        
        if len(current_subtitle) == 2:
            subtitles.append(current_subtitle)
            current_subtitle = None

    with open("tmp.srt", "w", encoding="gbk") as outfile:
        data = []
        for subtitle in subtitles:
            times = subtitle[0].split(" --> ")
            start_time, end_time = hms_to_sec(times[0]), hms_to_sec(times[1])
            
            duration = end_time - start_time
            content = subtitle[1].split()
            num_segments = len(content)
            duration_segments = duration/num_segments
            current_time = start_time
            for segment in content:
                new_subtitle = [
                    sec_to_hms(current_time), 
                    sec_to_hms(current_time + duration_segments - 0.01), 
                    segment]
                data.append(new_subtitle)
                current_time += duration_segments
        
        
        """
        for index, sub in enumerate(data):
            if len(sub[2]) <= 3:
                sub[1] = data[index + 1][1]
                sub[2] += data[index + 1][2]
                data.pop(index+1)
        """
        
        
        for i, line in enumerate(data):
            outfile.write(str(i+1)+"\n"+
                        f"{line[0]} --> {line[1]}"+"\n"+
                        line[2]+"\n\n")

def blur(image):
    return gaussian(image.astype(float), sigma=8)

def makeVid(bgvid, vidDuration, index):
    audio = AudioFileClip("tmp.mp3")
    audioDuration = audio.duration
    
    """
    img = ImageClip("Files/Data/"+str(index)+".jpg").set_position(('center', 400)).set_duration(audioDuration)
    img = img.resize(width=1080)
    img.duration = audioDuration
    """
    
    startPoint = random.uniform(0, vidDuration - audioDuration)
    subVid = bgvid.subclip(startPoint, startPoint+audioDuration)
    
    with open("Files/config.json", "r") as json_file:
        data = json.load(json_file)
        fontSize = data["font_size"]
        fontColor = data["font_color"]
        strokeWidth = data["stroke_width"]
        strokeColor = data["stroke_color"]
    
    generator = lambda txt: TextClip(txt, 
                                     font="./Files/Font/font.ttf", 
                                     color=fontColor, 
                                     fontsize=fontSize, 
                                     stroke_width=strokeWidth, 
                                     stroke_color=strokeColor)
    subtitles = SubtitlesClip("tmp.srt", generator, encoding="gbk")
    subtitles = subtitles.set_position(("center", 1440))
    
    #final = CompositeVideoClip([subVid, img, subtitles], size=bgvid.size).set_audio(audio)
    final = CompositeVideoClip([subVid, subtitles], size=bgvid.size).set_audio(audio)
    final.write_videofile("./Files/Output/"+str(index)+".mp4", codec = "libx264")

def main():
    Vid = VideoFileClip("./Files/bg.mp4")
    data_path = "./Files/Data"
    file_list = os.listdir(data_path)
    
    for i in range(int(len(file_list)/2)):
        os.system("cls")
        print("视频生成中: "+str(i)+"/"+str(int(len(file_list)/2)), end="\n\n")
        tts("./Files/Data/"+str(i))
        #makeVid(Vid.fl_image(blur), Vid.duration, i)
        makeVid(Vid, Vid.duration, i)

if __name__ == "__main__":
    main()
    



"""
import json
import random
import subprocess

def get_audio_duration(audio_file):
    result = subprocess.run(
        ['ffprobe', '-i', audio_file, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv="p=0"'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def make_vid(bgvid, vid_duration, index):
    audio = "tmp.mp3"
    audio_duration = get_audio_duration(audio)
    
    start_point = random.uniform(0, vid_duration - audio_duration)
    
    # Extract subclip from background video
    subprocess.run(['ffmpeg', '-ss', str(start_point), '-i', bgvid, '-t', str(audio_duration), '-c', 'copy', 'subclip.mp4'])
    
    # Load configuration
    with open("Files/config.json", "r") as json_file:
        data = json.load(json_file)
        font_size = data["font_size"]
        font_color = data["font_color"]
        stroke_width = data["stroke_width"]
        stroke_color = data["stroke_color"]
    
    # Overlay subtitles
    subtitle_filter = f"subtitles=tmp.srt:force_style='FontName=./Files/Font/font.ttf,FontSize={font_size},PrimaryColour=&H{font_color},OutlineColour=&H{stroke_color},BorderStyle={stroke_width}'"
    subprocess.run(['ffmpeg', '-i', 'subclip.mp4', '-vf', subtitle_filter, 'subclip_with_subtitles.mp4'])
    
    # Combine video with audio
    output_file = f"./Files/Output/{index}.mp4"
    subprocess.run(['ffmpeg', '-i', 'subclip_with_subtitles.mp4', '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', output_file])

# Example usage
make_vid('bgvid.mp4', 600, 1)

"""