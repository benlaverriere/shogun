# big change in this version:
# making things work in fullscreen (under maximus)
# [this started in 0.4, but I want to preserve the
#  first version that worked as a single-window app.]
# also, moving to the new syntax for *.shogun files,
# as in demo.shogun

# http://code.activestate.com/recipes/534124/
# ^ splash screen?

# For my own good, naming guidelines:
# Object.multiword_property_or_function(CONSTANT)

from Tkinter import *
from FileDialog import FileDialog
from PIL import Image, ImageTk

import pypm
import array
import time
import re
import os

# constants used by pypm for port types
INPUT = 0
OUTPUT = 1

NUM_MSGS = 100

# used for translating patch files to numeric bank+patch pairs
ALLBANKS = "ABCDEF"

# global storage for current patch number (not MIDI patch number)
# and latency value
patch = -1
latency = 0

# just a number, recognized by pypm
in_port = None
out_port = None
latency_var = None

# the actual objects
MidiIn = None
MidiOut = None

# the list, obviously
patchlist = []

# the main Shogun window
App = None
icon_path = "taiko.png"
background_path = "splash.png"
#background_image = ImageTk.PhotoImage(Image.open(background_path))

# three event handlers for interface-based patch changing...

def prev_patch(event):
    global patch
    set_patch(patch-1)

def next_patch(event):
    global patch
    set_patch(patch+1)

def change_patch(event):
    temp_patch = App.get_status()
    if not temp_patch == "":
        set_patch(long(temp_patch))
        App.clear_entry()

# and this one does the actual number-crunching and patch-changing
def set_patch(newpatch):
    global patch
    if len(patchlist) > 0:
        if newpatch < 0:
            patch = 0
        elif newpatch > len(patchlist)-1:
            patch = len(patchlist)-1
        else:
            patch = newpatch
        # print "Patch change: ", patch
        App.set_status(patch)
        send_patch_change(patchlist[patch][1],patchlist[patch][2],patchlist[patch][3])

class Shogun:

    def set_status(self, new_status):
        global patchlist
        self.status.set(new_status) # also updates label automagically
        fullpatchstr = patchlist[new_status][1]
        if not patchlist[new_status][2] == None:
            fullpatchstr = fullpatchstr + "(" + str(patchlist[new_status][2]) + ")"
        fullpatchstr = fullpatchstr + " " + str(patchlist[new_status][3])
        self.fullpatch.set(fullpatchstr)

    def get_status(self):
        return self.shell.get()

    def clear_entry(self):
        self.shell.delete(0,END)

    def _load_file(self):
        global patchlist
        d = FileDialog(self.frame)
        # is it possible to set the icon for the file dialog?
        patchfile = d.go()
        if patchfile is None:
            return
        else:
            source = open(patchfile, 'r')
            App.filename.set(os.path.basename(patchfile))
            for line in source:
                m = re.search('^((['+ALLBANKS+'G])(\d)? (\d+))', line)
                if m:
                    patchlist.append((MidiOut,m.group(2),m.group(3),int(m.group(4))))
        return

    def _set_input(self):
        global MidiIn
        pypm.Terminate()
        pypm.Initialize()
        MidiIn = pypm.Input(in_port.get())

    def _set_output(self):
        global MidiOut
        global latency
        if not MidiOut == None:
            del MidiOut
            pypm.Terminate()
        pypm.Initialize()
        tempthing = out_port.get()
        MidiOut = pypm.Output(tempthing,latency)

    def _set_latency(self):
        global latency
        latency = long(latency_var.get())

    def __init__(self, master):

        self.frame = Frame(master)
        self.frame.bind_all("<Left>", prev_patch)
        self.frame.bind_all("<Right>", next_patch)
        self.frame.bind_all("<Return>", change_patch)
	# set background image?
        self.frame.pack()

        self.status = StringVar()
        self.fullpatch = StringVar()
        self.filename = StringVar()
        global patch
        self.status.set(patch)
        self.filename.set("")

        btn_frame = Frame(self.frame)
        btn_frame.pack(side=TOP)

	dev_frame = Frame(self.frame)
	dev_frame.pack(side=BOTTOM)

	list_frame = Frame(dev_frame)
        list_frame.pack(side=TOP)

        latency_frame = Frame(dev_frame)
        latency_frame.pack(side=BOTTOM)

        in_frame = Frame(list_frame)
        in_frame.pack(side=LEFT)

        out_frame = Frame(list_frame)
        out_frame.pack(side=RIGHT)

        in_lbl = Label(in_frame, text = "Input Devices")
        in_lbl.pack(side=TOP, fill = BOTH, expand = YES)

        out_lbl = Label(out_frame, text = "Output Devices")
        out_lbl.pack(side=TOP, fill = BOTH, expand = YES)

	global in_port
	global out_port
	global latency_var

	in_port = IntVar()
        out_port = IntVar()
        latency_var = IntVar()

        in_port.set(-1)
        out_port.set(-1)
        latency_var.set(0)

	for loop in range(pypm.CountDevices()):
            interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
            if(inp == 1):
                self.curr_button = Radiobutton(in_frame, text = name, variable = in_port, value = loop, indicatoron = 0, command = self._set_input)
                if(opened == 1):
                    self.curr_button.select()
                self.curr_button.pack(side=TOP, fill = BOTH, expand = YES)
            elif(outp == 1):
                self.curr_button = Radiobutton(out_frame, text = name, variable = out_port, value = loop, indicatoron = 0, command = self._set_output)
                if(opened == 1):
                    self.curr_button.select()
                self.curr_button.pack(side=TOP, fill = BOTH, expand = YES)

        # TODO: fix layout here...

        latency_field = Entry(latency_frame, textvariable = latency_var)
        latency_field.pack(side=LEFT, fill = BOTH, expand = YES)

        latency_btn = Button(latency_frame, text = "Set Latency", command = self._set_latency)
        latency_btn.pack(side=RIGHT, fill = BOTH, expand = YES)


        #self.in_btn = Button(btn_frame,text="Test Input",command=test_input)
        #self.in_btn.pack(side=LEFT)

        self.file_btn = Button(btn_frame,text="Load File",command=self._load_file)
        self.file_btn.pack(side=LEFT)

