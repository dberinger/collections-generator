import os
from glob import glob
from time import sleep
from datetime import datetime
from typing import Union
import pandas as pd
from models.Collection import CmsColl, BankColl
import config


class CmsFileHelper:
    def __init__(self, coll_id: str):
        self.coll_id = coll_id
        self.source_type = None
        self.cms_export_f_name_partial = f'coll_{coll_id}_selected_products*.csv'
        self.cms_ori_export_f = None
        self.cms_ori_export_f_path = None
        self.download_dir = config.DOWNLOADS_DIR
        self.download_wait_t = config.DOWNLOAD_WAIT_T
        self.upload_f_name = f'upload_{coll_id}.csv'
        self.upload_f_path = None
        self.upload_f_dir = config.UPLOADS_DIR
        self.upload_headers = ['sellerid', 'productid', 'stock']
        self.upload_f_count = None
        self.messages = []
        self.totals = {
            'ori': '',
            'new': ''
        }

    def add_message(self, message: Union[list, str]):
        if isinstance(message, list):
            for i in message:
                self.messages.append(i)
        elif isinstance(message, str):
            self.messages.append(message)

    # this will return name of the file that is matching naming pattern with collection ID and a creation time older
    # than time at the start of the iteration.
    def get_expected_file(self, click_time: datetime,
                          wait_t_s: int = None, f_name_partial: str = None, download_directory: str = None):

        if wait_t_s is None:
            wait_t_s = self.download_wait_t

        if f_name_partial is None:
            f_name_partial = self.cms_export_f_name_partial

        if download_directory is None:
            download_directory = self.download_dir

        try:
            os.chdir(download_directory)
        except:
            self.add_message('Incorrect download directory')
            return False

        # flist = glob(f_name) #- this returns list of files matching f_name
        # max(flist, key=os.path.getctime) #- this returns the latest file in the list
        elapsed_time = 0
        # basically while no file found created after the click time datetime
        try:
            while datetime.fromtimestamp(
                    os.path.getctime(max(glob(f_name_partial), key=os.path.getctime, default=0))) < click_time:
                print(F"Waiting {wait_t_s - elapsed_time} seconds for download...")
                sleep(5)
                elapsed_time += 5
                if elapsed_time >= wait_t_s:
                    return False
            latest_export = max(glob(f_name_partial), key=os.path.getctime, default=0)
            if datetime.fromtimestamp(os.path.getctime(latest_export)) > click_time:
                print(latest_export)
                self.cms_ori_export_f = latest_export
                self.cms_ori_export_f_path = fr'{download_directory}\{latest_export}'
                return latest_export
        except Exception as e:
            self.add_message(f'Exception occurred while waiting for file download.\n{e}')
            print(e)
            return False

    # upload file can be prepared from a dataframe's seller and product id lists or from a collection cms export file
    def prepare_upload_f(self, backup: bool = False, output_f_dir: str = None, seller_product_ids: dict = None, src_f_path: str = None):
        if output_f_dir is None:
            if self.upload_f_dir:
                output_f_dir = self.upload_f_dir
            else:
                self.add_message('Incorrect file upload output directory.')
                return False

        if seller_product_ids is None and src_f_path is None:
            self.add_message("Can't prepare upload file. No source.")
            return False

        if seller_product_ids is None:
            try:
                df = pd.read_csv(src_f_path, usecols=['Seller ID', 'Product ID'])
                df.rename(columns={'Seller ID': 'sellerid', 'Product ID': 'productid'}, inplace=True, errors="raise")
                df['stock'] = ""
            except:
                self.add_message(f"ERROR: can't read file: {src_f_path}")
                return False
        elif src_f_path is None:
            df = pd.DataFrame(columns=self.upload_headers)
            df['sellerid'] = seller_product_ids['seller_id']
            df['productid'] = seller_product_ids['product_id']

        try:
            if backup:
                f_name = f'backup_{self.upload_f_name}'
            else:
                f_name = self.upload_f_name

            if self.upload_f_path is None:
                self.upload_f_path = fr'{output_f_dir}\{f_name}'
            df[['sellerid', 'productid', 'stock']].to_csv(self.upload_f_path, index=False)
            is_valid, product_count = self.is_upload_f_valid(self.upload_f_path)
            self.upload_f_count = product_count

            if is_valid:
                return True
            else:
                self.add_message('Upload file generated, but invalid.')
                return False
        except Exception as e:
            self.add_message('Upload file not generated')
            print(str(e))
            return False

    def prepare_full_f(self, collection: Union[CmsColl, BankColl], output_f_dir: str = None):
        try:
            if output_f_dir is None:
                if self.upload_f_dir:
                    output_f_dir = self.upload_f_dir
                else:
                    self.add_message('Incorrect file upload output directory.')
                    return False

                f_name = f'{self.coll_id}_full.csv'
                if self.upload_f_path is None:
                    self.upload_f_path = fr'{output_f_dir}\{f_name}'
                df = collection.get_df()
                df[df.columns.tolist()].to_csv(self.upload_f_path, index=False)

        except Exception as e:
            self.add_message('Full file not generated')
            return False

    def prepare_custom_full_f(self, collection: Union[CmsColl, BankColl], output_full_path: str):
        try:
            df = collection.get_df()
            df[df.columns.tolist()].to_csv(output_full_path, index=False)
            return True
        except Exception as e:
            self.add_message('Full file not generated')
            return False


    @staticmethod
    def are_all_values_instance_of(val_type, column):
        try:
            return all(isinstance(x, val_type) for x in column)
        except:
            print("ERROR: couldn't check instance type of all values in column.")
            return False

    def is_upload_f_valid(self, f_path):
        try:
            df = pd.read_csv(f_path)
        except:
            print(f"ERROR: can't read file: {f_path}")
            return False
        # check headers
        try:
            headers = list(df.columns)
            if headers != self.upload_headers:
                print("ERROR: incorrect headers.")
                return False
        except:
            print("ERROR: incorrect headers.")

        # check if first two columns are equal length and values are numbers
        if not (df['sellerid'].count() == df['productid'].count() != 0):
            return False, df['productid'].count()

        if not (self.are_all_values_instance_of(int, df["sellerid"]) and (self.are_all_values_instance_of(int,
                                                                                                        df["productid"]))):
            return False, df['productid'].count()

        # check if seller id is shorter than product id.
        if not (all([(i < j) for i, j in zip(df['sellerid'], df['productid'])])):
            return False, df['productid'].count()

        # check if last column is empty. Stock column is actually never filled
        if not df['stock'].count() == 0:
            return False, df['productid'].count()

        return True, df['productid'].count()
