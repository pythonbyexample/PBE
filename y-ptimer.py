# Imports {{{
from __future__ import division
import os, sys, wx, time, shelve
import thread
from time import time

"""Y-timer. See README for usage and licensing.

copyright (c) 2008 AK <ak@silmarill.org>
free wav sounds are from freesoundfiles.tintagel.net.
"""

is_win = False
if sys.platform.startswith("win"):
    is_win = True

if is_win:
    import winsound

__version__ = "0.2"
datafile = "conf.dat"
break_time = 20
defaults = {
    # "sound": "wav",
    "sound": "speaker",
    "wavfile" : "ECHOBEL2.wav",
    "spkr_freq" : 2200,
    "mp3fname": "",
    "repeat": False,
    "repeatSound": 5,
    "break_time": 20,
}
# }}}


class ddTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, icon, tooltip, frame):
        wx.TaskBarIcon.__init__(self)
        self.SetIcon(icon, tooltip)
        self.frame = frame
        # At the very least, restore the frame if double clicked.  Add other
        # events later.
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)

    def on_left_dclick(self, e):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def create_popup_menu(self):
        """
        Override with menu functionality, later.
        """
        return None


class Settings(wx.Frame):
    """Main timer class."""
    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, 'Timer Settings', size=(480,
            280), style=wx.DEFAULT_FRAME_STYLE |
            wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW ^ wx.RESIZE_BORDER)
        panel = wx.Panel(self, -1)
        self.parent = parent

        # sz: 1 2 3 5 10

        # sizer10 - repeat sound at the end of countdown
        sizer10 = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, -1, "Repeat sound at the end of countdown:")
        self.repeatSound = wx.SpinCtrl(panel, -1, "Repeat sound at the end of countdown:", (30, 20), (80, -1))
        self.repeatSound.SetRange(1,100)
        self.repeatSound.SetValue(data["repeatSound"])
        sizer10.Add(lbl, 0, wx.ALL)
        sizer10.Add((5,10), 0, wx.ALL)
        sizer10.Add(self.repeatSound, 0, wx.ALL)

        # int. speaker sizer
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.speaker = wx.RadioButton(panel, -1, "Internal Speaker",
                style=wx.RB_GROUP)
        self.spkrFreq = wx.TextCtrl(panel, -1, str(data["spkr_freq"]))
        buttonT = wx.Button(panel, 303, label="Test", size=(55,23))
        wx.EVT_BUTTON(self, 303, self.OnTest)
        st = wx.StaticText(panel, -1, "(frequency from 37 to 32767)")
        sizer1.Add(self.speaker, 0, wx.ALL)
        sizer1.Add((10,10),0, wx.ALL)
        sizer1.Add(self.spkrFreq, 0, wx.ALIGN_CENTER)
        sizer1.Add((10,10),0, wx.ALL)
        sizer1.Add(buttonT, 0, wx.ALIGN_CENTER)
        sizer1.Add((10,10),0, wx.ALL)
        sizer1.Add(st, 0, wx.ALL)

        # sizer 2 - wav sound
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.wavrb = wx.RadioButton(panel, -1, "Sound File")
        self.wav = wx.TextCtrl(panel, -1, data["wavfile"])
        #self.speaker.Enable(True)
        self.wavrb.Enable(True)
        self.wav.Enable(True)
        buttonB = wx.Button(panel, 302, label="Browse..", size=(80,23))
        wx.EVT_BUTTON(self, 302, self.OnBrowse)
        buttonTW = wx.Button(panel, 304, label="Test", size=(55,23))
        wx.EVT_BUTTON(self, 304, self.TestWav)
        sizer2.Add(self.wavrb, 0, wx.ALL)
        sizer2.Add((41,10),0, wx.ALL)
        sizer2.Add(self.wav, 0, wx.ALL)
        sizer2.Add((10,10),0, wx.ALL)
        sizer2.Add(buttonB, 0, wx.ALL)
        sizer2.Add((1,10),0, wx.ALL)
        sizer2.Add(buttonTW, 0, wx.ALL)

        # sizer 5 - mp3 song
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        self.mp3rb = wx.RadioButton(panel, -1, "Mp3 song (loop)")
        self.mp3 = wx.TextCtrl(panel, -1, data["mp3fname"])
        s = data["sound"]
        if s == "speaker":
            self.speaker.SetValue(True)
        elif s == "wav":
            self.wavrb.SetValue(True)
        elif s == "mp3":
            self.mp3rb.SetValue(True)
        buttonB2 = wx.Button(panel, 305, label="Browse..", size=(80,23))
        wx.EVT_BUTTON(self, 305, self.OnBrowseMp3)
        buttonTM = wx.Button(panel, 306, label="Play", size=(55,23))
        buttonTM.mp3fld = self.mp3
        wx.EVT_BUTTON(self, 306, parent.PlayMp3)
        buttonSM = wx.Button(panel, 307, label="Stop", size=(55,23))
        wx.EVT_BUTTON(self, 307, parent.StopMp3)

        sizer5.Add(self.mp3rb, 0, wx.ALL)
        sizer5.Add((13,10),0, wx.ALL)
        sizer5.Add(self.mp3, 0, wx.ALL)
        sizer5.Add((10,10),0, wx.ALL)
        sizer5.Add(buttonB2, 0, wx.ALL)
        sizer5.Add((1,10),0, wx.ALL)
        sizer5.Add(buttonTM, 0, wx.ALL)
        sizer5.Add((1,10),0, wx.ALL)
        sizer5.Add(buttonSM, 0, wx.ALL)

        sizer6 = wx.BoxSizer(wx.HORIZONTAL)

        # sizer 3 - Ok & Cancel
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        buttonOK = wx.Button(panel, 300, label="OK", size=(80,24))
        wx.EVT_BUTTON(self, 300, self.OnOK)
        sizer3.Add(buttonOK, 0, wx.ALIGN_RIGHT)
        buttonC = wx.Button(panel, 301, label="Cancel", size=(80,24))
        wx.EVT_BUTTON(self, 301, self.OnCancel)
        sizer3.Add(buttonC, 0, wx.ALIGN_RIGHT)
        sizer3.Add((10,10),0, wx.ALL)


        box = wx.StaticBox(panel, -1, label = "Alarm sound")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(sizer10, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add((10,5),0, wx.ALL)
        sizer.Add(sizer1, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add((10,5),0, wx.ALL)
        sizer.Add(sizer2,0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add((10,10),0, wx.ALL)
        sizer.Add(sizer5,0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add((10,5),0, wx.ALL)

        st = wx.StaticText(panel, -1, "Microbreak (seconds):")
        self.microbreak = wx.TextCtrl(panel, -1, str(data.break_time))
        box2 = wx.StaticBox(panel, -1, label = "")

        mbsizer = wx.StaticBoxSizer(box2, wx.VERTICAL)
        mbsizer.Add(st, 0, wx.ALIGN_LEFT)
        mbsizer.Add((5,5), 0, wx.ALIGN_LEFT)
        mbsizer.Add(self.microbreak, 0, wx.ALIGN_LEFT)


        outerSizer = wx.BoxSizer(wx.VERTICAL)
        outerSizer.Add(sizer,0, wx.ALL, border=5)
        outerSizer.Add(mbsizer,0, wx.ALL, border=5)
        outerSizer.Add(sizer3,0, wx.ALIGN_RIGHT, border=9)

        panel.SetSizer(outerSizer)
        self.SetDefaultItem(self)
        self.SetFocus()


    def on_test(self, event):
        try:
            freq = int(self.spkrFreq.GetValue())
            if freq < 37 or freq > 32767:
                raise ValueError
        except ValueError:
            print "Error: spkr frequency must be a number from 37 to 32767"
            return
        if is_win:
            winsound.Beep(freq, 200)


    def test_wav(self, event):
        wav = self.wav.GetValue()
        try:
            winsound.PlaySound(wav, winsound.SND_ALIAS)
        except:
            print "Some error trying to play the wav file.."
            pass


    def on_browse(self, event):
        wildcard = "Wav file (*.wav)|*.wav|All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(),
            "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.wav.SetValue(dialog.GetPath())
        dialog.Destroy()


    def on_browse_mp3(self, event):
        wildcard = "Mp3 file (*.mp3)|*.mp3|All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(),
            "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.mp3.SetValue(dialog.GetPath())
        dialog.Destroy()


    def on_oK(self, event):
        a = self.speaker.GetValue()
        b = self.wavrb.GetValue()
        if a:
            data.sound = "speaker"
        elif b:
            data.sound = "wav"
            data.wavfile = self.wav.GetValue()
        else:
            data.sound = "mp3"
            data.mp3fname = self.mp3.GetValue()


        try:
            data.spkr_freq = int(self.spkrFreq.GetValue())
        except ValueError:
            print "Error: spkr frequency must be a number"
            pass

        d = self.repeatSound.GetValue()
        if d:
            data.repeatSound = d

        e = self.microbreak.GetValue()
        if e:
            data.break_time = int(e)

        presets = data.presets
        self.Close(True)

    def on_cancel(self, event):
        self.Close(True)


class ExTimer(wx.Frame):
    def __init__(self, icon=None):
        width          = 1265
        height         = 940
        self.pause     = False
        self.do_skip   = False
        self.do_blink  = False
        self.do_stop   = False
        xdim           = 2
        ydim           = 395
        x              = y = 0
        self.buttons   = []
        times          = data.presets
        self.timer     = self.countdown = None, None
        self.stop_mp3   = False
        self.is_playing = False

        wx.Frame.__init__(self, None, -1, 'Y-Timer', size=(width, height))
        panel = self.panel = wx.Panel(self, -1)


        self.minitext = self.add_text_control('', (xdim, 1), (400, 20), 8)

        self.text = wx.TextCtrl(panel, -1, "0:00", (xdim, 190), (1250, 200))
        font = wx.Font(92, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.text.SetFont(font)
        xdim += 1285

        self.trayicon = ddTaskBarIcon(icon, "Y-Timer", self)
        # Handle the window being `iconized` (err minimized)
        self.Bind(wx.EVT_ICONIZE, self.on_iconify)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.gauge = wx.Gauge(panel, -1, 200, (2, 22), (1250, 165))
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)

        self.etext = wx.TextCtrl(panel, -1, "", (300, ydim), (480, 500), style=wx.TE_MULTILINE)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.etext.SetFont(font)

        xdim = 300 + 480 + 5
        buttonStop = wx.Button(panel, 201, label="stop", pos=(xdim, ydim), size=(60,96))
        wx.EVT_BUTTON(self, 201, self.Stop)

        xdim += 62
        buttonStart = wx.Button(panel, 202, label="start", pos=(xdim, ydim), size=(60,48))
        wx.EVT_BUTTON(self, 202, self.Start)

        bt_ydim = ydim
        ydim += 48
        wx.Button(panel, 206, label="pause", pos=(xdim, ydim), size=(60,24))
        wx.EVT_BUTTON(self, 206, self.OnPause)

        ydim += 24
        wx.Button(panel, 203, label="settings", pos=(xdim, ydim), size=(60,24))
        wx.EVT_BUTTON(self, 203, self.OnSettings)

        ydim += 26
        xdim -= 62
        wx.Button(panel, 207, label="skip", pos=(xdim, ydim), size=(124,24))
        wx.EVT_BUTTON(self, 207, self.OnSkip)

        ydim += 26
        self.elapsed_text = wx.TextCtrl(panel, -1, "0:00", (xdim, ydim), (124, 24))
        font = wx.Font(9, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.elapsed_text.SetFont(font)

        btnsz = 42
        ydim = bt_ydim
        xdim = 1210

        wx.Button(panel, 208, label="+1m", pos=(xdim, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 208, self.add1min)
        wx.Button(panel, 211, label="+1m", pos=(3, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 211, self.add1min)

        ydim += 50
        wx.Button(panel, 209, label="+2m", pos=(xdim, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 209, self.add2min)
        wx.Button(panel, 212, label="+2m", pos=(3, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 212, self.add2min)

        ydim += 50
        wx.Button(panel, 210, label="+3m", pos=(xdim, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 210, self.add3min)
        wx.Button(panel, 213, label="+3m", pos=(3, ydim), size=(btnsz, 50))
        wx.EVT_BUTTON(self, 213, self.add3min)

        self.FocusFrame()


    def add_text_control(self, '', (self, xdim, 1), (self, 400, 20), 8):
        self.minitext = wx.TextCtrl(panel, -1, "", (xdim, 1), (400, 20))
        font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.minitext.SetFont(font)
        return self.minitext

    def play_mp3(self, event):
        """Play an mp3 file."""
        self.stop_mp3   = False
        self.is_playing = True
        self.event      = event
        fname           = event.GetEventObject().mp3fld.GetValue() if event else data.mp3fname
        thread.start_new_thread(self.Mp3Thread, [fname])


    def mp3Thread(self, s_name):
        import pymedia.audio.acodec as acodec
        import pymedia.muxer as muxer
        import pymedia.audio.sound as sound

        dm  = muxer.Demuxer( str.split( str(sName), '.' )[ -1 ].lower() )
        f   = open( sName, 'rb' )
        s   = f.read(8192)
        fr  = dm.parse(s)
        dec = acodec.Decoder(dm.streams[0])
        r   = dec.decode(s)
        snd= sound.Output(r.sample_rate, r.channels, sound.AFMT_S16_LE)
        while len(s) > 0:
            if self.stop_mp3:
                break
            if r: snd.play(r.data)
            s = f.read(512)
            try:
                r = dec.decode(s)
            except:
                break

        while snd.is_playing(): time.sleep(.05)
        self.is_playing = False


    def stop_mp3(self, event=None):
        self.stop_mp3 = True

    def focus_frame(self, event=None):
        self.SetDefaultItem(self)
        self.SetFocus()

    def on_iconify(self, e):
        """Being minimized, hide self, which removes the program from the taskbar."""
        self.Hide()

    def time_to_quit(self, event):
        """Will also trigger OnClose through EVT_CLOSE."""
        self.Close(True)

    def on_close(self, event):
        """Close, clean up."""
        self.trayicon.RemoveIcon()
        data.close()
        self.Destroy()
        sys.exit()

    def on_settings(self, event):
        frame = Settings(self)
        frame.Show()

    def add2min(self, event):
        self.length += 2*60

    def add3min(self, event):
        self.length += 3*60

    def add1min(self, event):
        self.length += 60


    def stop(self, event):
        """Stop both timer and countdown."""
        self.do_stop = True
        if self.timer:
            if not self.timer.IsRunning():
                self.text.SetValue("0:00")
            self.timer.Stop()
        if self.countdown:
            self.countdown.Stop()
        self.gauge.SetValue(0)


    def parse_entries(self):
        text       = self.etext.GetValue()
        lst        = text.split("\n")
        lst        = [x for x in lst if x.strip()]     # take out empty lines
        self.items = []
        timel      = 0

        for line in lst:
            mins, txt = line.split(" ", 1)
            mins      = float(mins)*60
            mins      = int(round(mins))
            timel += mins + data.break_time
            self.items.append((mins, txt))
            self.items.append((data.break_time, "..."))

        timel = timel / 60
        return timel


    def start(self, event):
        """Start simple timer."""

        self.elapsed       = 0
        self.elapsed_total = 0
        self.last_time     = None
        timel              = self.ParseEntries()
        self.countdown     = wx.PyTimer(self.RunCountdown)
        self.do_stop       = False
        self.length, self.item_name = self.items.pop(0)
        self.countdown.Start(200)

        # md = wx.MessageDialog(self, "Total length: %smin" % timel)
        # val = md.ShowModal()
        # if val == wx.ID_OK:


    def run_countdown(self, *event):
        """Run countdown timer."""

        if self.last_time and not self.pause:
            self.elapsed_total += intrnd(time() - self.last_time)
            self.elapsed += intrnd(time() - self.last_time)
        self.last_time = time()

        if self.pause:
            return None

        if self.do_stop:
            self.countdown.Stop()

        if self.do_skip:
            self.length = 1
            self.do_skip = False

        self.elapsed_text.SetValue("%s:%02s" % (d/60, str(d%60).zfill(2)))

        progress = intrnd(self.elapsed/self.length * 200)
        left = intrnd(self.length - self.elapsed)
        self.gauge.SetValue(progress)
        if 21 < left <= 22 and self.item_name != "...":
            if self.do_blink: self.gauge.SetValue(0)
            self.do_blink = not self.do_blink

        self.text.SetValue("%s" % self.item_name)
        self.minitext.SetValue("%s [%s:%s]" % (self.item_name, left//60, str(left%60).zfill(2)) )

        if self.elapsed >= self.length:
            self.countdown.Stop()
            self.do_stop = False
            if data.sound == "mp3":
                if not self.is_playing:
                    self.PlayMp3(None)
            else:
                thread.start_new_thread(self.alarm, ())

            if self.items:
                self.length, self.item_name = self.items.pop(0)
                self.elapsed = 0
                self.countdown.Start()


    def on_skip(self, event):
        self.do_skip = True

    def on_pause(self, event):
        self.pause = not self.pause

    def run_timer(self, *event):
        """Run simple timer, updating time display."""
        if self.do_stop:
            self.timer.Stop()
        a = intrnd(time() - self.start)
        self.text.SetValue( display_time((a/60,a%60)) )


    def on_click(self, event=None, length=None):
        """Start the countdown timer."""
        if self.timer:
            self.timer.Stop()
        if self.countdown:
            self.countdown.Stop()
        self.countdown = wx.PyTimer(self.run_countdown)

        try:
            # get time from preset button
            a = event.EventObject.time
            self.length = a[0]*60 + a[1]
        except:
            try:
                # trying to get time from text entry field..
                self.length = float(event.EventObject.GetValue())*60
                self.length = intrnd(self.length)
            except:
                print "failed to get time, will do nothing.."
                pass

        self.start = time()
        self.do_stop = False
        self.countdown.Start(200)


    def alarm(self):
        """Sound the alarm, needs to be in a separate thread to be possible to stop this."""
        for i in range(data.repeatSound):
            # does not work right now, need to be in a sep. thread
            if self.do_stop:
                break
            # does not work right now, need to be in a sep. thread
            if self.do_stop:
                break

            if is_win:
                if data.sound == "speaker":
                    winsound.Beep(data.spkr_freq, 100)
                else:
                    winsound.PlaySound(data.wavfile, winsound.SND_ALIAS)
            if self.do_stop:
                break
            time.sleep(.2)


def test_display_time():
    lst = [(500,5), (300,0), (68,30), (14,8),]
    for t in lst:
        print DisplayTime(t)


def display_time(timetuple):
    """Return string of time.
    2, 45 => '2:45'
    3, 0 =>  '3:00'"""

    m, s = timetuple
    h, m = m/60, m%60
    if h:
        h = str(h) + ':'
        m = str(int(m)).zfill(2)
    else:
        h = ""
    return "%s%s:%02s" % (h, m, str(int(s)).zfill(2))


def parse_time_entry(text):
    """Time can be either in form 'x' or 'x:x', we need to return (example):
    '2' -> (2,0)
    '2.5' -> (2, 30)
    2:45 -> (2, 45)
    """
    if ':' in text:
        a = text.split(':')
        return [int(b.strip()) for b in a]
    else:
        mins = float(text)
        m, s = int(mins), mins % 1
        return m, s * 100 / 60


def intrnd(val):
    return int(round(value))

class Data:
    def __init__(self, shelve_data):
        if not shelve_data.keys():
            shelve_data.update(defaults)
        self.shelve_data = shelve_data
        self.__dict__.update(shelve_data)

    def __setitem__(self, k, v):
        self.__dict__[k] = v
        self.shelve_data[k] = v

    def __delitem__(self, k):
        del self.__dict__[k]
        del self.shelve_data[k]

    def close(self):
        self.shelve_data.close()

    def __getitem__(self, k)    : return self.__dict__[k]
    def __iter__(self)          : return iter(self.__dict__)
    def __str__(self)           : return str(self.__dict__)
    def __repr__(self)          : return u"Data: <%s>" % repr(self.__dict__)
    def __unicode__(self)       : return unicode(self.__dict__)
    def __nonzero__(self)       : return len(self.__dict__)
    def pop(self, *args)        : return self.__dict__.pop(*args)
    def get(self, *args)        : return self.__dict__.get(*args)
    def update(self, arg)       : return self.__dict__.update(arg)
    def items(self)             : return self.__dict__.items()
    def keys(self)              : return self.__dict__.keys()
    def values(self)            : return self.__dict__.values()
    def dict(self)              : return self.__dict__
    def pp(self)                : pprint(self.__dict__)


if __name__ == "__main__":
    # load_times()
    data  = Data(shelve.open(datafile))
    app   = wx.PySimpleApp()
    icon  = wx.Icon("ytimer.ico", wx.BITMAP_TYPE_ICO)
    frame = ExTimer(icon=icon)
    frame.SetIcon(icon)
    frame.Show()
    app.MainLoop()
