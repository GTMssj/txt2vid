import random, os, subprocess, json, time

def tts(path):
    command = [
        "edge-tts", 
        "-f", 
        path+".txt", 
        "-v", 
        "zh-CN-YunJianNeural", 
        "--rate=+35%", 
        "--write-media", 
        "tmp.mp3", 
        "--write-subtitles", 
        "tmp.srt"
    ]
    subprocess.run(command, encoding="utf-8")
    '''
    file_name = 'tmp.srt'  # 替换为你的文件名
    with open(file_name, 'r') as file:  # 以读模式打开文件
        data = file.read()  # 读取文件内容
    data_no_spaces = data.replace(' ', '')
    with open(file_name, 'w') as file:
        file.write(data_no_spaces)
    '''

def makeVid(bgvid, index):
    def duration(path:str):
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', '-i', path], 
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)

    def mk_subvid(start:float, length:float):
        subprocess.run(['ffmpeg', '-i', bgvid, '-ss', str(start), '-t', str(length), 'sub.mp4'])

    def mk_titlevid():
        with open("Files/config.json", "r") as json_file:
            data = json.load(json_file)
            fontSize = data["font_size"]
            fontColor = data["font_color"]
            strokeWidth = data["stroke_width"]
            strokeColor = data["stroke_color"]

        #subtitle_filter = f"subtitles=tmp.srt:force_style='FontName=./Files/Font/font.ttf,FontSize={fontSize},PrimaryColour=&H{fontColor},OutlineColour=&H{strokeColor},BorderStyle={strokeWidth}'"
        subtitle_filter = f"subtitles=tmp.srt:force_style='FontName=./Files/Font/font.ttf,FontSize={fontSize},PrimaryColour=&H{fontColor},OutlineColour=&H{strokeColor},Outline=2,MaxGlyphW=5'"
        subprocess.run(['ffmpeg', '-i', 'sub.mp4', '-vf', subtitle_filter, 'title.mp4', '-y'])

    def mk_finvid(audio:str, index:int):
        output_file = f"./Files/Output/{index}.mp4"
        subprocess.run(['ffmpeg', '-i', 'title.mp4', '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', output_file])

#   =================================   #

    audio = "tmp.mp3"
    subtitle = "tmp.srt"
    audioDuration = duration(audio)
    startPoint = random.uniform(0, duration(bgvid) - audioDuration)
    mk_subvid(startPoint, audioDuration)
    mk_titlevid()
    mk_finvid(audio, index)
    subprocess.run(['rm', './sub.mp4', 'title.mp4'])
    
def main():
    bg_vid = "./Files/bg.mp4"
    data_path = "./Files/Data"
    file_list = os.listdir(data_path)
    
    for i in range(int(len(file_list))):
        os.system("clear")
        print("视频生成中: "+str(i+1)+"/"+str(int(len(file_list))), end="\n\n")
        time.sleep(1)
        tts("./Files/Data/"+str(i))
        makeVid(bg_vid, i)

if __name__ == "__main__":
    main()
