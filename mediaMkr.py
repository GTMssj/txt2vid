import random, os, subprocess, json, time

def tts(path):
    command = [
        "edge-tts", 
        "-f", 
        path, 
        "-v", 
        "zh-CN-YunJianNeural", 
        "--rate=+35%", 
        "--write-media", 
        "tmp.mp3", 
        "--write-subtitles", 
        "tmp.srt"
    ]
    subprocess.run(command, encoding="utf-8")
    lines = []
    with open('./tmp.srt', 'r', encoding='utf-8') as file:
        for line in file:
            if line != "WEBVTT" and "-->" not in line and line != "":
                trimline = line.replace(' ', '')
                modline = ' '.join(trimline[i:i+10] for i in range(0, len(trimline), 10))
                lines.append(modline)
            else:
                lines.append(line)
    with open('./tmp.srt', 'w', encoding='utf-8') as file:
        for line in lines:
            file.write(line)

def makeVid(bgvid, index):
    def duration(path:str):
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', '-i', path], 
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)

    def mk_subvid(start:float, length:float):
        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', bgvid, '-ss', str(start), '-t', str(length), 'sub.mp4'])

    def mk_titlevid(fontSize, fontColor, strokeWidth, strokeColor):
        subtitle_filter = f"subtitles=tmp.srt:force_style='fontfile=/data/data/com.termux/files/home/code/python/txt2vid/Files/Font/font.ttf,FontSize={fontSize},PrimaryColour=&H{fontColor},OutlineColour=&H{strokeColor},Outline=2,MaxGlyphW=5'"
        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'sub.mp4', '-vf', subtitle_filter, 'title.mp4', '-y'])

    def mk_finvid(audio:str, name:str):
        output_file = f"./Files/Output/{name}.mp4"
        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'title.mp4', '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', output_file])

#   =================================   #

    with open("Files/config.json", "r") as json_file:
        data = json.load(json_file)
        fontSize = data["font_size"]
        fontColor = data["font_color"]
        strokeWidth = data["stroke_width"]
        strokeColor = data["stroke_color"]

    audio = "tmp.mp3"
    subtitle = "tmp.srt"
    audioDuration = duration(audio)
    startPoint = random.uniform(0, duration(bgvid) - audioDuration)
    print("正在裁剪视频...")
    mk_subvid(startPoint, audioDuration)
    print("正在添加字幕...")
    mk_titlevid(fontSize, fontColor, strokeWidth, strokeColor)
    print("正在添加音频...")
    mk_finvid(audio, index)
    subprocess.run(['rm', './sub.mp4', 'title.mp4', 'tmp.srt', 'tmp.mp3'])
    
def main():
    bg_vid = "./Files/bg.mp4"
    data_path = "./Files/Data"
    file_list = os.listdir(data_path)
    
    for i, filename in enumerate(file_list):
        os.system("clear")
        print("视频生成中: "+str(i+1)+"/"+str(int(len(file_list))), end="\n\n")
        time.sleep(1)
        print(f"当前：{filename[:-4]}\n")
        print("正在语音转文字...")
        tts("./Files/Data/"+filename)
        time.sleep(0.5)
        makeVid(bg_vid, filename[:-4])

if __name__ == "__main__":
    main()