#        self.dev_btn = Button(btn_frame, text="Devices", command=self._pick_devices)
#        self.dev_btn.pack(side=LEFT)

        self.out_btn = Button(btn_frame,text="Test Output",command=test_output)
        self.out_btn.pack(side=LEFT)

        self.shell = Entry(self.frame,font=("Envy Code R", 72, "bold"),width=3)
        self.shell.focus_force()
        self.shell.pack(side=BOTTOM, fill = BOTH, expand = YES)
        
        self.file_lbl = Label(self.frame, textvariable=self.filename)
        self.file_lbl.pack(side=TOP)
        
        self.label_thing = Label(self.frame, textvariable=self.status, font=("Envy Code R", 72, "bold"))
        self.label_thing.pack(side=TOP)

        self.fullpatch_lbl = Label(self.frame, textvariable=self.fullpatch, font=("Envy Code R", 14))
        self.fullpatch_lbl.pack(side=TOP)

	#background_image = Image.open(background_path)
	#self.image_thing = Label(self.frame, image=background_image)
	#self.image_thing = Label(self.frame, image=background_image)
	#self.image_thing.image = background_image
	#self.image_thing.pack(side=LEFT)
        
    # this quit method based on code by Bill Allen,
    # http://www.3dartist.com/WP/python/tknotes.htm
    def quit(self):
        del MidiOut
        del MidiIn
        pypm.Terminate()
        self.frame.quit()
        root.quit()

# #################################### begin MIDI/pypm code

def send_patch_change(bank, banknum, patch):

    global MidiOut
    
    if not MidiOut == None:
        bankpos = ALLBANKS.find(bank.upper())
        if(bankpos < 0):
            # we know it's one of the G banks
            if not isinstance(banknum, int) : banknum = 0
            MidiOut.Write([[[0xB0,0,121,121],pypm.Time()]])
            MidiOut.Write([[[0xB0,32,int(banknum),int(banknum)],pypm.Time()]])
            MidiOut.Write([[[0xC0,patch,0],pypm.Time()]])
        else:
            # print "Changing to bank "+str(bankpos)+", patch "+str(patch)+"..."
            MidiOut.Write([[[0xB0,0,63],pypm.Time()]])
            MidiOut.Write([[[0xB0,32,bankpos],pypm.Time()]])
            MidiOut.Write([[[0xc0,patch,0],pypm.Time()]])

def test_output():

    global MidiOut
    
    program_number = 64
    bank_number = 1
    
    # note that the single note-on tests may not actually
    # be audible, but you should at least see the patch/bank
    # changes and hear the chord.
    MidiOut.Write([[[0xB0,0,63],pypm.Time()]])
    MidiOut.Write([[[0xB0,32,bank_number],pypm.Time()]])
    MidiOut.Write([[[0xc0,program_number,0],pypm.Time()]])
    MidiOut.Write([[[0x90,60,100],pypm.Time()]])
    MidiOut.Write([[[0x90,60,0],pypm.Time()+1000]])
    MidiOut.WriteShort(0x90,60,100)
    temp_time = 1000
    while temp_time > 0:
        temp_time -= 1
    MidiOut.WriteShort(0x90,60,0)
    chord = [60, 67, 76, 83, 90]
    chord_list = []
    MidiTime = pypm.Time()
    for i in range(len(chord)):
        chord_list.append([[0x90,chord[i],100], MidiTime + 1000 * i])
    MidiOut.Write(chord_list)
    while pypm.Time() < MidiTime + 1000 + len(chord) * 1000 : pass
    chord_list = []
    # seems a little odd that they don't update MidiTime here...
    for i in range(len(chord)):
        chord_list.append([[0x90,chord[i],0], MidiTime + 1000 * i])
    MidiOut.Write(chord_list)

def test_input():

    global MidiIn

    InputTestWindow = Toplevel()
    InputTestWindow.title("MIDI Input Test")
#    InputTestWindow.iconbitmap(icon_path)

    input_test_data = StringVar()
    input_test_data.set("")

    InputTestConsole = Message(InputTestWindow, textvariable = input_test_data)
    InputTestConsole.pack()
    if not MidiIn == None:
        MidiIn.SetFilter(pypm.FILT_ACTIVE | pypm.FILT_CLOCK)
        for message_counter in range(1,NUM_MSGS+1):
            while not MidiIn.Poll(): time.sleep(.01)
            MidiData = MidiIn.Read(1) # read only 1 message at a time
            input_test_data.set(input_test_data.get() + "\nGot message " + message_counter  + ": time "  + MidiData[0][1] + ", " + MidiData[0][0][0] + " " + MidiData[0][0][1] + " " + MidiData[0][0][2] + MidiData[0][0][3])
            # NOTE: most Midi messages are 1-3 bytes, but the 4 byte is returned for use with SysEx messages.
        MidiIn.RemoveFilter() # I don't yet know if this command exists(!)
    else:
        input_test_data.set("No MIDI input device selected.")

# #################################### begin actual code

root = Tk()
root.title("Shogun")
#root.iconbitmap(icon_path)

pypm.Initialize() # always call this first, or OS may crash when you try to open a stream

App = Shogun(root)

root.mainloop()
