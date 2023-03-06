# CustomTkinter - MIT License
# Copyright (c) 2023 Tom Schimansky
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
import textwrap
import tkinter
import customtkinter
import pandas as pd
import logic
from models.Collection import CmsColl, BankColl
from models.CmsFileHelper import CmsFileHelper
import ctypes
from tkinter import messagebox, filedialog, simpledialog
from config import PROJECT_DIR
from configparser import ConfigParser
from config import DEF_F_EXTENSION

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
                                                text="Total products:",
                                                font=("Roboto Medium", -12))  # font name and size in px
        self.total_lbl.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        self.max_coll_size = customtkinter.CTkEntry(master=self.frame_left,
                                                    width=100,
                                                    placeholder_text="Max size")
        self.max_coll_size.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        self.generate_btn = customtkinter.CTkButton(master=self.frame_left,
                                                    text="Create",
                                                    command=self.generate_collection,
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

    @staticmethod
    def set_placeholder(ui_element, text: str):
        if ui_element._state == 'normal':
            ui_element.configure(placeholder_text=text)
        elif ui_element._state == 'disabled':
            ui_element.configure(state='normal')
            ui_element.configure(placeholder_text=text)
            ui_element.configure(state='disabled')

    def clear_options(self):
        self.max_coll_size.delete(0, 'end')
        self.set_placeholder(self.max_coll_size, 'Max size')
        self.cat_ids.delete(0, 'end')
        self.set_placeholder(self.cat_ids, 'Category IDs')
        self.pp_min.delete(0, 'end')
        self.set_placeholder(self.pp_min, 'Min')
        self.pp_max.delete(0, 'end')
        self.set_placeholder(self.pp_max, 'Max')
        self.clusters_cmb_box.set('Clusters')
        self.clear_extra_input()
        self.ratio_local.delete(0, 'end')
        self.ratio_offshore.delete(0, 'end')
        self.ratio_local.insert(0, 3)
        self.ratio_offshore.insert(0, 2)

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

    def reset_collection(self):
        self.working_coll.set_df(self.original_src.get_df().copy(deep=True))

    # ******************************* EXTRA INPUT *******************************

    def extra_input_handler(self):
        self.extra_input = tkinter.simpledialog.askstring(title="+Input",
                                                          prompt="Paste seller and product ids in 2 columns x "
                                                                 "rows format,\n without headers:")

        self.extra_input = logic.validate_extra_input(self.extra_input)

        if self.extra_input is None:
            self.clear_extra_input()
            tkinter.messagebox.showerror('Error', "Couldn't process pasted input. Please make sure to paste 2 columns "
                                                  "per x rows, as in spreadsheet, without headers.")
            return

        total_extra_input = len(self.extra_input['product_id'])
        if total_extra_input != 0:
            self.extra_input_btn.configure(text=f'+Input: {total_extra_input}')
            self.clr_extra_input_btn.configure(fg_color='red', state=tkinter.NORMAL)

    def clear_extra_input(self):
        self.extra_input = ''
        self.extra_input_btn.configure(text='+Input')
        self.clr_extra_input_btn.configure(fg_color='gray38', state=tkinter.DISABLED)

    # ******************************* READING CRITERIA *******************************

    def get_user_set_coll_size(self):
        user_custom_size = self.max_coll_size.get()
        try:
            if len(self.max_coll_size.get()) != 0:
                return logic.validate_size(user_custom_size)
            else:
                return None
        except ValueError:
            messagebox.showerror('Collection size error', 'Please input a natural number, eg. 10000.')
            return None

    def get_cat_ids(self):
        cat_ids = self.cat_ids.get()
        try:
            src_cat_ids = self.working_coll.get_column_values('cat_id')
            return logic.validate_cat_ids(cat_ids, src_cat_ids)
        except:
            return None

    def get_cluster(self):
        cluster = self.clusters_cmb_box.get()
        if cluster in ['All', 'Clusters', 'N/A']:
            return None
        else:
            return cluster

    def get_price_points(self):
        price_points = {
            'min': self.pp_min.get(),
            'max': self.pp_max.get()
        }

        for key, price in price_points.items():
            if price != '':
                try:
                    price = float(price)
                    # check for negative
                    if price < 0:
                        price_points[key] = price * -1
                    else:
                        price_points[key] = price
                except:
                    messagebox.showerror('Price points error', 'Please make sure price points are positive numbers.\n'
                                                               'Floating points number should be typed in with a dot.')
                    price_points[key] = ''

        return logic.validate_price_points(price_points)

    def get_ratio(self):
        try:
            ratio = {
                'local': int(self.ratio_local.get()),
                'offshore': int(self.ratio_offshore.get())
            }
            # check if negative
            for key, val in ratio.items():
                if val < 0:
                    ratio[key] = val * -1
            return ratio
        except:
            messagebox.showerror('Ratio value error', 'Please input a natural number for ratio, eg. 3, 0 etc.')
            return None

    def get_sort_values(self):
        sort = {
            'sort_first': '',
            'sort_next': ''
        }

        if bool(self.ado_var.get()):
            sort['sort_first'] = 'ado'
        if bool(self.rating_var.get()):
            sort['sort_next'] = 'rating'

        return sort

    # ******************************* GENERATING COLLECTION *******************************

    def get_all_criteria(self):
        criteria = {}
        criteria['size_min'] = None
        criteria['size_max'] = self.get_user_set_coll_size()
        criteria['extra_input'] = self.extra_input
        criteria['cat_id'] = self.get_cat_ids()
        criteria['cluster'] = self.get_cluster()
        prices = self.get_price_points()
        if prices is None:
            criteria['price_min'], criteria['price_max'] = '', ''
        else:
            criteria['price_min'] = prices['min']
            criteria['price_max'] = prices['max']
        sort = self.get_sort_values()
        criteria['sort_first'] = sort['sort_first']
        criteria['sort_next'] = sort['sort_next']
        criteria['ratio'] = self.get_ratio()
        criteria['out_of_stock'] = bool(self.sold_out_checkbox_val.get())
        return criteria

    def generate_collection(self):
        if not isinstance(self.working_coll, (CmsColl, BankColl)):
            messagebox.showerror('Error', 'Please select a data source first.')
            return
        try:
            criteria = self.get_all_criteria()
            self.working_coll.process_by_criteria(criteria)
            if len(self.working_coll.messages) > 0:
                messages_str = '\n'.join(self.working_coll.messages)
                messagebox.showinfo('Messages', messages_str)
            if len(self.working_coll.get_column_values('product_id')) == 0:
                messagebox.showinfo('Collection empty',
                                    'Created collection is empty. Please consider changing criteria.\nNot saving file.')
                self.reset_collection()
                return

            user_save_path = filedialog.asksaveasfilename(filetypes=DEF_F_EXTENSION,
                                                          defaultextension=DEF_F_EXTENSION)
            if user_save_path == '':
                messagebox.showerror('Error', 'Please select a directory and a filename to save the generated collection.')
                self.reset_collection()
                return
            fh = CmsFileHelper('')
            # adjust to use in app
            fh.upload_f_path = user_save_path
            prep_result = fh.prepare_upload_f(seller_product_ids=self.working_coll.export_for_upload())
            if not prep_result:
                messagebox.showerror('Error', 'Failed to generate collection upload file.')
                self.reset_collection()
                return
            if bool(self.full_file_checkbox_val.get()):
                f_name = user_save_path.split("/")[-1]
                save_path = user_save_path.split(f_name)[0]
                full_save_path = f'{save_path}full_{f_name}'
                full_prep_result = fh.prepare_custom_full_f(self.working_coll, full_save_path)
                if not full_prep_result:
                    messagebox.showerror('Error', 'Failed to generate full collection file.')
                    self.reset_collection()
                    return
            messagebox.showinfo('Success', 'File(s) generated!')
            self.reset_collection()
        except:
            messagebox.showerror('Error', 'Failure in collection generation process.')
            self.reset_collection()
            return


if __name__ == "__main__":
    app = App()
    app.mainloop()
