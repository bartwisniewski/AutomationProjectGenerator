import os
import automation as aut

try:
    import tkinter
except ImportError:  # python2
    import Tkinter as tkinter

from tkinter import filedialog
from tkinter import ttk


class Scrolltext(tkinter.Text):

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs, exportselection=False)

        self.scrollbar = ttk.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        # tkinter.Listbox.grid(self, row=row, column=column, sticky=sticky, rowspan=rowspan,
        # **kwargs) # python 2

        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column+columnspan-1, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


class Scrollbox(tkinter.Listbox):

    def __init__(self, window, **kwargs):
        # tkinter.Listbox.__init__(self, window, **kwargs) # Py2
        super().__init__(window, **kwargs, exportselection=False)

        self.scrollbar = ttk.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        # tkinter.Listbox.grid(self, row=row, column=column, sticky=sticky, rowspan=rowspan,
        # **kwargs) # python 2

        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column+columnspan-1, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


class DataListBox(Scrollbox):

    def __init__(self, window, shortcut, app, **kwargs):
        super().__init__(window, **kwargs)
        self.app = app
        self.shortcut = shortcut
        self.bind('<<ListboxSelect>>', self.on_select)

    def populate(self, data):
        self.clear()
        for val in data:
            try:
                self.insert(tkinter.END, val.to_listbox())
            except AttributeError:
                self.insert(tkinter.END, str(val))

    def clear(self):
        self.delete(0, tkinter.END)

    def on_select(self, event):
        index = self.curselection()[0]
        value = (self.get(index),)
        # print("index: {}".format(index))
        # print("index: {}".format(value))
        # sel = self.selection()[0]
        # sel = sel.split('-')
        # sel_type = sel[0]
        # sel_id = None
        # if len(sel) > 1:
        #     sel_id = sel[1]
        # if self.app:
        self.app.display(self.shortcut, index)


class ItemList:
    def __init__(self, master, title, shortcut, data, parent='', parent_short=''):
        self.master = master
        self.title = title
        self.shortcut = shortcut
        self.data = data
        self.parent = parent
        self.parent_short = parent_short
        self.tree = master.tree
        self.to_tree()

    def filtered(self, cond):
        return [d for d in self.data if str(d) == cond]

    def to_tree(self):
        if self.tree:
            parent_id = self.parent_short if self.parent_short else self.parent
            if parent_id:
                if not self.tree.exists(parent_id):
                    self.tree.insert("", "end", parent_id, text=self.parent)
            if not self.tree.exists(self.shortcut):
                self.tree.insert(parent_id, "end", self.shortcut, text=self.title)
            else:
                self.tree.clear_item(self.shortcut)

    def get_list_frame(self, frame):
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        tkinter.Label(frame, text=self.title, bg='grey90').grid(row=0, column=0, sticky='new')
        list_box = DataListBox(frame, self.shortcut, self.master)
        list_box.populate(self.data)
        list_box.grid(row=1, column=0, sticky='nsew', padx=(0, 0))
        list_box.config(border=2, relief='sunken')

    def get_filtered_list_frame(self, frame, cond, title=''):
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        if not title:
            if self.tree:
                title = self.tree.item(self.shortcut+'-'+cond)['text']
            else:
                title = 'filtered'
        tkinter.Label(frame, text=title, bg='grey90').grid(row=0, column=0, sticky='new')
        list_box = DataListBox(frame, self.shortcut, self.master)
        list_box.populate(self.filtered(cond))
        list_box.grid(row=1, column=0, sticky='nsew', padx=(0, 0))
        list_box.config(border=2, relief='sunken')

    def get_details_frame(self, frame, idx):
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame = ttk.Frame(frame)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        item = self.data[int(idx)]
        item_text = Scrolltext(frame)
        item_text.grid(row=0, column=0, sticky='nsew')
        try:
            item_text.insert(tkinter.END, str(item.to_file()))
        except AttributeError:
            item_text.insert(tkinter.END, str(item))


class BlockList(ItemList):
    def __init__(self, master, title, shortcut, data, symbols):
        super(BlockList, self).__init__(master, title, shortcut, data)
        self.symbols = symbols

    def to_tree(self):
        if self.tree:
            super(BlockList, self).to_tree()
            for idx, val in enumerate(self.data):
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut, "end", self.shortcut+'-'+str(idx), text=text)


class StringList(ItemList):
    def to_tree(self):
        if self.tree:
            super(StringList, self).to_tree()
            for idx, val in enumerate(self.data):
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut, "end", self.shortcut+'-'+str(idx), text=text)


class SymbolList(ItemList):
    def __init__(self, master, title, shortcut, data):
        super(SymbolList, self).__init__(master, title, shortcut, data)

    def get_all(self):
        return self.data

    def get_outputs(self):
        return [d for d in self.data if d.is_output()]

    def get_inputs(self):
        return [d for d in self.data if d.is_input()]

    def get_analog_inputs(self):
        return [d for d in self.data if d.is_analog_input()]

    def get_analog_outputs(self):
        return [d for d in self.data if d.is_analog_output()]

    def get_others(self):
        return [d for d in self.data if not(d.is_input() or d.is_output() or d.is_analog_input())]

    def filtered(self, cond):
        if cond == 'aus':
            return self.get_outputs()
        elif cond == 'ein':
            return self.get_inputs()
        elif cond == 'aei':
            return self.get_analog_inputs()
        elif cond == 'oth':
            return self.get_others()
        else:
            return self.data

    def to_tree(self):
        if self.tree:
            super(SymbolList, self).to_tree()
            self.tree.insert(self.shortcut, "end", self.shortcut+"-aus", text="Ausgänge")
            self.tree.insert(self.shortcut, "end", self.shortcut+"-ein", text="Eingänge")
            self.tree.insert(self.shortcut, "end", self.shortcut+"-aei", text="Analog Eingänge")
            self.tree.insert(self.shortcut, "end", self.shortcut+"-oth", text="Sonstige")
            for idx, val in enumerate(self.data):
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                if val.is_output():
                    self.tree.insert(self.shortcut+"-aus", "end", self.shortcut+'-'+str(idx), text=text)
                elif val.is_input():
                    self.tree.insert(self.shortcut+"-ein", "end", self.shortcut+'-'+str(idx), text=text)
                elif val.is_analog_input():
                    self.tree.insert(self.shortcut+"-aei", "end", self.shortcut+'-'+str(idx), text=text)
                else:
                    self.tree.insert(self.shortcut+"-oth", "end", self.shortcut+'-'+str(idx), text=text)

    def get_details_frame(self, frame, idx):
        idx = str(idx)
        if idx.isdigit():
            super(SymbolList, self).get_details_frame(frame, idx)
        else:
            super(SymbolList, self).get_filtered_list_frame(frame, idx)


