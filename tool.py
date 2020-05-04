import os
import sys
import shutil
from pycaption import SRTReader, DFXPWriter
from pathlib import Path
from subprocess import call
import pysubs2


# Screen Clear
def clear():
    _ = call('clear' if os.name == 'posix' else 'cls', shell=True)


# Y/N Question (Default No)
def ynask(text):
    ans = str(input(text + " (y/N): ")).lower().strip()
    if ans[:1] == 'y':
        return True
    if ans[:1] == 'n':
        return False
    print("Defaulting to No.")
    return False


def dfxpconv(filename=str, ckeep=bool):
    fsrt = open(filename, "r", encoding='utf-8', errors='ignore')
    srtcont = fsrt.read()
    fdfxp = open(filename.replace(".srt", ".dfxp"), "wb")

    # Super Netflix Compatibility
    # Converter that is used (DFXPWriter) uses a different set of rules
    # than what Super Netflix (and Netflix) wants.
    # Doing this will avoid the "M7034" error.
    # It will also remove any formatting as there is no such thing as formatting
    # in the Netflix Player.
    dfxpedit = DFXPWriter().write(SRTReader().read(srtcont))
    dfxpedit = dfxpedit.replace("<tt xml:lang=\"en\" xmlns:=\"http://www.w3.org/ns/ttml\" "
                                "xmlns:tts=\"http://www.w3.org/ns/ttml#styling\">",
                                "<tt xml:lang='en' xmlns='http://www.w3.org/2006/10/ttaf1' "
                                "xmlns:tts='http://www.w3.org/2006/10/ttaf1#style'>")
    dfxpedit = dfxpedit.replace("<div region=\"bottom\" xml:lang=\"en-US\">", "<div xml:id=\"captions\">")
    dfxpedit = dfxpedit.replace("&lt;font face=\"Open Sans Semibold\" size=\"36\"&gt;", "")
    dfxpedit = dfxpedit.replace("&lt;/font&gt;", "")
    dfxpedit = dfxpedit.replace(" region=\"bottom\" style=\"default\"", "")
    dfxpedit = dfxpedit.replace("&lt;b&gt;", "")
    dfxpedit = dfxpedit.replace("&lt;/b&gt;", "")
    dfxpedit = dfxpedit.replace("&lt;i&gt;", "")
    dfxpedit = dfxpedit.replace("&lt;/i&gt;", "")
    dfxpedit = dfxpedit.replace("{\\an8}", "")

    dfxpedit = dfxpedit.encode('utf-8', errors='replace')
    fdfxp.write(dfxpedit)
    fsrt.close()
    fdfxp.close()
    if ckeep:
        return
    if not ckeep:
        os.remove(filename)
        return


def getdir():
    subfold = False
    condir = False
    currdir = ""
    dirlist = []

    if Path("subs").is_dir():
        subfold = True
    print("Directories Available:")
    print("1. Current Directory")
    print("2. Custom Directory")
    if subfold:
        print("3. \"subs\" Directory")

    while True:
        if condir:
            break
        foldopt = input("Choose a directory: ")
        if foldopt == "1":
            return "", "1"
        if foldopt == "3" and subfold:
            return "subs/", "3"
        if foldopt == "2":
            print("Custom Directory List:")
            rootdir = os.listdir(os.getcwd())
            i = 1
            for odir in rootdir:
                if Path(odir).is_dir():
                    dirlist.append(odir)
                    print(str(i) + ". " + odir)
                    i += 1
                    continue
                else:
                    continue
            i = 1
            cdir = input("Choose a directory: ")
            while True:
                currdir = currdir + dirlist[int(cdir) - 1] + "/"
                ldir = os.listdir(currdir)
                dirlist = []
                for odir in ldir:
                    if Path(currdir + odir).is_dir():
                        dirlist.append(odir)
                        print(str(i) + ". " + odir)
                        i += 1
                        continue
                    else:
                        continue
                i = 1
                cdir = input("Choose a directory (Press Y to confirm current directory): ")
                if cdir.lower() == "y":
                    return currdir, foldopt


