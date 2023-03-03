import textwrap
import tkinter
import customtkinter
import pandas as pd
import logic
from models.Collection import CmsColl, BankColl
import ctypes
from tkinter import messagebox
from config import PROJECT_DIR
from configparser import ConfigParser
from tkinter import filedialog
from config import DEF_F_EXTENSION
from sys import stdout

app_id = 'dberinger.apps.collectionsgenerator.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(fr"{PROJECT_DIR}\app\assets\custom_theme.json")


class App(customtkinter.CTk):
    WIDTH = 550
    HEIGHT = 450

    def __init__(self):
        super().__init__()

        self.original_src = pd.DataFrame()
        self.working_coll = pd.DataFrame()
        self.src_type = ''
        self.extra_input = ''
        self.settings_f_path = fr'{PROJECT_DIR}\app\settings.ini'
        self.parser = ConfigParser()

        # ******************************* USER INTERFACE *******************************

        self.title("Collections Generator")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.iconbitmap("ikonka.ico")

        # FRAME SETUP

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=100,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=2, sticky="nswe")
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=3, sticky="nswe", padx=20, pady=20)

        # LEFT FRAME

        self.frame_left.columnconfigure(0, weight=1)
        self.frame_left.columnconfigure(1, weight=1)
        self.frame_left.grid_columnconfigure(0, minsize=60)
        self.frame_left.grid_columnconfigure(1, minsize=40)
        self.frame_left.grid_rowconfigure(0, minsize=40)
        self.frame_left.grid_rowconfigure(5, minsize=40)
        self.frame_left.grid_rowconfigure(11, minsize=10)

        self.select_src_btn = customtkinter.CTkButton(master=self.frame_left,
                                                         text="Select source",
                                                         command=self.select_src,
                                                         text_color='#fff')
        self.select_src_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=20)

        self.src_lbl = customtkinter.CTkLabel(master=self.frame_left,
                                                 text="No source file selected.",
                                                 font=("Roboto Medium", -12))  # font name and size in px
        self.src_lbl.grid(row=2, column=0, columnspan=2, pady=(5, 10), padx=10)

        self.extra_input_btn = customtkinter.CTkButton(master=self.frame_left,
                                                       text="+Input",
                                                       width=80,
                                                       border_width=1,  # <- custom border_width
                                                       fg_color=None,
                                                       command=self.extra_input_handler)
        self.extra_input_btn.grid(row=3, column=0, pady=10, padx=(20, 0))

        self.clr_extra_input_btn = customtkinter.CTkButton(master=self.frame_left,
                                                           width=30,
                                                           fg_color=None,
                                                           border_width=1,
                                                           text=u"\U0001F5D1",
                                                           command=self.clear_extra_input)
        self.clr_extra_input_btn.grid(row=3, column=1, padx=(0, 15))

        self.total_lbl = customtkinter.CTkLabel(master=self.frame_left,
                                                text="Total items:",
                                                font=("Roboto Medium", -12))  # font name and size in px
        self.total_lbl.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        self.max_coll_size = customtkinter.CTkEntry(master=self.frame_left,
                                                    width=100,
                                                    placeholder_text="Max size")
        self.max_coll_size.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        self.generate_btn = customtkinter.CTkButton(master=self.frame_left,
                                                    text="Create",
                                                    text_color='#fff')
        self.generate_btn.grid(row=7, column=0, columnspan=2, pady=10, padx=20)

        self.full_file_checkbox_val = customtkinter.IntVar()
        self.full_file_checkbox = customtkinter.CTkCheckBox(master=self.frame_left,
                                                            text="Include full file?",
                                                            variable=self.full_file_checkbox_val,
                                                            border_width=1,  # <- custom border_width
                                                            fg_color=None)
        self.full_file_checkbox.grid(row=8, column=0, columnspan=2, pady=10, padx=20)

        # MIDDLE RIGHT

        # configure grid layout (3x7)
        self.frame_right.columnconfigure((0, 1), weight=2)
        self.frame_right.columnconfigure(2, weight=1)

        # category ids
        self.cat_ids = customtkinter.CTkEntry(master=self.frame_right,
                                              width=100,
                                              placeholder_text="Category IDs")
        self.cat_ids.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=20, sticky="we")

        # clusters
        self.clusters_cmb_box = customtkinter.CTkComboBox(master=self.frame_right, values=[], state="readonly")

        self.clusters_cmb_box.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        # price points
        self.pp_label = customtkinter.CTkLabel(master=self.frame_right,
                                               text="Price Points")
        self.pp_label.grid(row=3, column=0, columnspan=2, sticky="nwe", padx=15, pady=(15, 0))

        self.pp_min = customtkinter.CTkEntry(master=self.frame_right,
                                             width=40,
                                             placeholder_text="Min")
        self.pp_min.grid(row=4, column=0, pady=10, padx=(10, 5), sticky="we")

        self.pp_max = customtkinter.CTkEntry(master=self.frame_right,
                                             width=40,
                                             placeholder_text="Max")
        self.pp_max.grid(row=4, column=1, pady=10, padx=(5, 10), sticky="we")

        # ratio
        self.pp_lbl = customtkinter.CTkLabel(master=self.frame_right, text="Ratio - Local:Offshore")
        self.pp_lbl.grid(row=5, column=0, columnspan=2, sticky="nwe", padx=15, pady=(15, 0))

        self.ratio_local = customtkinter.CTkEntry(master=self.frame_right,
                                                  width=40,
                                                  placeholder_text="Local")
        self.ratio_local.grid(row=6, column=0, pady=10, padx=(10, 5), sticky="we")

        self.ratio_offshore = customtkinter.CTkEntry(master=self.frame_right,
                                                     width=40,
                                                     placeholder_text="Offshore")
        self.ratio_offshore.grid(row=6, column=1, pady=10, padx=(5, 10), sticky="we")

        # sold-outs
        self.sold_out_checkbox_val = customtkinter.IntVar()
        self.sold_out_checkbox = customtkinter.CTkCheckBox(master=self.frame_right,
                                                           width=40,
                                                           text="DEL out of stock?",
                                                           variable=self.sold_out_checkbox_val,
                                                           border_width=1,
                                                           fg_color=None)
        self.sold_out_checkbox.grid(row=7, column=0, columnspan=2, sticky="nwe", padx=15, pady=(15, 0))

        # RIGHT RIGHT

        # sorting
        self.sort_lbl = customtkinter.CTkLabel(master=self.frame_right, text="Sort by:", width=50, )
        self.sort_lbl.grid(column=2, row=0, sticky="nwe", padx=15, pady=10)

        # ado
        self.ado_var = customtkinter.IntVar()
        self.ado_switch = customtkinter.CTkSwitch(master=self.frame_right,
                                                  text="ADO",
                                                  variable=self.ado_var,
                                                  onvalue=1,
                                                  offvalue=0)
        self.ado_switch.grid(row=1, column=2, pady=10, padx=20, sticky="we")

        # rating
        self.rating_var = customtkinter.IntVar()
        self.rating_switch = customtkinter.CTkSwitch(master=self.frame_right,
                                                     text="Rating",
                                                     variable=self.rating_var,
                                                     onvalue=1,
                                                     offvalue=0)
        self.rating_switch.grid(row=2, column=2, pady=10, padx=20, sticky="we")

        # clear options
        self.clear_options_btn = customtkinter.CTkButton(master=self.frame_right,
                                                         width=30,
                                                         fg_color=None,
                                                         border_width=1,
                                                         text="Clear criteria",
                                                         command=self.clear_options)
        self.clear_options_btn.grid(row=4, column=2, pady=0, padx=20)

        # theme options
        self.theme_optionmenu = customtkinter.CTkOptionMenu(master=self.frame_right,
                                                            values=["Light", "Dark", "System"],
                                                            width=70,
                                                            text_color='#fff',
                                                            command=self.set_theme)
        self.theme_optionmenu.grid(row=8, column=2, pady=0, padx=(20, 0))

        self.settings_mapping = {
            'theme': self.theme_optionmenu,
            'rating_switch_on': self.rating_switch,
            'ado_switch_on': self.ado_switch,
            'del_out_of_stock': self.sold_out_checkbox,
            'include_full_file': self.full_file_checkbox
        }

        # ******************************* UI DEFAULTS *******************************

        self.set_theme(self.get_setting('theme'))
        self.clr_extra_input_btn.configure(state=tkinter.DISABLED)
        self.cat_ids.configure(state=tkinter.DISABLED)
        self.clusters_cmb_box.set("Clusters")
        self.clusters_cmb_box.configure(state="readonly")
        self.ratio_local.insert(0, 3)
        self.ratio_offshore.insert(0, 2)
        # set default or last user preferred state for toggles and checkboxes
        for key in self.settings_mapping:
            # but skip theme
            if key == 'theme':
                continue
            if self.get_setting(key) == 'True':
                self.settings_mapping[key].select()

    # ******************************* FUNCTIONS *******************************

    def get_setting(self, key: str, section: str = 'defaults'):
        self.parser.read(self.settings_f_path)
        return self.parser.get(section, key)

    def set_setting(self, new_val, key: str, section: str = 'defaults'):
        self.parser.set(section, key, str(new_val))
        with open(self.settings_f_path, 'w') as settings_f:
            self.parser.write(settings_f)

    def set_theme(self, new_theme):
        self.set_setting(new_theme, 'theme')
        self.theme_optionmenu.set(new_theme)
        customtkinter.set_appearance_mode(new_theme)

    def on_closing(self, event=0):
        self.set_setting(bool(self.full_file_checkbox_val.get()), 'include_full_file')
        self.set_setting(bool(self.sold_out_checkbox_val.get()), 'del_out_of_stock')
        self.set_setting(bool(self.ado_var.get()), 'ado_switch_on')
        self.set_setting(bool(self.rating_var.get()), 'rating_switch_on')
        self.destroy()

    def set_placeholder(self, ui_element, text: str):
        if ui_element._state == 'normal':
            ui_element.configure(placeholder_text=text)
        elif ui_element._state == 'disabled':
            ui_element.configure(state='normal')
            ui_element.configure(placeholder_text=text)
            ui_element.configure(state='disabled')

    def extra_input_handler(self):
        self.extra_input = tkinter.simpledialog.askstring(title="+Input",
                                                          prompt="Paste seller and product ids without headers:")
        if self.extra_input is None:
            self.clear_extra_input()
            return

        self.extra_input = be.process_bd_input(self.extra_input)
        print(self.extra_input[0])
        if len(self.extra_input) != 0:
            self.extra_input_btn.configure(text=f'BD: {len(self.extra_input[0])}')
            self.clr_extra_input_btn.configure(fg_color='red', state=tkinter.NORMAL)

    def clear_extra_input(self):
        self.extra_input = ''
        self.extra_input_btn.configure(text='+Input')
        self.clr_extra_input_btn.configure(fg_color=None, state=tkinter.DISABLED)

    def clear_options(self):
        self.max_coll_size.delete(0, 'end')
        # self.set_placeholder(self.max_coll_size, 'Max size')
        self.cat_ids.delete(0, 'end')
        self.pp_min.delete(0, 'end')
        self.pp_max.delete(0, 'end')
        self.clusters_cmb_box.set('Clusters')
        self.clear_extra_input()
        self.ratio_local.delete(0, 'end')
        self.ratio_offshore.delete(0, 'end')
        self.ratio_local.insert(0, 3)
        self.ratio_offshore.insert(0, 2)

    def get_user_set_coll_size(self):
        try:
            if len(self.max_coll_size.get()) != 0:
                coll_size = int(self.max_coll_size.get())
                if coll_size <= len(self.working_coll):
                    df_size = coll_size
                elif coll_size >= len(self.working_coll):
                    df_size = len(self.working_coll)
                elif coll_size > 20000:
                    df_size = 20000

                print(f'Coll size: {df_size}')
                return df_size
            else:
                return None
        except ValueError:
            messagebox.showerror('Collection size error', 'Please input a natural number, eg 10000.\nGenerating file '
                                                          'without size restrictions...')
            return

    def get_price_point_fields(self):
        price_points = [[], [], []]
        try:
            price_points[0].append(self.pp_min.get())
            price_points[0].append(self.pp_max.get())
        except Exception as e:
            print(e)
            price_points[0] = ['', '']

        if price_points == [['', ''], ['', ''], ['', '']]:
            return None

        for pair in price_points:
            for i, value in enumerate(pair):
                try:
                    pair[i] = float(value)
                except:
                    pair[i] = ''
            if pair != ['', ''] and '' not in pair:
                if pair[0] > pair[1]:
                    pair[0], pair[1] = pair[1], pair[0]
            price_points = [pair for pair in price_points if pair != ['', '']]

        return price_points

    # ******************************* SOURCE *******************************

    def update_src_total(self, num):
        self.total_lbl.configure(text=f'Total products: {num}')

    def toggle_options_for_src_type(self):
        if self.src_type == 'cms':
            self.clusters_cmb_box.configure(state="normal")
            self.clusters_cmb_box.set('N/A')
            self.clusters_cmb_box.configure(state="disabled")
            self.cat_ids.delete(0, 'end')
            self.set_placeholder(self.cat_ids, 'N/A')
            self.cat_ids.configure(state='disabled')
            self.sold_out_checkbox.configure(state='normal')

        if self.src_type == 'bank':
            self.clusters_cmb_box.configure(state="normal")
            self.clusters_cmb_box.set('Clusters')
            self.clusters_cmb_box.configure(state="readonly")
            self.cat_ids.configure(state='normal')
            self.set_placeholder(self.cat_ids, 'Category IDs')
            self.sold_out_checkbox.configure(state='disabled')

    def select_src(self):
        src_file_path = filedialog.askopenfilename(filetypes=DEF_F_EXTENSION, defaultextension=DEF_F_EXTENSION)
        src_type, ori_df = logic.validate_src(src_file_path)

        if src_type == 'cms' or src_type == 'bank':
            self.src_type = src_type
        else:
            messagebox.showerror('Error', src_type)
            self.update_src_total(0)
            self.src_lbl.configure(text='')
            self.original_src = None
            self.working_coll = None
            return

        if self.src_type == 'cms':
            self.original_src = CmsColl(ori_df)
            self.working_coll = CmsColl(ori_df.copy(deep=True))

        elif self.src_type == 'bank':
            self.original_src = BankColl(ori_df)
            self.working_coll = BankColl(ori_df.copy(deep=True))

            clusters = logic.validate_clusters(self.working_coll.get_column_values('cluster'))
            if clusters is not None:
                self.clusters_cmb_box.configure(state="normal")
                self.clusters_cmb_box.configure(values=clusters)
                self.clusters_cmb_box.set('Clusters')
                self.clusters_cmb_box.configure(state="readonly")

        self.toggle_options_for_src_type()

        total_products = len(self.working_coll.get_column_values('product_id'))
        self.update_src_total(total_products)
        src_lbl_text = textwrap.fill(src_file_path.split("/")[-1], width=27)
        self.src_lbl.configure(text=src_lbl_text)
        self.src_lbl.configure(fg_color=("white", "gray38"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