class ComponentsList(ItemList):

    def get_all(self):
        return self.data

    def filtered(self, cond):
        return [d for d in self.data if d.__class__.__name__ == cond]

    def to_tree(self):
        if self.tree:
            super(ComponentsList, self).to_tree()
            for idx, val in enumerate(self.data):
                if self.shortcut+"-"+val.__class__.__name__ not in self.tree.get_children(self.shortcut):
                    self.tree.insert(self.shortcut, "end", self.shortcut+"-"+val.__class__.__name__, text=val.__class__.__name__)
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut+"-"+val.__class__.__name__, "end", self.shortcut+'-'+str(idx), text=text)

    def get_details_frame(self, frame, idx):
        if idx.isdigit():
            super(ComponentsList, self).get_details_frame(frame, idx)
        else:
            super(ComponentsList, self).get_filtered_list_frame(frame, idx)


class MeasurementsList(ItemList):

    def get_all(self):
        return self.data

    def filtered(self, cond):
        return [d for d in self.data]

    def to_tree(self):
        if self.tree:
            super(MeasurementsList, self).to_tree()
            for idx, val in enumerate(self.data):
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut, "end", self.shortcut+'-'+str(idx), text=text)

    def get_details_frame(self, frame, idx):
        if idx.isdigit():
            super(MeasurementsList, self).get_details_frame(frame, idx)
        else:
            super(MeasurementsList, self).get_filtered_list_frame(frame, idx)


class PIDList(ItemList):

    def get_all(self):
        return self.data

    def filtered(self, cond):
        return [d for d in self.data]

    def to_tree(self):
        if self.tree:
            super(PIDList, self).to_tree()
            for idx, val in enumerate(self.data):
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut, "end", self.shortcut+'-'+str(idx), text=text)

    def get_details_frame(self, frame, idx):
        if idx.isdigit():
            super(PIDList, self).get_details_frame(frame, idx)
        else:
            super(PIDList, self).get_filtered_list_frame(frame, idx)


class AnalogOutputsList(ItemList):

    def get_all(self):
        return self.data

    def filtered(self, cond):
        return [d for d in self.data]

    def to_tree(self):
        if self.tree:
            super(AnalogOutputsList, self).to_tree()

            for idx, val in enumerate(self.data):
                if self.shortcut+"-"+val.__class__.__name__ not in self.tree.get_children(self.shortcut):
                    self.tree.insert(self.shortcut, "end", self.shortcut+"-"+val.__class__.__name__,
                                     text=val.__class__.__name__)
                try:
                    text = val.to_listbox()
                except AttributeError:
                    text = str(val)
                self.tree.insert(self.shortcut+"-"+val.__class__.__name__, "end", self.shortcut+'-'+str(idx), text=text)

    def get_details_frame(self, frame, idx):
        if idx.isdigit():
            super(AnalogOutputsList, self).get_details_frame(frame, idx)
        else:
            super(AnalogOutputsList, self).get_filtered_list_frame(frame, idx)


class CompSetting:
    def __init__(self, master, var, key, on_change=None, frame=None):
        setting = var[key]
        self.cont = tkinter.StringVar(master, value=','.join(setting[0]))
        self.cont.trace('w', self.change)
        self.beg = tkinter.StringVar(master, value=setting[1])
        self.beg.trace('w', self.change)
        self.end = tkinter.StringVar(master, value=setting[2])
        self.end.trace('w', self.change)
        self.setting_var = var
        self.setting_key = key
        self.on_change = on_change
        self.master = master
        self.frame = frame

    def change(self, *args):
        self.setting_var[self.setting_key] = (self.cont.get().replace(' ', '').split(','), self.beg.get(), self.end.get())
        if self.on_change:
            self.on_change()

    def grid(self, row=0, column=0, text='Label', pady=(0, 0)):
        if self.frame:

            ttk.Label(self.frame, text=text).grid(row=row, column=column, sticky='ew', padx=(5, 5), pady=pady)
            ttk.Entry(self.frame, textvariable=self.cont, width=30)\
                .grid(row=row, column=column+1, padx=(0, 5), pady=pady)
            ttk.Entry(self.frame, textvariable=self.beg, width=30)\
                .grid(row=row, column=column+2, padx=(0, 5), pady=pady)
            ttk.Entry(self.frame, textvariable=self.end, width=30)\
                .grid(row=row, column=column+3, padx=(0, 5), pady=pady)


class IntSetting:
    def __init__(self, master, var, key='', on_change=None, frame=None):
        if key:
            setting = var[key]
        else:
            setting = var
        self.setting_var = var
        self.setting_key = key
        self.var = tkinter.StringVar(master, value=setting)
        if self.var.get().isdigit():
            self.val = int(self.var.get())
        else:
            self.val = 0
        self.var.trace('w', self.change)
        self.on_change = on_change
        self.master = master
        self.frame = frame

    def change(self, *args):
        if self.var.get().isdigit():
            self.val = int(self.var.get())
        else:
            self.val = 0

        if self.setting_key:
            self.setting_var[self.setting_key] = self.val
        else:
            self.setting_var = self.var.get()

        if self.on_change:
            self.on_change()

    def grid(self, row=0, column=0, text='Label', pady=(0, 0)):
        if self.frame:
            ttk.Label(self.frame, text=text).grid(row=row, column=column, sticky='ew', padx=(5, 5), pady=pady)
            ttk.Entry(self.frame, textvariable=self.var, width=30) \
                .grid(row=row, column=column+1, padx=(0, 5), pady=pady)


