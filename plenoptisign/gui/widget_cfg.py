#!/usr/bin/env python

__author__ = "Christopher Hahne"
__email__ = "inbox@christopherhahne.de"
__license__ = """
Copyright (c) 2019 Christopher Hahne <inbox@christopherhahne.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

# local python files
from plenoptisign.constants import ABBS, EXPR, RSLT, UNTS, SW, PX, PY, MSG_W, DEC_P, RSYM, ESYM

# 'from', 'to' and 'increment' exponents for 'pp, fs, hh, pm, dA, fU, HH, df, f_num, a, M, G, dx' in that order
SPIN_SET = ((1,-3), (2,-2), (2,-3), (3,-3), (3,-2), (3,-2), (3,-2), (5,2), (3,-1), (2,-1), (2,-1), (2,-1), (2,-1))

# make object for config widget
class CfgWidget(tk.Frame):

    def __init__(self, parent):

        # inheritance
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # declare multiple tk string variables
        tk_params = dict(zip(ABBS, (tk.StringVar() for _ in range(len(ABBS)))))

        # transfer config parameters to tk strings
        for key in ABBS:
            tk_params[key].set(str(self.parent.cfg.params[key]))

        # place scientific notations used throughout the author's publications
        for i, exp in enumerate(ESYM+[' ']+RSYM):
            text = tk.Text(self, width=7, height=2, borderwidth=0, background=self.cget('background'), font=('', 10))
            text.tag_configure('ver_align', offset=-4)
            text.tag_configure('sub', offset=-8)
            if exp.__contains__('_'):
                tags = exp.split('_')
                tags = list(filter(None, sum([tag.split('{') for tag in tags], [])))
                tags = list(filter(None, sum([tag.split('}') for tag in tags], [])))

                if len(tags) == 2:
                    text.insert(tk.INSERT, tags[0], 'ver_align', tags[1], 'sub')
                elif len(tags) == 4:
                    text.insert(tk.INSERT, tags[0], 'ver_align', tags[1], 'sub', tags[2], 'ver_align', tags[3], 'sub')
                text.configure(state=tk.DISABLED)
            else:
                text.insert(tk.INSERT, exp, 'ver_align')
            text.grid(row=i+1, column=0, sticky='S')

        # place entry labels
        for i, exp in enumerate(EXPR):
            label = tk.Label(self, text=exp)
            label.grid(row=i+1, column=1, sticky='W')

        # place entries and keep them as instance variables
        self.entries = []
        for i, (s, key) in enumerate(zip(SPIN_SET, ABBS)):
            if key != 'df' and key != 'f_num' and key != 'M':
                entry = tk.Spinbox(self, from_=-10**s[0], to=10**s[0], increment=10**s[1],
                                   textvariable=tk_params[key], width=SW, command=self.parent.run)
            elif key == 'df':
                # special treatment for focus distance 'df' to cover infinity values
                entry = tk.Entry(self, textvariable=tk_params[key], width=SW)
            elif key == 'f_num':
                # special treatment for f-number 'f_num' to trigger micro image resolution estimation
                entry = tk.Spinbox(self, from_=-10**s[0], to=10**s[0], increment=10**s[1],
                                   textvariable=tk_params[key], width=SW, command=self.update_M)
            elif key == 'M':
                # special treatment for micro image size 'M' to trigger f-number estimation
                entry = tk.Spinbox(self, from_=-10**s[0], to=10**s[0], increment=10**s[1],
                                   textvariable=tk_params[key], width=SW, command=self.update_fnum)
            entry.grid(row=i+1, column=2, sticky='NW', padx=PX)
            self.entries.append(entry)

        # margin separating inputs from outputs
        margin = tk.Label(self)
        margin.grid(row=i+2, column=2)

        # place output labels
        for j, res in enumerate(RSLT):
            label = tk.Label(self, text=res)
            label.grid(row=i+3+j, column=1, sticky='W')

        # place outputs
        self.grid_columnconfigure(index=2, minsize=MSG_W)
        self.msgs = []
        for j in range(len(RSLT)):
            msg = tk.Message(self, text='', width=MSG_W)
            msg.grid(row=i+3+j, column=2, sticky='E')
            self.msgs.append(msg)

        # place units
        for j, unit in enumerate(UNTS):
            label = tk.Label(self, text=unit)
            label.grid(row=j+1, column=3, sticky='W')

    def update_M(self):

        # compute micro image size
        self.parent.obj.compute_mic_img_size()

        # pass estimated micro image size to entry in GUI
        tk_var = tk.StringVar()
        tk_var.set(str(round(self.parent.obj.M, DEC_P)))
        self.entries[10].config(textvariable=tk_var)

        # update results in GUI
        self.parent.run()

        return True

    def update_fnum(self):

        # compute micro image size
        self.parent.obj.compute_pupil_size()

        # pass estimated micro image size to entry in GUI
        tk_var = tk.StringVar()
        tk_var.set(str(round(self.parent.obj.fU/self.parent.obj.D, DEC_P)))
        self.entries[8].config(textvariable=tk_var)

        # update results in GUI
        self.parent.run()

        return True

    def refresh(self):

        # convert results to string with respective metric unit under consideration of infinity
        strings = []
        for res in self.parent.obj.get_results():
            strings.append('%.4f' %round(res, DEC_P) if not "inf" in str(res) else "infinity")

        # update results
        for j, res_str in enumerate(strings):
            self.msgs[j].config(text=res_str)