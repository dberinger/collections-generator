from typing import Union
import pandas as pd


class Collection:
    def __init__(self, df):
        self.df = df
        self.extra_input = None
        self.is_extra_input_merged = False
        self.size_max = 5000
        self.columns = {}
        self.local_to_offshore = {}
        self.messages = []

    def get_df(self):
        return self.df

    def set_df(self, new_df):
        self.df = new_df

    def get_column_values(self, column_key):
        return list(self.df[self.columns[column_key]].values)

    def get_extra_input_size(self):
        if self.extra_input is None:
            return 0
        else:
            return len(self.extra_input)

    def get_df_size(self):
        return len(self.df)

    def get_total_size(self):
        if self.is_extra_input_merged:
            return self.get_df_size()
        else:
            return self.get_df_size() + self.get_extra_input_size()

    def get_messages(self):
        return self.messages

    def add_message(self, message: Union[list, str]):
        if isinstance(message, list):
            self.messages.extend(message)
        elif isinstance(message, str):
            self.messages.append(message)

    def shuffle(self, ratio: dict, inplace=True):
        df = self.get_df()

        # if one of ratio values is 0, skip shuffling and return df filtered by non-zero value
        if ratio['local'] == 0:
            final_df = df.loc[df[self.columns['seller_type']] == self.local_to_offshore['offshore']]
            if inplace:
                self.set_df(final_df)
                return
            else:
                return final_df

        if ratio['offshore'] == 0:
            final_df = df.loc[df[self.columns['seller_type']] == self.local_to_offshore['local']]
            if inplace:
                self.set_df(final_df)
                return
            else:
                return final_df

        local_list = df.loc[df[self.columns['seller_type']] == self.local_to_offshore['local']].values.tolist()
        offshore_list = df.loc[
            df[self.columns['seller_type']] == self.local_to_offshore['offshore']].values.tolist()

        local_len = len(local_list)
        offshore_len = len(offshore_list)

        # if ratio has both non-zero values, but the df itself only has offshore or local products, so no point
        # shuffling
        if local_len == 0 or offshore_len == 0:
            self.add_message('Local or Offshore only products. Not shuffling.')
            if inplace:
                return
            else:
                return df

        local_index_list = []
        offshore_index_list = []

        local_c = 0
        offshore_c = 0
        i = 0
        loop_reps = local_len + offshore_len

        while i < loop_reps:
            # LOCAL
            if local_c < local_len:
                for _ in range(ratio['local']):
                    if local_c < local_len:
                        local_index_list.append(i)
                        i += 1
                        local_c += 1
            # OFFSHORE
            if offshore_c < offshore_len:
                for _ in range(ratio['offshore']):
                    if offshore_c < offshore_len:
                        offshore_index_list.append(i)
                        i += 1
                        offshore_c += 1

        shuffled_list = [None] * loop_reps

        for index, row in zip(local_index_list, local_list):
            shuffled_list[index] = row

        for index, row in zip(offshore_index_list, offshore_list):
            shuffled_list[index] = row

        final_df = pd.DataFrame(shuffled_list, columns=list(df.columns))

        if inplace:
            self.set_df(final_df)
        else:
            return final_df

    def filter_by_single_price_points(self, min_price, max_price, inplace=True):
        new_df = None
        # fix for numbers with commas like 1,500,232
        try:
            self.df[self.columns['price']] = self.df[self.columns['price']].str.replace(',', '').astype(float)
        except Exception as e:
            if str(e) != 'Can only use .str accessor with string values!':
                print(e)

        # converting all prices to numeric values
        self.df[self.columns['price']] = pd.to_numeric(self.df[self.columns['price']])

        if min_price and max_price == '':
            new_df = self.df[(self.df[self.columns['price']] >= min_price)]
        elif min_price == '' and max_price:
            new_df = self.df[(self.df[self.columns['price']] <= max_price)]
        elif min_price == max_price == '':
            new_df = self.df.copy(deep=True)
        elif min_price == max_price != '':
            new_df = self.df[(self.df[self.columns['price']] == min_price)]
        else:
            # auto-reverse in case min and max mixed up
            if min_price > max_price:
                min_price, max_price = max_price, min_price
            new_df = self.df[(self.df[self.columns['price']] >= min_price) & (self.df[self.columns['price']]
                                                                              <= max_price)]

        if len(new_df) == 0:
            self.add_message(f"No values for price points min: {min_price}, max: {max_price}.")

        if inplace:
            self.set_df(new_df)
        else:
            return new_df

    def set_extra_input(self, extra_input_seller_product: dict):
        extra_df_columns = [self.columns['seller_id'], self.columns['product_id']]
        extra_df = pd.DataFrame(columns=extra_df_columns)
        extra_df[self.columns['seller_id']] = extra_input_seller_product['seller_id']
        extra_df[self.columns['product_id']] = extra_input_seller_product['product_id']
        # remove duplicates in extra in extra input
        extra_df.drop_duplicates(subset=self.columns['product_id'], keep='first', inplace=True)
        self.extra_input = extra_df

    def concat_extra_input(self):
        if self.extra_input is None or self.get_extra_input_size() == 0:
            return
        # remove duplicates from main df by product_id column
        extra_df_products = self.extra_input[self.columns['product_id']].tolist()
        self.set_df(self.df[~self.df[self.columns['product_id']].isin(extra_df_products)])
        self.set_df(pd.concat([self.extra_input, self.df]))
        self.is_extra_input_merged = True

    def sort_by(self, column_key: str, asc_order: bool = False):
        col_name = self.columns[column_key]
        try:
            self.df.sort_values(by=[col_name], ascending=asc_order, inplace=True)
        except KeyError:
            self.add_message(f'Failed to sort by {col_name}.')
            return

    def export_for_upload(self):
        return {
            'seller_id': self.get_column_values('seller_id'),
            'product_id': self.get_column_values('product_id')
        }