class AppWindow(tkinter.Tk):
    ausg_dbs = [('DB_AUSG_BA', 6998, 'DB Ausgabe Betriebsart', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE'),
                ('DB_AUSG_ENDL_NA', 6993, 'DB Ausgabe Endlage nicht angesteuert', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE'),
                ('DB_AUSG_ENDL_ANG', 6994, 'DB Ausgabe Endlage angesteuert', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE'),
                ('DB_AUSG_STOER', 6995, 'Data Modul Ausgabebits Stoerung', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE'),
                ('DB_AUSG_STOER_QUITT', 6996, 'Data Modul Ausgabebits Stoerung Quittierung', 'AUSGABE', 'Ausgabe',
                 'BOOL', 'FALSE'),
                ('DB_AUSG_STOER_SP', 6997, 'DB Ausgabe Stoerung speichernd', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE'),
                ('DB_AUSGABE', 6999, 'Datenbaustein Ausgabe', 'AUSGABE', 'Ausgabe', 'BOOL', 'FALSE')]

    mes_dbs = [('DB_AI_NORM', 4000, 'DB Normierte Analogeingänge', 'ANALOG', 'INPUT', 'REAL', '0.0')]

    ao_dbs = [('DB_AO_NORM', 5000, 'DB Normierte Analogausgänge', 'ANALOG', 'OUTPUT', 'REAL', '0.0')]

    def __init__(self):
        super(AppWindow, self).__init__()
        self.title('Gögler Projekt Generator')
        self.geometry('1424x768')

        self.inputfile = tkinter.StringVar(self, value='')
        self.outputpath = tkinter.StringVar(self, value=os.path.abspath(os.curdir))
        self.gen_dbs = tkinter.BooleanVar(self, value=True)
        self.gen_visu_fcs = tkinter.BooleanVar(self, value=True)
        self.gen_ctrl_fcs = tkinter.BooleanVar(self, value=True)
        self.gen_meas_fcs = tkinter.BooleanVar(self, value=True)
        self.gen_pid_fcs = tkinter.BooleanVar(self, value=True)
        self.gen_ao_fcs = tkinter.BooleanVar(self, value=True)
        self.gen_idbs = tkinter.BooleanVar(self, value=True)
        self.gen_symbols = tkinter.BooleanVar(self, value=True)
        self.gen_lib_comm = tkinter.BooleanVar(self, value=True)
        self.gen_tia = tkinter.BooleanVar(self, value=True)
        self.gen_tia_al = tkinter.BooleanVar(self, value=True)
        self.gen_tia_ar = tkinter.BooleanVar(self, value=True)
        self.vlv_setting = CompSetting(self, var=aut.SETTINGS, key='vlv', on_change=self.valve_setting_change)
        self.vlv_on_setting = CompSetting(self, var=aut.SETTINGS, key='vlv_on', on_change=self.valve_setting_change)
        self.vlv_off_setting = CompSetting(self, var=aut.SETTINGS, key='vlv_off', on_change=self.valve_setting_change)
        self.vlv_e_su_setting = CompSetting(self, var=aut.SETTINGS, key='vlv_e_su', on_change=self.valve_setting_change)
        self.vlv_e_so_setting = CompSetting(self, var=aut.SETTINGS, key='vlv_e_so', on_change=self.valve_setting_change)
        self.mot_setting = CompSetting(self, var=aut.SETTINGS, key='mot', on_change=self.motor_setting_change)
        self.mot_on_setting = CompSetting(self, var=aut.SETTINGS, key='mot_ra', on_change=self.motor_setting_change)
        self.mot_1r2g_l_setting = CompSetting(self, var=aut.SETTINGS, key='mot1R2G_L',
                                              on_change=self.motor_setting_change)
        self.mot_1r2g_s_setting = CompSetting(self, var=aut.SETTINGS, key='mot1R2G_S',
                                              on_change=self.motor_setting_change)
        self.mot_1r2g_l_ra_setting = CompSetting(self, var=aut.SETTINGS, key='mot1R2G_L_ra',
                                                 on_change=self.motor_setting_change)
        self.mot_1r2g_s_ra_setting = CompSetting(self, var=aut.SETTINGS, key='mot1R2G_S_ra',
                                                 on_change=self.motor_setting_change)
        self.mot_fu_ready_setting = CompSetting(self, var=aut.SETTINGS, key='fu_ready',
                                                on_change=self.motor_setting_change)
        self.mot_fu_run_setting = CompSetting(self, var=aut.SETTINGS, key='fu_run', on_change=self.motor_setting_change)
        self.rel_setting = CompSetting(self, var=aut.SETTINGS, key='rel', on_change=self.relay_setting_change)
        self.ai_setting = CompSetting(self, var=aut.SETTINGS, key='ai', on_change=self.ai_setting_change)
        self.ao_setting = CompSetting(self, var=aut.SETTINGS, key='ao', on_change=self.ao_setting_change)
        self.setpoint_setting = CompSetting(self, var=aut.SETTINGS, key='setpoint', on_change=self.ao_setting_change)
        self.pid_setting = CompSetting(self, var=aut.SETTINGS, key='pid', on_change=self.pid_setting_change)

        self.comp_start_byte = IntSetting(self, var='', on_change=self.comp_setting_change)
        self.comp_end_byte = IntSetting(self, var='', on_change=self.comp_setting_change)
        self.visu_fc_num = IntSetting(self, var=aut.SETTINGS, key='visu_fc_num', on_change=self.vfc_setting_change)
        self.ctrl_fc_num = IntSetting(self, var=aut.SETTINGS, key='ctrl_fc_num', on_change=self.cfc_setting_change)
        self.meas_fc_num = IntSetting(self, var=aut.SETTINGS, key='meas_fc_num', on_change=self.ai_setting_change)
        self.fc_num_ao = IntSetting(self, var=aut.SETTINGS, key='fc_num_ao', on_change=self.ao_setting_change)
        self.fc_num_pid = IntSetting(self, var=aut.SETTINGS, key='fc_num_pid', on_change=self.pid_setting_change)

        self.idb_num = IntSetting(self, var=aut.SETTINGS, key='idb_num', on_change=self.comp_setting_change)
        self.idb_num_ai = IntSetting(self, var=aut.SETTINGS, key='idb_num_ai', on_change=self.ai_setting_change)
        self.idb_num_ao = IntSetting(self, var=aut.SETTINGS, key='idb_num_ao', on_change=self.ao_setting_change)
        self.idb_num_pid = IntSetting(self, var=aut.SETTINGS, key='idb_num_pid', on_change=self.pid_setting_change)
        self.idb_num_pid_ctrl = IntSetting(self, var=aut.SETTINGS, key='idb_num_pid_ctrl',
                                           on_change=self.pid_setting_change)

        self.start_analog = IntSetting(self, var=aut.SETTINGS, key='start_analog', on_change=self.load_all)
        self.start_digital1 = IntSetting(self, var=aut.SETTINGS, key='start_digital1', on_change=self.load_all)
        self.start_digital2 = IntSetting(self, var=aut.SETTINGS, key='start_digital2', on_change=self.load_all)
        self.end_digital2 = IntSetting(self, var=aut.SETTINGS, key='end_digital2', on_change=self.load_all)

        self.data = {}

        # === styling ===
        style = ttk.Style(self)
        style.theme_use("vista")

        # Basic structure of window
        self.columnconfigure(0, weight=1)  # menu
        self.columnconfigure(1, weight=1)  # symbols
        self.columnconfigure(2, weight=1)  # list
        self.rowconfigure(0)

        ttk.Label(self, text='Projekt Inhalt', anchor=tkinter.CENTER) \
            .grid(row=0, column=0, pady=(5, 0))

        self.rowconfigure(1, weight=1)

        self.tree_frame = ttk.Frame(self)
        self.tree_frame.grid(row=1, column=0, sticky='nsew', pady=(20, 20), padx=(20, 0))
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree = ProjectTree(window=self.tree_frame, app=self)
        self.tree.heading('#0', text='Projekt Inhalt')
        self.tree.grid(row=0, column=0, sticky='nswe', padx=(5, 0))

        self.list_frame = None
        self.detail_frame = None

        self.display('home')

    def init_list_frame(self):

        ttk.Label(self, text='List', anchor=tkinter.CENTER) \
            .grid(row=0, column=1, pady=(5, 0))

        if self.list_frame:
            self.list_frame.destroy()
        new_frame = ttk.Frame(self)
        new_frame.grid(row=1, column=1, sticky='nsew', pady=(5, 20), padx=(5, 0))
        self.list_frame = new_frame
        return new_frame

    def init_detail_frame(self):

        ttk.Label(self, text='Details', anchor=tkinter.CENTER) \
            .grid(row=0, column=2, pady=(5, 0))

        if self.detail_frame:
            self.detail_frame.destroy()
        new_frame = ttk.Frame(self)
        new_frame.grid(row=1, column=2, sticky='nsew', pady=(5, 20), padx=(5, 20))
        self.detail_frame = new_frame
        return new_frame

    def display(self, item_type, idx=None):
        disp_function = {'home': self.show_home, 'gen': self.show_generate}
        if item_type in self.data:
            if idx:
                idx = str(idx)
                if idx.isdigit():
                    frame = self.init_detail_frame()
                else:
                    frame = self.init_list_frame()
                self.data[item_type].get_details_frame(frame, idx)
            else:
                frame = self.init_list_frame()
                self.data[item_type].get_list_frame(frame)
        else:
            try:
                disp_function[item_type](idx)
            except KeyError:
                print("Nothing to display for this item")

    def show_home(self, idx=None):
        frame = self.init_detail_frame()
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=0)
        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, sticky='nsew')
        file_frame = ttk.Frame(top_frame)
        file_frame.pack(fill="none", expand=True)
        button = OpenFileButton(file_frame, target_var=self.inputfile, title='Symbole laden', on_load=self.load_symbols)
        button.pack(side=tkinter.LEFT)
        tkinter.Entry(file_frame, textvariable=self.inputfile, width=50).pack(side=tkinter.LEFT, padx=(20, 0))

        bottom_frame = tkinter.Frame(frame, relief='sunken', bd=1)
        bottom_frame.grid(row=1, column=0, sticky='new', pady=(20, 0))
        ttk.Label(bottom_frame, text='Objekte:', anchor=tkinter.CENTER)\
            .grid(row=0, column=0, columnspan=4, pady=(5, 0))
        ttk.Label(bottom_frame, text='...ABC...', anchor=tkinter.CENTER).grid(row=1, column=1, sticky='ew', pady=(5, 0))
        ttk.Label(bottom_frame, text='ABC...', anchor=tkinter.CENTER).grid(row=1, column=2, sticky='ew', pady=(5, 0))
        ttk.Label(bottom_frame, text='...ABC', anchor=tkinter.CENTER).grid(row=1, column=3, sticky='ew', pady=(5, 0))

        self.vlv_setting.frame = bottom_frame
        self.vlv_setting.grid(text='Ventil', row=2, column=0, pady=(5, 0))
        self.vlv_on_setting.frame = bottom_frame
        self.vlv_on_setting.grid(text='Ventil RA', row=3, column=0, pady=(5, 0))
        self.vlv_off_setting.frame = bottom_frame
        self.vlv_off_setting.grid(text='Ventil RN', row=4, column=0, pady=(5, 0))
        self.vlv_e_su_setting.frame = bottom_frame
        self.vlv_e_su_setting.grid(text='VentilE SU', row=5, column=0, pady=(5, 0))
        self.vlv_e_so_setting.frame = bottom_frame
        self.vlv_e_so_setting.grid(text='VentilE SO', row=6, column=0, pady=(5, 0))
        self.mot_setting.frame = bottom_frame
        self.mot_setting.grid(text='Motor', row=7, column=0, pady=(5, 0))
        self.mot_on_setting.frame = bottom_frame
        self.mot_on_setting.grid(text='Motor RA', row=8, column=0, pady=(5, 0))
        self.mot_1r2g_l_setting.frame = bottom_frame
        self.mot_1r2g_l_setting.grid(text='Motor langsam', row=9, column=0, pady=(5, 0))
        self.mot_1r2g_s_setting.frame = bottom_frame
        self.mot_1r2g_s_setting.grid(text='Motor schnell', row=10, column=0, pady=(5, 0))
        self.mot_1r2g_l_ra_setting.frame = bottom_frame
        self.mot_1r2g_l_ra_setting.grid(text='Motor langsam RA', row=11, column=0, pady=(5, 0))
        self.mot_1r2g_s_ra_setting.frame = bottom_frame
        self.mot_1r2g_s_ra_setting.grid(text='Motor schnell RA', row=12, column=0, pady=(5, 0))
        self.mot_fu_ready_setting.frame = bottom_frame
        self.mot_fu_ready_setting.grid(text='FU bereit', row=13, column=0, pady=(5, 0))
        self.mot_fu_run_setting.frame = bottom_frame
        self.mot_fu_run_setting.grid(text='FU läuft', row=14, column=0, pady=(5, 0))
        self.rel_setting.frame = bottom_frame
        self.rel_setting.grid(text='Schütz', row=15, column=0, pady=(5, 0))
        self.ai_setting.frame = bottom_frame
        self.ai_setting.grid(text='Analog Eingang', row=16, column=0, pady=(5, 0))
        self.pid_setting.frame = bottom_frame
        self.pid_setting.grid(text='Regler', row=17, column=0, pady=(5, 0))
        self.ao_setting.frame = bottom_frame
        self.ao_setting.grid(text='Analog Ausgang', row=18, column=0, pady=(5, 0))
        self.setpoint_setting.frame = bottom_frame
        self.setpoint_setting.grid(text='Analog Ausgabe', row=19, column=0, pady=(5, 0))

        einst_row = 1
        einst_col = 4
        ttk.Label(bottom_frame, text='Einstellungen:', anchor=tkinter.CENTER) \
            .grid(row=einst_row, column=einst_col, columnspan=4, pady=(10, 0))
        einst_row += 1
        self.meas_fc_num.frame = bottom_frame
        self.meas_fc_num.grid(text='Analog Eingang FC:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.fc_num_ao.frame = bottom_frame
        self.fc_num_ao.grid(text='Analog Ausgabe FC:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.fc_num_pid.frame = bottom_frame
        self.fc_num_pid.grid(text='Regler FC:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.visu_fc_num.frame = bottom_frame
        self.visu_fc_num.grid(text='Start Obj. FC:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.ctrl_fc_num.frame = bottom_frame
        self.ctrl_fc_num.grid(text='Start Anst. FC:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.idb_num.frame = bottom_frame
        self.idb_num.grid(text='Start Instanz DB:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.idb_num_ai.frame = bottom_frame
        self.idb_num_ai.grid(text='Start Instanz DB AI:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.idb_num_ao.frame = bottom_frame
        self.idb_num_ao.grid(text='Start Instanz DB AO:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.idb_num_pid.frame = bottom_frame
        self.idb_num_pid.grid(text='Start Instanz DB PID:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.idb_num_pid_ctrl.frame = bottom_frame
        self.idb_num_pid_ctrl.grid(text='Start Instanz DB PID CTRL:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.comp_start_byte.frame = bottom_frame
        self.comp_start_byte.grid(text='Objekte von [Byte]:', row=einst_row, column=einst_col, pady=(5, 0))
        einst_row += 1
        self.comp_end_byte.frame = bottom_frame
        self.comp_end_byte.grid(text=' '*16+'bis [Byte]:', row=einst_row, column=einst_col, pady=(5, 5))
        einst_row += 1
        self.start_digital1.frame = bottom_frame
        self.start_digital1.grid(text='Digital Eingänge von [Byte] - Teil 1', row=einst_row, column=einst_col,
                                 pady=(5, 5))
        einst_row += 1
        self.start_analog.frame = bottom_frame
        self.start_analog.grid(text='Analog Eingänge von [Byte]', row=einst_row, column=einst_col, pady=(5, 5))
        einst_row += 1
        self.start_digital2.frame = bottom_frame
        self.start_digital2.grid(text='Digital Eingänge von [Byte] - Teil 2', row=einst_row, column=einst_col,
                                 pady=(5, 5))
        einst_row += 1
        self.end_digital2.frame = bottom_frame
        self.end_digital2.grid(text='Digital Eingänge bis [Byte] - Teil 2', row=einst_row, column=einst_col,
                               pady=(5, 0))

    def show_generate(self, idx=None):
        frame = self.init_detail_frame()
        frame.columnconfigure(0, weight=0)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)

        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, sticky='nsew')
        file_frame = tkinter.Frame(top_frame)
        file_frame.pack(fill="none", expand=True)
        settings_frame = tkinter.Frame(frame, bd=1, relief='sunken')
        settings_frame.grid(row=1, column=0, sticky='new', pady=(20, 0))

        frame = file_frame
        SelectFolderButton(frame, target_var=self.outputpath, title='Output dir').pack(side=tkinter.LEFT)
        tkinter.Entry(frame, textvariable=self.outputpath, width=30).pack(side=tkinter.LEFT, padx=(20, 0))
        ttk.Button(frame, text='Generieren', command=self.make_output).pack(side=tkinter.LEFT, padx=(20, 0))

        frame = settings_frame
        tkinter.Checkbutton(frame, text="DB", variable=self.gen_dbs).grid(row=0, column=0, sticky='w', pady=(5, 0))
        tkinter.Checkbutton(frame, text="Visualisierung FC", variable=self.gen_visu_fcs)\
            .grid(row=1, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Ansteuerung FC", variable=self.gen_ctrl_fcs)\
            .grid(row=2, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Analog Eingabe FC", variable=self.gen_meas_fcs) \
            .grid(row=3, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Regler FC", variable=self.gen_pid_fcs) \
            .grid(row=4, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Analog Ausgabe FC", variable=self.gen_ao_fcs) \
            .grid(row=5, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Instanz DBs", variable=self.gen_idbs).grid(row=6, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Symbole", variable=self.gen_symbols).grid(row=7, column=0, sticky='w')
        tkinter.Checkbutton(frame, text="Text Bibliotheken", variable=self.gen_lib_comm)\
            .grid(row=8, column=0, sticky='w')

    def load_symbols(self):
        file_name = self.inputfile.get()
        file_type = file_name.split('.')[-1]
        if file_type == 'txt':
            symbols = aut.txt_get_symbols(file_name)
        elif file_type == 'xlsx':
            symbols = aut.xls_get_symbols(file_name)
        else:
            symbols = []

        sym_list = SymbolList(master=self, title='Symbole', shortcut='sym', data=symbols)
        self.data['sym'] = sym_list
        print("symbols loaded")
        self.display('sym', 'aus')
        self.load_all()

    def load_all(self):
        self.load_measurements()
        self.load_pids()
        self.load_analog_outputs()
        self.load_components()
        self.load_idbs()
        self.load_meas_fcs()
        self.load_pid_fcs()
        self.load_ao_fcs()
        self.load_visu_fcs()
        self.load_ctrl_fcs()
        self.load_tiavariables()
        self.load_tiaalarms()
        self.load_tiaarchives()
        self.load_dbs()
        self.load_libs()

    def load_dbs(self):
        components = self.data['com'].get_all() if 'com' in self.data.keys() else None
        measurements = self.data['mes'].get_all() if 'mes' in self.data.keys() else None
        analog_outputs = self.data['ao'].get_all() if 'ao' in self.data.keys() else None
        data, symbols = [], []
        if components:
            tmp_data, tmp_symbols = aut.dbs_from_objects(self.ausg_dbs, do=components)
            data = data + tmp_data
            symbols = symbols + tmp_symbols

        if measurements:
            tmp_data, tmp_symbols = aut.dbs_from_objects(self.mes_dbs, ai=measurements)
            data = data + tmp_data
            symbols = symbols + tmp_symbols
        if analog_outputs:
            tmp_data, tmp_symbols = aut.dbs_from_objects(self.ao_dbs, ao=analog_outputs)
            data = data + tmp_data
            symbols = symbols + tmp_symbols

        dbs = BlockList(master=self, title='Datenbausteine', shortcut='db', data=data, symbols=symbols)
        self.data['db'] = dbs
        self.load_new_symbols()

    def load_measurements(self):
        if 'sym' in self.data:
            symbols = self.data['sym'].get_all()
            data = aut.measurements_from_symbols(symbols)
            measurements = MeasurementsList(master=self, title='Messungen', shortcut='mes', data=data)
            self.data[measurements.shortcut] = measurements

    def load_pids(self):
        if 'mes' in self.data:
            measurements = self.data['mes'].get_all()
            data = aut.pid_from_measurements(measurements)
            pids = PIDList(master=self, title='Regler', shortcut='reg', data=data)
            self.data[pids.shortcut] = pids

    def load_analog_outputs(self):
        if 'sym' in self.data:
            symbols = self.data['sym'].get_all()
            data = aut.analog_outputs_from_symbols(symbols)
            analog_outputs = AnalogOutputsList(master=self, title='Ausgabe', shortcut='ao', data=data)
            self.data[analog_outputs.shortcut] = analog_outputs

    def load_components(self):
        if 'sym' in self.data:
            symbols = self.data['sym'].get_all()
            outputs = self.data['sym'].get_outputs()
            comp_range = range(self.comp_start_byte.val, self.comp_end_byte.val)
            if self.comp_start_byte.val and not self.comp_end_byte.val:
                max_byte = max([o.address.byte for o in outputs])
                comp_range = range(self.comp_start_byte.val, max_byte)
            data = aut.components_from_symbols(symbols, byte_range=comp_range)
            components = ComponentsList(master=self, title='Objekte', shortcut='com', data=data)
            self.data[components.shortcut] = components

    def load_idbs(self):
        source_data = []
        if 'com' in self.data.keys():
            source_data += self.data['com'].data

        if 'mes' in self.data.keys():
            source_data += self.data['mes'].data

        if 'reg' in self.data.keys():
            source_data += self.data['reg'].data

        if 'ao' in self.data.keys():
            source_data += self.data['ao'].data

        if source_data:
            data, symbols = aut.idbs_from_objects(source_data)
            block_list = BlockList(master=self, title='Instanz DBs', shortcut='idb', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_visu_fcs(self):
        if 'com' in self.data.keys():
            data, symbols = aut.visu_fcs_from_components(self.data['com'].data)
            block_list = BlockList(master=self, title='Komponent FC', shortcut='vfc', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_ctrl_fcs(self):
        if 'com' in self.data.keys():
            data, symbols = aut.ctrl_fcs_from_components(self.data['com'].data)
            block_list = BlockList(master=self, title='Ansteuerung FC', shortcut='cfc', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_tiavariables(self):
        if 'com' in self.data.keys():
            data1, symbols1 = aut.tiavariables_from_objects(self.data['com'].data)
            data2, symbols2 = aut.tiavariables_from_objects(self.data['mes'].data)
            data3, symbols3 = aut.tiavariables_from_objects(self.data['ao'].data)
            data4, symbols4 = aut.tiavariables_from_objects(self.data['reg'].data)
            data = data1 + data2 + data3 + data4
            symbols = symbols1 + symbols2 + symbols3 + symbols4
            block_list = BlockList(master=self, title='TIA Variablen', shortcut='tia', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_tiaalarms(self):
        if 'com' in self.data.keys():
            data1, symbols1 = aut.tiaalarms_from_objects(self.data['com'].data)
            data2, symbols2 = aut.tiaalarms_from_objects(self.data['mes'].data)
            data3, symbols3 = aut.tiaalarms_from_objects(self.data['ao'].data)
            data4, symbols4 = aut.tiaalarms_from_objects(self.data['reg'].data)
            data = data1 + data2 + data3 + data4
            symbols = symbols1 + symbols2 + symbols3 + symbols4
            block_list = BlockList(master=self, title='TIA Alarme', shortcut='tia_al', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_tiaarchives(self):
        if 'mes' in self.data.keys():
            data2, symbols2 = aut.tiaarchive_from_objects(self.data['mes'].data)
            data3, symbols3 = aut.tiaarchive_from_objects(self.data['ao'].data)
            data4, symbols4 = aut.tiaarchive_from_objects(self.data['reg'].data)
            data = data2 + data3 + data4
            symbols = symbols2 + symbols3 + symbols4
            block_list = BlockList(master=self, title='TIA Archive', shortcut='tia_ar', data=data,
                                   symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_meas_fcs(self):
        if 'mes' in self.data.keys():
            data, symbols = aut.meas_fcs_from_measurements(self.data['mes'].data)
            block_list = BlockList(master=self, title='Eingabe FC', shortcut='mfc', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_pid_fcs(self):
        if 'reg' in self.data.keys():
            data, symbols = aut.fcs_from_pid_list(self.data['reg'].data)
            block_list = BlockList(master=self, title='Regler FC', shortcut='rfc', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_ao_fcs(self):
        if 'ao' in self.data.keys():
            data, symbols = aut.ao_fcs_from_ao(self.data['ao'].data)
            block_list = BlockList(master=self, title='Ausgabe FC', shortcut='afc', data=data, symbols=symbols)
            self.data[block_list.shortcut] = block_list
            self.load_new_symbols()

    def load_libs(self):
        if 'sym' in self.data.keys():
            symbols = self.data['sym'].get_all()
            controllers = self.data['reg'].get_all()

            lib_add_do, lib_comm_do, lib_add_ai, lib_comm_ai, lib_add_ao, lib_comm_ao = aut.lib_from_symbols(symbols)
            lib_add_reg, lib_comm_reg = aut.lib_from_controllers(controllers)

            string_list = StringList(master=self, title='Kommentare DO', shortcut='clibdo', data=lib_comm_do,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Addressen DO', shortcut='alibdo', data=lib_add_do,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Kommentare AI', shortcut='clibai', data=lib_comm_ai,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Addressen AI', shortcut='alibai', data=lib_add_ai,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Kommentare AO', shortcut='clibao', data=lib_comm_ao,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Addressen AO', shortcut='alibao', data=lib_add_ao,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Kommentare Regler', shortcut='clibreg', data=lib_comm_reg,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list
            string_list = StringList(master=self, title='Addressen Regler', shortcut='alibreg', data=lib_add_reg,
                                     parent='Bibliotheken', parent_short='libs')
            self.data[string_list.shortcut] = string_list

    def load_new_symbols(self):
        new_symbols = []
        for d in self.data:
            try:
                new_symbols += self.data[d].symbols
            except AttributeError:
                pass
        sym_list = SymbolList(master=self, title='Neue Symbole', shortcut='nsym', data=new_symbols)
        self.data[sym_list.shortcut] = sym_list

    def valve_setting_change(self):
        self.comp_setting_change()
        self.display('com', 'Valve')

    def motor_setting_change(self):
        self.comp_setting_change()
        self.display('com', 'Motor')

    def relay_setting_change(self):
        self.comp_setting_change()
        self.display('com', 'Relay')

    def ai_setting_change(self):
        self.load_measurements()
        self.load_pids()
        self.load_meas_fcs()
        self.load_pid_fcs()
        self.display('mfc')

    def ao_setting_change(self):
        self.load_analog_outputs()
        self.load_ao_fcs()
        self.display('ao')

    def pid_setting_change(self):
        self.load_pids()
        self.load_pid_fcs()
        self.display('reg')

    def vfc_setting_change(self):
        self.load_visu_fcs()
        self.display('vfc')

    def cfc_setting_change(self):
        self.load_ctrl_fcs()
        self.load_tiavariables()
        self.load_tiaalarms()
        self.load_tiarchives()
        self.display('cfc')

    def idb_setting_change(self):
        self.load_idbs()
        self.display('idb')

    def comp_setting_change(self):
        self.load_components()
        self.load_visu_fcs()
        self.load_ctrl_fcs()
        self.load_tiavariables()
        self.load_tiaalarms()
        self.load_tiarchives()
        self.display('com')

    def make_output(self):
        path = self.outputpath.get()
        try:
            if self.gen_dbs.get():
                for db in self.data['db'].data:
                    with open("{}/{}.awl".format(path, db.symbol), "w") as objFile:
                        print(db, file=objFile)

            if self.gen_visu_fcs.get():
                for fc in self.data['vfc'].data:
                    with open("{}/{}.awl".format(path, fc.symbol), "w") as objFile:
                        print(fc, file=objFile)

            if self.gen_ctrl_fcs.get():
                for fc in self.data['cfc'].data:
                    with open("{}/{}.awl".format(path, fc.symbol), "w") as objFile:
                        print(fc, file=objFile)

            if self.gen_meas_fcs.get():
                for fc in self.data['mfc'].data:
                    with open("{}/{}.awl".format(path, fc.symbol), "w") as objFile:
                        print(fc, file=objFile)

            if self.gen_pid_fcs.get():
                for fc in self.data['rfc'].data:
                    with open("{}/{}.awl".format(path, fc.symbol), "w") as objFile:
                        print(fc, file=objFile)

            if self.gen_ao_fcs.get():
                for fc in self.data['afc'].data:
                    with open("{}/{}.awl".format(path, fc.symbol), "w") as objFile:
                        print(fc, file=objFile)

            if self.gen_idbs.get():
                if self.data['idb'].data:
                    with open("{}/idbs.awl".format(path), "w") as objFile:
                        for idb in self.data['idb'].data:
                            print(idb, file=objFile)

            if self.gen_symbols.get():
                if self.data['nsym'].data:
                    with open("{}/new_symbols.txt".format(path), "w") as objFile:
                        for s in self.data['nsym'].data:
                            print(s.to_file(), file=objFile)

            if self.gen_lib_comm.get():
                if self.data['clibdo'].data:
                    with open("{}/lib_comments_do.txt".format(path), "w") as objFile:
                        for l in self.data['clibdo'].data:
                            print(l, file=objFile)
                if self.data['alibdo'].data:
                    with open("{}/lib_add_do.txt".format(path), "w") as objFile:
                        for l in self.data['alibdo'].data:
                            print(l, file=objFile)
                if self.data['clibai'].data:
                    with open("{}/lib_comments_ai.txt".format(path), "w") as objFile:
                        for l in self.data['clibai'].data:
                            print(l, file=objFile)
                if self.data['alibai'].data:
                    with open("{}/lib_add_ai.txt".format(path), "w") as objFile:
                        for l in self.data['alibai'].data:
                            print(l, file=objFile)
                if self.data['clibao'].data:
                    with open("{}/lib_comments_ao.txt".format(path), "w") as objFile:
                        for l in self.data['clibao'].data:
                            print(l, file=objFile)
                if self.data['alibao'].data:
                    with open("{}/lib_add_ao.txt".format(path), "w") as objFile:
                        for l in self.data['alibao'].data:
                            print(l, file=objFile)
                if self.data['clibreg'].data:
                    with open("{}/lib_comments_reg.txt".format(path), "w") as objFile:
                        for l in self.data['clibreg'].data:
                            print(l, file=objFile)
                if self.data['alibreg'].data:
                    with open("{}/lib_add_reg.txt".format(path), "w") as objFile:
                        for l in self.data['alibreg'].data:
                            print(l, file=objFile)
            if self.gen_tia.get():
                with open("{}/tia.txt".format(path), "w") as objFile:
                    print("""Name	Path	Connection	PLC tag	DataType	HMI DataType	Length	Coding	Access Method	Address	Start value	Quality Code	Persistency	Substitute value	Tag value [de-DE]	Update Mode	Comment [de-DE]	Raw data mode	R_ID	Limit Upper 2 Type	Limit Upper 2	Limit Lower 2 Type	Limit Lower 2	Linear scaling	End value PLC	Start value PLC	End value HMI	Start value HMI	Synchronization""",
                          file=objFile)
                    for entry in self.data['tia'].data:
                        print(entry, file=objFile)

            if self.gen_tia_al.get():
                with open("{}/tia_al.txt".format(path), "w") as objFile:
                    print("""Name	Alarm text [de-DE], Alarm text 1	FieldInfo [Alarm text 1]	Class	Trigger tag	Trigger bit	Trigger mode	Acknowledgement tag	Acknowledgement bit	Status tag	Status bit	Group	Priority	Single acknowledgement	Info text [de-DE], Info text	Additional text 1 [de-DE], Alarm text 2	FieldInfo [Alarm text 2]	Additional text 2 [de-DE], Alarm text 3	FieldInfo [Alarm text 3]	Additional text 3 [de-DE], Alarm text 4	FieldInfo [Alarm text 4]	Additional text 4 [de-DE], Alarm text 5	FieldInfo [Alarm text 5]	Additional text 5 [de-DE], Alarm text 6	FieldInfo [Alarm text 6]	Additional text 6 [de-DE], Alarm text 7	FieldInfo [Alarm text 7]	Additional text 7 [de-DE], Alarm text 8	FieldInfo [Alarm text 8]	Additional text 8 [de-DE], Alarm text 9	FieldInfo [Alarm text 9]	Additional text 9 [de-DE], Alarm text 10	FieldInfo [Alarm text 10]	Alarm parameter 1	Alarm parameter 2	Alarm parameter 3	Alarm parameter 4	Alarm parameter 5	Alarm parameter 6	Alarm parameter 7	Alarm parameter 8	Alarm parameter 9	Alarm parameter 10	Alarm annunciation	Display suppression mask	PLC number	CPU number""",
                          file=objFile)
                    for entry in self.data['tia_al'].data:
                        print(entry, file=objFile)

            if self.gen_tia_ar.get():
                with open("{}/tia_ar.txt".format(path), "w") as objFile:
                    for entry in self.data['tia_ar'].data:
                        print(entry, file=objFile)

        except KeyError:
            pass
        os.startfile(path)


class ProjectTree(ttk.Treeview):

    def __init__(self, window, app, **kwargs):
        super().__init__(window, selectmode="browse", **kwargs)
        self.home = self.insert("", 0, "home", text="Start")
        self.generate = self.insert("", "end", "gen", text="Generieren")
        self.components = None
        self.app = app
        self.bind('<<TreeviewSelect>>', self.on_click)
        self.scrollbar = ttk.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)
        if app:
            app.tree = self

    def see_component(self, class_name):
        if self.exists("com-"+class_name):
            ch = self.get_children("com-"+class_name)
            if ch:
                self.see(ch[0])

    def on_click(self, event):
        sel = self.selection()[0]
        sel = sel.split('-')
        sel_type = sel[0]
        sel_id = None
        if len(sel) > 1:
            sel_id = sel[1]
        if self.app:
            self.app.display(sel_type, sel_id)

    def clear_item(self, item):
        if self.get_children(item):
            for ch in self.get_children(item):
                self.delete(ch)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column+columnspan-1, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


class OpenFileButton(ttk.Button):
    def __init__(self, master, target_var, title='Select file', on_load=None):
        self.target_var = target_var
        self.on_load = on_load
        self.title = title
        super(OpenFileButton, self).__init__(master, text=self.title, command=self.open_file)

    def open_file(self):
        file_name = filedialog.askopenfilename(initialdir=os.path.abspath(os.curdir), title=self.title,
                                               filetypes=(("xlsx", "*.xlsx",), ("txt", "*.txt"), ("all files", "*.*")))
        if file_name:
            self.target_var.set(file_name)
            if self.on_load:
                self.on_load()


class SelectFolderButton(ttk.Button):
    def __init__(self, master, target_var, title='Select directory', on_load=None):
        self.target_var = target_var
        self.on_load = on_load
        self.title = title
        super(SelectFolderButton, self).__init__(master, text=self.title, command=self.select_folder)

    def select_folder(self):
        dir_name = filedialog.askdirectory(initialdir=os.path.abspath(os.curdir), title=self.title)
        if dir_name:
            self.target_var.set(dir_name)


if __name__ == '__main__':
    print('Working ..')

    # ==== create app object ====
    mainWindow = AppWindow()

    # ==== init ====
    # mainWindow.inputfile.set("C:/Projects/GoeglerGen/exchange/Symbols.xlsx")
    # mainWindow.load_symbols()

    # ==== run ====
    mainWindow.mainloop()

