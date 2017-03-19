# encoding:utf-8
#
# Download videos from the Dutch `Uitzending gemist' site.
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2017 Martin Tournoij <martin@arp242.net>
# See below for full copyright
#

from __future__ import print_function
import os
import re
import sys
import time
import traceback

# Play some import games to make it work with Python 2 & 3
if sys.version_info[0] > 2:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import queue

    try:
        import _thread as thread
    except ImportError:
        import _dummy_thread as thread
else:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import Queue as queue

    try:
        import thread
    except ImportError:
        import dummy_thread as thread

import download_npo


class GUI:
    def __init__(self, root, argv_videos=None):
        self.root = root
        self.queue = queue.Queue()
        self._videos = []
        self.urls = []

        # Styling
        paths = [os.path.dirname(os.path.realpath(__file__)),
                 '/usr/share/download-npo', '/usr/local/share/download-npo']
        for p in paths:
            p = '{}/icon.gif'.format(p)
            if os.path.exists(p):
                self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file=p))
                break
        self.root.title('download-npo %s, %s' % download_npo.version())

        s = ttk.Style()
        s.theme_use('clam')
        s.configure('Small.TButton', padding=[5, 1], width=0)

        # Keybinds
        root.bind('<Control-q>', lambda a: self.root.quit())

        # +- root ----------------------------------------------------+
        # | +- paned -----------------------------------------------+ |
        # | | +- options_frame ----------+ | +- progress_frame ---+ | |
        # | | |                          | | |                   ^| | |
        # | | | [..]                     | | | (o) title_1 100%  || | |
        # | | |                          | | | (o) title_2 50%   || | |
        # | | |                          | / | (o) title_2 queue || | |
        # | | |                          | / |                   || | |
        # | | |                          | | |                   || | |
        # | | |                          | | |                   || | |
        # | | |     [Voeg toe aan lijst] | | |                   v| | |
        # | | +--------------------------+ | +--------------------+ | |
        # | +-------------------------------------------------------+ |
        # |                                                           |
        # | +- buttons_frame ---------------------------------------+ |
        # | | [Quit] [Sla config op]                        [Start] | |
        # | +-------------------------------------------------------+ |
        # +-----------------------------------------------------------+
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(orient=tk.HORIZONTAL)

        options_frame = ttk.Frame(paned, padding=5, borderwidth=5, relief=tk.RAISED)
        self.progress_frame = ttk.Frame(paned, padding=5, borderwidth=5, relief=tk.RAISED)

        paned.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        buttons_frame = ttk.Frame(self.root, padding=5, borderwidth=5, relief=tk.RAISED)

        options_frame.columnconfigure(0, weight=1)
        options_frame.rowconfigure(1, weight=1)

        options_frame.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky=tk.E + tk.W)
        self.progress_frame.grid(row=0, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        paned.add(options_frame)
        paned.add(self.progress_frame)

        # progress_frame
        ttk.Label(self.progress_frame, text='Voeg een video toe om te beginnen'
                  ).grid(row=0, column=0, sticky=tk.N)

        # options_frame
        self.row = -1

        def row(inc=True):
            if inc:
                self.row += 1
            return self.row

        def label(text, add_space=True):
            if add_space:
                ttk.Label(options_frame, text='').grid(row=row(), column=0, pady=0)
            ttk.Label(options_frame, text=text).grid(row=row(), column=0, columnspan=3, sticky=tk.W)

        # url_input
        label("URL of ID, meerdere scheiden door spatie of enter", False)
        self.url_input = tk.Text(options_frame, height=3, width=60)
        self.url_input.grid(row=row(), column=0, sticky=tk.W + tk.E + tk.N + tk.S, columnspan=3)
        self.url_input.insert(tk.END, '\n'.join(argv_videos))

        # outdir
        self.outdir = tk.StringVar()
        self.outdir.set(os.path.expanduser('~'))
        outdir_input = tk.Entry(options_frame, textvariable=self.outdir)

        def cmd():
            self.outdir.set(filedialog.askdirectory(
                            initialdir=self.outdir.get(),
                            parent=self.root,
                            title='Selecteer map om bestanden op te slaan'))
        selectdir_btn = tk.Button(options_frame, text='Selecteer', command=cmd)

        label('Map om bestanden op te slaan')
        outdir_input.grid(row=row(), column=0, columnspan=2, sticky=tk.W + tk.E)
        selectdir_btn.grid(row=row(False), column=2, sticky=tk.E)

        # Filename
        self.filename = tk.StringVar()
        self.filename.set('{titel}-{episode_id}')

        ttk.Label(options_frame, text='').grid(row=row(), column=0, pady=0)
        r = row()
        ttk.Label(options_frame, text='Bestandsnaam').grid(row=r, column=0, sticky=tk.W)

        filename_input = ttk.Entry(options_frame, textvariable=self.filename)
        filename_input.grid(row=r, column=1, columnspan=2, sticky=tk.W + tk.E)

        # Quality
        self.quality = tk.IntVar()
        self.quality.set(0)

        r = row()
        ttk.Label(options_frame, text='Kwaliteit').grid(row=r, column=0, columnspan=2, sticky=tk.W)

        quality_frame = ttk.Frame(options_frame)
        quality_frame.grid(row=r, column=1, sticky=tk.W)

        quality1 = ttk.Radiobutton(quality_frame, text='Laag', variable=self.quality, value=2)
        quality2 = ttk.Radiobutton(quality_frame, text='Middel', variable=self.quality, value=1)
        quality3 = ttk.Radiobutton(quality_frame, text='Hoog', variable=self.quality, value=0)

        quality1.grid(row=0, column=1, sticky=tk.W)
        quality2.grid(row=0, column=2, sticky=tk.W)
        quality3.grid(row=0, column=3, sticky=tk.W)

        # Overwrite
        self.overwrite = tk.IntVar()
        overwrite = ttk.Checkbutton(options_frame, var=self.overwrite,
                                    text='Overschrijf al bestaande bestanden')
        overwrite.grid(row=row(), column=0, columnspan=3, sticky=tk.W)

        # Subtitles
        self.subtitles = tk.IntVar()
        subtitles = ttk.Checkbutton(options_frame, var=self.subtitles,
                                    text='Download ook ondertiteling, als deze bestaat')
        subtitles.grid(row=row(), column=0, columnspan=3, sticky=tk.W)

        add_btn = ttk.Button(options_frame, text='Voeg toe aan lijst', command=self.click_add)
        add_btn.grid(row=row(), column=0, columnspan=3, sticky=tk.E)

        # buttons_frame
        buttons_frame.columnconfigure(2, weight=1)

        quit_btn = ttk.Button(buttons_frame, text='Sluiten', command=root.quit)
        quit_btn.grid(row=0, column=0, sticky=tk.W)

        start_btn = ttk.Button(buttons_frame, text='Start alles', command=self.click_start_all)
        start_btn.grid(row=0, column=2, sticky=tk.E)

        self.root.minsize(width=800, height=300)
        self.root.update()

        v = download_npo.check_update()
        if v is not None:
            messagebox.showwarning('download-npo', 'Waarschuwing: De laatste '
                                   'versie is {}, je gebruikt nu versie {}'.format(
                                       v, download_npo.version()[0]))

    def click_add(self):
        v = self.url_input.get(1.0, tk.END).strip()
        print(v)
        self.url_input.delete(1.0, tk.END)

        # Do nothing if no filename or outdir
        if v == '' or self.outdir.get() == '':
            return

        urls = re.split(r'\s+', v)
        for u in urls:
            if u in self.urls:
                for i, v in enumerate(self._videos):
                    if v['url'] == u:
                        del self._videos[i]
                        break
                self.urls.remove(u)
            self.urls.append(u)

        self.get_meta_all()

    def click_start_all(self):
        self.start_download_all()

    def get_video(self, url):
        for v in self._videos:
            if v['url'] == url:
                return v
        return None

    def get_meta_all(self):
        for u in self.urls:
            if self.get_video(u) is None:
                self.append_download_to_queue(u)
        self.run_queue()

    def start_download_all(self):
        for u in self.urls:
            v = self.get_video(u)
            if v['status'] == 0:
                self.start_video(v)
        self.run_queue()

    def start_or_pause_video(self, video):
        if video['start_pause'].get() == 'Pauze':
            self.pause_video(video)
        else:
            self.start_video(video)

    def start_video(self, video):
        self.queue.put(lambda: thread.start_new_thread(self.background_download, (video,)))
        video['start_pause'].set('Pauze')
        if video['status'] == 4:
            video['status'] = 1

    def pause_video(self, video):
        video['status'] = 4
        video['start_pause'].set('Ga verder')

    def cancel_video(self, video):
        video['frame'].grid_forget()
        video['frame'].destroy()

        try:
            self.urls.remove(video['url'])
        except:
            pass
        try:
            self._videos.remove(video)
        except:
            pass

    def make_progress_frame_entry(self, label_text, video):
        # +-------------------------------------------------+
        # | *Titel*                   start/pause] [cancel] |
        # | progress                                        |
        # +-------------------------------------------------+
        video['progress'] = tk.StringVar()
        video['progress'].set('Nog niet gestart')

        frame = ttk.Frame(self.progress_frame, relief=tk.GROOVE, borderwidth=10)
        video['frame'] = frame
        print(video['row'])
        frame.grid(row=video['row'], sticky=tk.W + tk.E + tk.N, column=0)
        # paned.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        title = tk.Label(frame, text=label_text)
        title.grid(row=0, column=0, sticky=tk.W)

        video['start_pause'] = tk.StringVar()
        video['start_pause'].set('Start')
        btn = ttk.Button(frame, textvariable=video['start_pause'], style='Small.TButton',
                         command=lambda: self.start_or_pause_video(video))
        btn.grid(row=0, column=1, sticky=tk.E)

        cancel = ttk.Button(frame, text='Annuleren', style='Small.TButton',
                            command=lambda: self.cancel_video(video))
        cancel.grid(row=0, column=2, sticky=tk.E)

        progress = tk.Label(frame, textvariable=video['progress'])
        progress.grid(row=1, column=0, sticky=tk.W)

    def append_download_to_queue(self, url):
        video = None
        # for v in self._videos:
        #    if v['status'] not in [3, 5] and v['url'] == url:
        #        # TODO: Update opts
        #        video = v

        # if video is None:
        if True:
            video = {
                'url': url,
                'filename': self.filename.get(),
                'outdir': self.outdir.get(),
                'subtitles': self.subtitles.get(),
                'overwrite': self.overwrite.get(),
                'quality': self.quality.get(),

                # 0: not yet started
                # 1: in progress
                # 2: finished
                # 3: error
                # 4: paused
                # 5: cancelled
                'status': 0,
            }
            self._videos.append(video)
        video['row'] = len(self._videos)
        self.queue.put(lambda: thread.start_new_thread(self.fetch_meta, (video,)))

    def fetch_meta(self, video):
        try:
            site = download_npo.match_site(video['url'])
            videourl, player_id, ext = site.find_video(video['url'])
            meta = site.meta(player_id)
            text = download_npo.make_filename(video['outdir'], video['filename'],
                                              'mp4', meta, True, True, True)

            extra_text = ['{} kwaliteit'.format(
                ['hoge', 'middel', 'lage'][video['quality']])]
            if video['subtitles']:
                extra_text.append('ondertitels')
            if video['overwrite']:
                extra_text.append('overschrijven')
            text += ' ({})'.format(', '.join(extra_text))
        except Exception as exc:
            video['status'] = 3
            text = '{} - Fout'.format(video['url'], sys.exc_info()[1])
        self.make_progress_frame_entry(text, video)
        thread.exit()

    # TODO: Voeg optie toe om te beperken tot /n/ processen
    def run_queue(self):
        try:
            while True:
                self.queue.get_nowait()()
        except queue.Empty:
            pass

        self.root.after(100, self.run_queue)

    def background_download(self, video):
        """ Download videos in thread """

        if video['status'] != 0:
            return
        video['status'] = 1

        site = download_npo.match_site(video['url'])

        try:
            videourl, player_id, ext = site.find_video(video['url'], video['quality'])
            outdir = download_npo.make_outdir(video['outdir'], site.meta(player_id))
            outfile = download_npo.make_filename(outdir, video['filename'], ext,
                                                 site.meta(player_id),
                                                 overwrite=video['overwrite'])
            if video['subtitles'] > 0:
                subout = download_npo.make_filename(outdir, video['filename'],
                                                    'srt', site.meta(player_id),
                                                    overwrite=video['overwrite'])
                with open(subout, 'wb') as fp:
                    fp.write(site.subs(player_id).read())
        except download_npo.Error:
            messagebox.showerror('Fout', sys.exc_info()[1])
            self.queue.put(lambda: video['progress'].set('Fout'))
            video['status'] = 3
            thread.exit()

        pcomplete = -1
        starttime = time.time()
        ptime = remaining = 0
        for total, completed, speed in site.download_video(player_id, videourl, outfile):
            # Paused
            if video['status'] == 4:
                self.queue.put(lambda: video['progress'].set('Gepauzeerd'))
                time.sleep(1)
                continue
            # Cancelled
            if video['status'] == 5:
                break
            completepc = int(completed / (total / 100))
            curtime = time.time()

            if completepc != pcomplete:
                # self.queue.put(lambda: video['progress'].set(completepc))
                pcomplete = completepc

            if curtime - starttime > 2:
                speed = int(completed / (curtime - starttime))
                if speed == 0:
                    remaining = 100
                else:
                    remaining = (total - completed) / speed

            if curtime >= ptime + 1:
                if speed == 0:
                    remaining = 100
                else:
                    remaining = (total - completed) / speed

                if total < 0:
                    line = '  {completed} van onbekende groote met {speed:>4}/s'.format(
                        completed=download_npo.human_size(completed),
                        speed=download_npo.human_size(speed))
                else:
                    line = '{complete:>3}% van {total}; nog {remaining:>4} te gaan met {speed:>4}/s'
                    line = line.format(
                        total=download_npo.human_size(total),
                        complete=int(completed / (total / 100)),
                        speed=download_npo.human_size(speed),
                        remaining=download_npo.human_time(remaining))
                self.queue.put(lambda: video['progress'].set(line))
                ptime = curtime

        if video['status'] == 1:
            video['status'] = 2
            self.queue.put(lambda: video['progress'].set('Klaar'))
        thread.exit()


def main():
    root = tk.Tk()
    GUI(root, sys.argv[1:])
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


# The MIT License (MIT)
#
# Copyright © 2012-2017 Martin Tournoij
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# The software is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. In no event shall the
# authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or other dealings
# in the software.