def getsubfile(filetype=".srt"):
    # Will give a prompt for the user to choose the sub file.
    # Current file formats can be given in ".XXX" as an argument to filter file formats.
    multi = False
    filelist = []
    fileout = []
    filenum = 1

    currdir, foldopt = getdir()

    print("Detected Subtitles: ")
    if foldopt == "1":
        outdir = ""
        currdir = os.listdir(os.getcwd())
    if foldopt == "2":
        outdir = currdir
        currdir = os.listdir(currdir)
    elif foldopt == "3":
        outdir = "subs/"
        currdir = os.listdir("subs")
    for file in currdir:
        if file.endswith(filetype) and not Path(outdir + file).is_dir():
            print(str(filenum) + ". " + file)
            filelist.append(file)
            filenum += 1
            continue
        else:
            continue
    fileopt = input("Choose the subtitle file (Separate files using \",\"): ")
    if "," in fileopt:
        multi = True

        fileopt = fileopt.split(",")
        for num in fileopt:
            fileopt = int(num) - 1
            if foldopt == "1" or foldopt == "2":
                fileout.append(filelist[fileopt])
            elif foldopt == "3":
                fileout.append("subs/" + filelist[fileopt])
    else:
        fileopt = int(fileopt) - 1
        fileout.append(filelist[fileopt])
    return fileout, multi, outdir


if __name__ == "__main__":
    print("Subtitle Tools")
    print("Menu:")
    print("1. Sync SRT Time")
    print("2. Convert SRT to DFXP")
    print("3. Convert ASS to SRT")
    print("0. Exit")
    action = input("Please choose your action: ")

    if action == "1":
        print("SRT Syncer")
        files, multi, folder = getsubfile()
        keep = ynask("Do you want to keep the original file?")
        if keep and not multi:
            shutil.copyfile(folder + files[0], folder + files[0].replace(".srt", "_orig.srt"))
        elif keep and multi:
            for file in files:
                shutil.copyfile(folder + file, folder + file.replace(".srt", "_orig.srt"))
        offset = input("What offset do you want to apply? (+XX or -XX): ")
        if offset.startswith("+"):
            offset = offset.replace("+", "")
        if not multi:
            subs = pysubs2.load(folder + files[0])
            subs.shift(s=int(offset))
            subs.save(folder + files[0])
        elif multi:
            for file in files:
                subs = pysubs2.load(folder + files)
                subs.shift(s=int(offset))
                subs.save(folder + file)
        dfxpconvert = ynask("Convert the new SRT file to DFXP?")
        if dfxpconvert:
            if not multi:
                dfxpconv(folder + files[0], True)
            elif multi:
                for file in files:
                    dfxpconv(folder + file, True)
    elif action == "2":
        print("SRT -> DFXP Converter")
        files, multi, folder = getsubfile()
        if not multi:
            dfxpconv(folder + files[0], True)
            print("Converted to DFXP at: " + folder + files[0].replace(".srt", ".dfxp"))
        elif multi:
            for file in files:
                dfxpconv(folder + file, True)
            print("Converted all SRT files to DFXP.")
    elif action == "3":
        print("ASS -> SRT Converter")
        files, multi, folder = getsubfile(".ass")
        if not multi:
            subs = pysubs2.load(folder + files[0])
            subs.save(path=folder + files[0].replace(".ass", ".srt"), format="srt", encoding='utf-8')
            print("ASS file is converted to SRT file at: " + folder + files[0].replace(".ass", ".srt"))
        elif multi:
            for file in files:
                subs = pysubs2.load(folder + file)
                subs.save(path=folder + file.replace(".ass", ".srt"), format="srt", encoding='utf-8')
            print("All ASS files has been converted to SRT files.")
    elif action == "0":
        sys.exit()
