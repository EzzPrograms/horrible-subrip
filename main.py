import os
import sys
import subprocess
import webbrowser
import shutil
from pathlib import Path
from tool import clear, ynask, dfxpconv

# Variables
ffmpeg = ".\\ffmpeg\\bin\\ffmpeg.exe"  # Change if you have a custom Windows install (Linux variant coming soon)
dfxp = False
multi = False


def main():
    # User Input
    clear()
    print("HorribleSubs SRT Downloader")
    print("Enter \"cancel\" to cancel your current request.")
    print(
        "If your chosen anime was not right after entering it,\nenter \"animelist\" to go to HorribleSubs to know what "
        "it's name is there.")
    while True:
        anime = input("What anime would you like to download?: ")
        if anime == "animelist":
            print("Opening HorribleSubs site now...")
            webbrowser.open("https://horriblesubs.info/")
        elif anime == "cancel":
            print("Aborting.")
            sys.exit()
        elif anime != "":
            break
        else:
            print("No anime name detected! Enter \"cancel\" or try again.")
    print("For info on episode syntax, enter \"syntax\".")
    while True:
        episode = input("Which episode would you like to download?: ")
        if episode == "cancel":
            print("Aborting.")
            sys.exit()
        elif episode == "syntax":
            print("Episode Syntax:")
            print("-----------------------------------------------------------------------------------------")
            print("| Character |                              Usage                              | Example |")
            print("-----------------------------------------------------------------------------------------")
            print("|     ,     |       Allows to specify more than one episode or option         |   1,6   |")
            print("-----------------------------------------------------------------------------------------")
            print("|     -     |       Specify a range of episodes, including start and end      |   4-10  |")
            print("-----------------------------------------------------------------------------------------")
            print("|     >     |               Bigger than, must be last in order                |    7>   |")
            print("-----------------------------------------------------------------------------------------")
            print("|     <     |               Smaller than, must be first in order              |   <10   |")
            print("-----------------------------------------------------------------------------------------")
            print("|     =     | Equals, in conjunction with < or >, includes the episode number |   11>=  |")
            print("-----------------------------------------------------------------------------------------")
        elif episode != "":
            break
        else:
            print("No episode detected! Enter \"cancel\" or try again.")
    while True:
        conv = ynask("Do you want to convert it to DFXP(Super Netflix)?")
        if conv:
            dfxp = True
            break
        else:
            break
    dir = os.getcwd() + "\\temp"
    try:
        os.mkdir(dir)
    except:
        deltemp = ynask("\"temp\" folder detected! Do you want to delete it?")
        if deltemp:
            print("Deleting the \"temp\" folder.")
            shutil.rmtree("temp")
        else:
            print("Directory Error! Make sure that a folder called \"temp\" is not in this directory!")
            sys.exit()

    # Download a 480p of the video(s)
    subprocess.call(["horrible-downloader", "-d", anime, "-e", episode, "-r", "480", "-o", dir])

    # Check for the video files that horrible-downloader made.
    aniname = os.listdir("temp")
    anifold = "temp/" + aniname[0]

    # Check for multiple episodes
    if len(os.listdir(anifold)) > 1:
        multi = True
    print(len(os.listdir(anifold)))

    # Grab SRT files from the video(s) downloaded
    for file in os.listdir(anifold):
        if file.endswith(".mkv"):
            realep = file.split(" ")[-2:-1]
            realep = realep[0]
            print(realep)
            subprocess.call([ffmpeg, "-i", os.getcwd() + "\\temp\\" + aniname[0] + "\\" + file, "-map", "0:s:0",
                             aniname[0] + " Episode " + realep + ".srt"])
            continue
        else:
            continue
    shutil.rmtree("temp")
    if not dfxp:
        if multi:
            if not Path("subs").is_dir():
                os.mkdir("subs")
            for file in os.listdir(os.getcwd()):
                if file.endswith(".srt"):
                    shutil.move(file, "subs\\" + file)
                    continue
                else:
                    continue
            print("Finished grabbing SRT. SRT files are at the \"subs\" folder.")
        else:
            print("Finished grabbing SRT. SRT file is at: " + aniname[0] + " Episode " + realep + ".srt")
    else:
        print("Finished grabbing SRT.")
        keep = ynask("Do you want to keep the SRT file?(Enables Future Subtitles Offset)")
        if keep:
            clear()
            if not Path("subs").is_dir():
                os.mkdir("subs")
            if multi:
                print("Keeping SRT File.")
                for file in os.listdir(os.getcwd()):
                    dfxpconv(file, True)
                for file in os.listdir(os.getcwd()):
                    if file.endswith(".srt") or file.endswith(".dfxp"):
                        shutil.move(file, "subs\\" + file)
                        continue
                    else:
                        continue
                print("Converted to DFXP. SRT and DFXP files are at the \"subs\" folder.")
            else:
                print("Keeping SRT File.")
                dfxpconv(aniname[0] + " Episode " + realep + ".srt", True)
                shutil.move(aniname[0] + " Episode " + realep + ".srt",
                            "subs\\" + aniname[0] + " Episode " + realep + ".srt")
                shutil.move(aniname[0] + " Episode " + realep + ".dfxp",
                            "subs\\" + aniname[0] + " Episode " + realep + ".dfxp")
                print("SRT file is at: subs/" + aniname[0] + " Episode " + realep + ".srt")
                print("Converted to DFXP. DFXP file is at: subs/" + aniname[0] + " Episode " + realep + ".dfxp")
        else:
            clear()
            if multi:
                print("Deleting SRT file after conversion.")
                for file in os.listdir(os.getcwd()):
                    dfxpconv(file, False)
                if not Path("subs").is_dir():
                    os.mkdir("subs")
                for file in os.listdir(os.getcwd()):
                    if file.endswith(".dfxp"):
                        shutil.move(file, "subs\\" + file)
                        continue
                    else:
                        continue
                print("Converted to DFXP. DFXP files are at the \"subs\" folder.")
            else:
                print("Deleting SRT file after conversion.")
                dfxpconv(aniname[0] + " Episode " + realep + ".srt", False)
                print("Converted to DFXP. DFXP file is at: " + aniname[0] + " Episode " + realep + ".dfxp")


if __name__ == "__main__":
    main()