class CmsColl(Collection):
    def __init__(self, df):
        super().__init__(df)
        self.columns = {
            'seller_id': 'Seller ID',
            'product_id': 'Product ID',
            'price': 'Price',
            'old_price': 'Old Price',
            'ado': 'ADO',
            'stock': 'Stock',
            'rating': 'Rating',
            'seller_type': 'Offshore Seller'
        }
        self.local_to_offshore = {
            'local': False,
            'offshore': True
        }

    def remove_out_of_stock(self):
        try:
            self.df = self.df[self.df['Stock'] != 0]
        except KeyError:
            self.add_message('Failed to find Stock column.')
            return

    def process_by_criteria(self, criteria: dict):
        try:
            if criteria['size_max']:
                self.size_max = criteria['size_max']

            if criteria['extra_input']:
                self.set_extra_input(criteria['extra_input'])

            if criteria['out_of_stock']:
                self.remove_out_of_stock()

            if criteria['price_min'] or criteria['price_max']:
                self.filter_by_single_price_points(criteria['price_min'], criteria['price_max'])

            sort_first_val = criteria['sort_first']
            sort_next_val = criteria['sort_next']

            if sort_first_val and sort_next_val:
                sort_first_val = self.columns[sort_first_val]
                sort_next_val = self.columns[sort_next_val]
                self.df = self.df.sort_values([sort_first_val, sort_next_val], ascending=[False, False])
            elif sort_first_val:
                self.sort_by(sort_first_val)
            elif sort_next_val:
                self.sort_by(sort_next_val)

            if criteria['ratio']:
                self.shuffle(criteria['ratio'])

            if criteria['extra_input']:
                self.concat_extra_input()

            if criteria['size_min']:
                if self.get_total_size() < criteria['size_min']:
                    self.add_message(f"Min size {criteria['min_size']} not reached. Instead got "
                                     f"{self.get_total_size()}.")

            if self.get_total_size() > self.size_max:
                self.df = self.df[:self.size_max]

        except Exception as e:
            self.add_message('Failure in Collection creation')
            print(e)


class BankColl(Collection):
    def __init__(self, df):
        super().__init__(df)
        self.columns = {
            'seller_id': 'seller_id',
            'product_id': 'product_id',
            'price': 'price',
            'ado': 'ado',
            'discount': 'discount',
            'cat_id': 'category_id',
            'cluster': 'cluster',
            'rating': 'rating',
            'seller_type': 'seller_type'
        }
        self.local_to_offshore = {
            'local': 'Local',
            'offshore': 'Offshore'
        }

    def get_clusters(self):
        try:
            return list(self.df[self.columns['cluster']].unique())
        except KeyError:
            self.add_message('Cluster column not found.')
            return []

    def filter_by_cluster(self, cluster: str):
        if cluster not in self.get_clusters():
            self.add_message(f"Cluster: {cluster} not found in source")
            # not returning empty df, because global ids or l3s might give sth still
            return

        self.df = self.df.loc[self.df[self.columns['cluster']] == cluster]

    def filter_by_cat_allocation(self, cat_ids: list):
        if cat_ids:
            valid_cats = []
            invalid_cats = []
            bank_cat_ids = self.get_column_values('cat_id')

            for val in cat_ids:
                val = str(val).strip()
                if val.isnumeric() and int(val) in bank_cat_ids:
                    if val not in valid_cats:
                        valid_cats.append(int(val))
                else:
                    invalid_cats.append(val)

            if len(invalid_cats) > 0:
                self.add_message(f'Invalid categories: {invalid_cats}.')

            if len(valid_cats) != 0:
                self.df = self.df.loc[self.df[self.columns['cat_id']].isin(valid_cats)]
            else:
                self.add_message(f'None of the selected categories are valid.')
                return

    def process_by_criteria(self, criteria: dict):
        try:
            if criteria['size_max']:
                self.size_max = criteria['size_max']

            if criteria['extra_input']:
                self.set_extra_input(criteria['extra_input'])

            if criteria['cat_id']:
                self.filter_by_cat_allocation(criteria['cat_id'])

            if criteria['price_min'] or criteria['price_max']:
                self.filter_by_single_price_points(criteria['price_min'], criteria['price_max'])

            sort_first_val = criteria['sort_first']
            sort_next_val = criteria['sort_next']

            if sort_first_val and sort_next_val:
                sort_first_val = self.columns[sort_first_val]
                sort_next_val = self.columns[sort_next_val]
                self.df = self.df.sort_values([sort_first_val, sort_next_val], ascending=[False, False])
            elif sort_first_val:
                self.sort_by(sort_first_val)
            elif sort_next_val:
                self.sort_by(sort_next_val)

            if criteria['ratio']:
                self.shuffle(criteria['ratio'])

            if criteria['extra_input']:
                self.concat_extra_input()

            if criteria['size_min']:
                if self.get_total_size() < criteria['size_min']:
                    self.add_message(f"Min size {criteria['min_size']} not reached. Instead got "
                                     f"{self.get_total_size()}.")

            if self.get_total_size() > self.size_max:
                self.df = self.df[:self.size_max]

        except Exception as e:
            self.add_message('Failure in Collection creation')
            print(e)
