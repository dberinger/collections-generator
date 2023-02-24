from Collection import CmsColl, BankColl
import pandas as pd
from random import sample, choices, uniform, randrange
from tkinter.filedialog import asksaveasfile


class DummyDataGenerator:

    def __init__(self, sample_type: str, size: int):
        # types are cms or bank
        self.sample_type = sample_type
        self.col_mapping = {}
        self.cms_coll = CmsColl(pd.DataFrame())
        self.bank_coll = BankColl(pd.DataFrame())
        self.df = self.gen_dummy_df()
        self.size = size
        self.val_ranges = {
            'seller_id': {
                'min': 100000,
                'max': 999999
            },
            'product_id': {
                'min': 10000000,
                'max': 99999999
            },
            'price': {
                'min': 1.00,
                'max': 1000.00
            },
            'ado': {
                'min': 0.0,
                'max': 1.0
            },
            'stock': {
                'min': 0,
                'max': 10000
            },
            'rating': {
                'min': 1,
                'max': 5
            },
            'discount': {
                'min': 0.0,
                'max': 1.0
            },
            'cat_id': {
                'min': 1,
                'max': 10
            },
            'seller_type': {

            },
            'cluster': ['Electronics', 'FMCG', 'Lifestyle', 'Fashion']
        }
        self.fill_df()

    def gen_dummy_df(self):
        if self.sample_type == 'cms':
            self.col_mapping = self.cms_coll.columns
        elif self.sample_type == 'bank':
            self.col_mapping = self.bank_coll.columns
        else:
            print("Initiate with type cms or bank.")
            return None

        return pd.DataFrame(columns=list(self.col_mapping.values()))

    def fill_df(self):
        # seller & product id
        for k in ['seller_id', 'product_id']:
            self.df[self.col_mapping[k]] = sample(range(self.val_ranges[k]['min'], self.val_ranges[k]['max']),
                                                  self.size)

        # price
        price_floats = []
        for _x in range(self.size):
            price_floats.append(round(uniform(self.val_ranges['price']['min'], self.val_ranges['price']['max']), 2))
        self.df[self.col_mapping['price']] = price_floats

        # rating
        self.df[self.col_mapping['rating']] = choices(
            [*range(self.val_ranges['rating']['min'], self.val_ranges['rating']['max'] + 1, 1)], k=self.size)

        # ado
        ado_floats = []
        for _x in range(self.size):
            ado_floats.append(round(uniform(self.val_ranges['ado']['min'], self.val_ranges['ado']['max']), 2))
        self.df[self.col_mapping['ado']] = choices(ado_floats, k=self.size)

        # cms only -----------------
        if self.sample_type == 'cms':

            # stock
            self.df[self.col_mapping['stock']] = choices(
                [*range(self.val_ranges['stock']['min'], self.val_ranges['stock']['max'] + 1)], k=self.size)

            # old prices
            base_prices = self.df[self.col_mapping['price']].tolist()
            old_prices = []

            for price in base_prices:
                max_price = price * (randrange(1, 10, 1))
                old_prices.append(round(uniform(price, max_price), 2))

            self.df[self.col_mapping['old_price']] = old_prices

            # local & offshore
            local_to_offshore_vals = [self.cms_coll.local_to_offshore['local'],
                                      self.cms_coll.local_to_offshore['offshore']]

            self.df[self.cms_coll.local_to_offshore['col_name']] = choices(local_to_offshore_vals, k=self.size)

        # bank only -----------------
        if self.sample_type == 'bank':

            # discount
            discount_floats = []
            for _x in range(self.size):
                discount_floats.append(
                    round(uniform(self.val_ranges['discount']['min'], self.val_ranges['discount']['max']), 2))
            self.df[self.col_mapping['discount']] = choices(discount_floats, k=self.size)

            # cat ids
            self.df[self.col_mapping['cat_id']] = choices(
                [*range(self.val_ranges['cat_id']['min'], self.val_ranges['cat_id']['max'] + 1, 1)], k=self.size)

            # cluster
            self.df[self.col_mapping['cluster']] = choices(self.val_ranges['cluster'], k=self.size)

            # local & offshore
            local_to_offshore_vals = [self.bank_coll.local_to_offshore['local'],
                                      self.bank_coll.local_to_offshore['offshore']]

            self.df[self.bank_coll.local_to_offshore['col_name']] = choices(local_to_offshore_vals, k=self.size)

    def save_to_csv(self):
        def_f_name = f'{self.sample_type}_{self.size}_dummy_data'
        save_f_path = asksaveasfile(initialfile=f'{def_f_name}.csv',
                                    defaultextension=".csv", filetypes=[("csv file(*.csv)", "*.csv")], )
        try:
            self.df.to_csv(save_f_path, index=False, lineterminator='\n')
            return True
        except OSError:
            print("ERROR: output directory not found.")
            return False


# select source type and sample size to generate and save to file

# dumdum = DummyDataGenerator('bank', 100)
# dumdum.save_to_csv()
