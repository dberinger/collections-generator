import unittest
import pandas as pd
from models.Collection import CmsColl, BankColl
from models.DummyDataGenerator import DummyDataGenerator
from config import PROJECT_DIR


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.cms_df = pd.read_csv(fr'{PROJECT_DIR}\tests\Collection\files\cms_20_test.csv')
        self.bank_df = pd.read_csv(fr'{PROJECT_DIR}\tests\Collection\files\bank_20_test.csv')

    def getCmsColl(self):
        return CmsColl(self.cms_df)

    def getBankColl(self):
        return BankColl(self.bank_df)

    def test_shuffle(self):
        local_key = 'local'
        offshore_key = 'offshore'

        ratio_cases = [
            {
                local_key: 0,
                offshore_key: 1
            },
            {
                local_key: 1,
                offshore_key: 0
            },
            {
                local_key: 1,
                offshore_key: 1
            },
            {
                local_key: 3,
                offshore_key: 2
            },
            {
                local_key: 1,
                offshore_key: 2
            },
        ]

        # case 0 - only offshore
        for coll in [self.getCmsColl(), self.getBankColl()]:
            coll.shuffle(ratio_cases[0])
            self.assertNotIn(coll.local_to_offshore['local'], coll.get_column_values('seller_type'))

        # case 1 - only local
        for coll in [self.getCmsColl(), self.getBankColl()]:
            coll.shuffle(ratio_cases[1])
            self.assertNotIn(coll.local_to_offshore['offshore'], coll.get_column_values('seller_type'))

        # case 2 - 1 : 1
        case2_cms_manual_result = [False, True, False, True, False, True, False, True, False, True, False, False, False,
                                   False, False, False, False, False, False, False]
        case2_bank_manual_result = ['Local', 'Offshore', 'Local', 'Offshore', 'Local', 'Offshore', 'Local', 'Offshore',
                                    'Local', 'Offshore', 'Local', 'Offshore', 'Local', 'Offshore', 'Local', 'Offshore',
                                    'Local', 'Local', 'Local', 'Local']

        case2_shuffled_cms_coll = self.getCmsColl()
        case2_shuffled_bank_coll = self.getBankColl()

        case2_shuffled_cms_coll.shuffle(ratio_cases[2])
        case2_shuffled_bank_coll.shuffle(ratio_cases[2])

        self.assertEqual(case2_cms_manual_result, case2_shuffled_cms_coll.get_column_values('seller_type'))
        self.assertEqual(case2_bank_manual_result, case2_shuffled_bank_coll.get_column_values('seller_type'))

        # case 3 - 3 : 2
        case3_cms_manual_result = [False, False, False, True, True, False, False, False, True, True, False, False,
                                   False, True, False, False, False, False, False, False]
        case3_bank_manual_result = ['Local', 'Local', 'Local', 'Offshore', 'Offshore', 'Local', 'Local', 'Local',
                                    'Offshore', 'Offshore', 'Local', 'Local', 'Local', 'Offshore', 'Offshore', 'Local',
                                    'Local', 'Local', 'Offshore', 'Offshore']

        case3_shuffled_cms_coll = self.getCmsColl()
        case3_shuffled_bank_coll = self.getBankColl()

        case3_shuffled_cms_coll.shuffle(ratio_cases[3])
        case3_shuffled_bank_coll.shuffle(ratio_cases[3])

        self.assertEqual(case3_cms_manual_result, case3_shuffled_cms_coll.get_column_values('seller_type'))
        self.assertEqual(case3_bank_manual_result, case3_shuffled_bank_coll.get_column_values('seller_type'))

        # case 4 - 1 : 2
        case4_cms_manual_result = [False, True, True, False, True, True, False, True, False, False, False, False, False,
                                   False, False, False, False, False, False, False]
        case4_bank_manual_result = ['Local', 'Offshore', 'Offshore', 'Local', 'Offshore', 'Offshore', 'Local',
                                    'Offshore', 'Offshore', 'Local', 'Offshore', 'Offshore', 'Local', 'Local', 'Local',
                                    'Local', 'Local', 'Local', 'Local', 'Local']

        case4_shuffled_cms_coll = self.getCmsColl()
        case4_shuffled_bank_coll = self.getBankColl()

        case4_shuffled_cms_coll.shuffle(ratio_cases[4])
        case4_shuffled_bank_coll.shuffle(ratio_cases[4])

        self.assertEqual(case4_cms_manual_result, case4_shuffled_cms_coll.get_column_values('seller_type'))
        self.assertEqual(case4_bank_manual_result, case4_shuffled_bank_coll.get_column_values('seller_type'))

    def test_remove_out_of_stock(self):
        cms_coll = self.getCmsColl()
        self.assertIn(0, cms_coll.get_column_values('stock'))
        cms_coll.remove_out_of_stock()
        self.assertNotIn(0, cms_coll.get_column_values('stock'))

    def test_filter_by_single_price_points(self):
        test_prices = [[10, 100], [100, 10], [10, ''], ['', 100], ['', ''], [9.50, 213.44], [150.99, ''], ['', 455.25], [5, 5]]

        for price in test_prices:
            min_price = price[0]
            max_price = price[1]

            for coll in [self.getCmsColl(), self.getBankColl()]:
                coll.filter_by_single_price_points(min_price, max_price)
                pp_df = coll.df.copy(deep=True)
                if min_price == '' and max_price != '':
                    result = pp_df[coll.columns['price']].le(max_price)
                    self.assertNotIn(False, result)
                elif max_price == '' and min_price != '':
                    result = pp_df[coll.columns['price']].ge(min_price)
                    self.assertNotIn(False, result)
                elif min_price == max_price == '':
                    self.assertEqual(coll.get_column_values('price'), pp_df[coll.columns['price']].values.tolist())
                elif min_price == max_price != '':
                    if min_price in pp_df[coll.columns['price']].values.tolist():
                        result = pp_df[coll.columns['price']].eq(min_price)
                        self.assertNotIn(False, result)
                    else:
                        self.assertEqual(True, pp_df.empty)
                else:
                    result = pp_df[coll.columns['price']].between(min_price, max_price)
                    self.assertNotIn(False, result)

    def test_extra_input(self):
        cms_coll = self.getCmsColl()
        bank_coll = self.getBankColl()

        # generate some random input
        dg = DummyDataGenerator('bank', 50)
        seller_ids = dg.df[bank_coll.columns['seller_id']].values.tolist()
        product_ids = dg.df[bank_coll.columns['product_id']].values.tolist()

        # combine random input from above and double 5 values to create duplicates
        test_extra_input = {
            'seller_id': seller_ids + seller_ids[:5],
            'product_id': product_ids + product_ids[:5]
        }

        for coll in [cms_coll, bank_coll]:
            # setting
            coll.set_extra_input(test_extra_input)
            # checks if duplicates were dropped by column 'product_id' and input added
            # Seller ids can be duplicated
            self.assertEqual(coll.extra_input[coll.columns['seller_id']].values.tolist(), seller_ids)
            self.assertEqual(coll.extra_input[coll.columns['product_id']].values.tolist(), product_ids)

            # concatenating with Collection's main Dataframe
            # add some new duplicates shared with main Dataframe
            test_extra_input2 = {
                'seller_id': seller_ids + coll.get_column_values('seller_id')[:5],
                'product_id': product_ids + coll.get_column_values('product_id')[:5]
            }
            coll.set_extra_input(test_extra_input2)
            # check if input is marked merged
            self.assertEqual(False, coll.is_extra_input_merged)
            coll.concat_extra_input()
            self.assertEqual(True, coll.is_extra_input_merged)

            extra_input_len = len(coll.extra_input[coll.columns['seller_id']])
            self.assertEqual(coll.get_column_values('seller_id')[:extra_input_len], test_extra_input2['seller_id'])
            self.assertEqual(coll.get_column_values('product_id')[:extra_input_len], test_extra_input2['product_id'])

    def test_sort_by(self):
        for column_key in ['rating', 'ado']:
            for coll in [self.getCmsColl(), self.getBankColl()]:
                ratings = coll.get_column_values(column_key)
                self.assertNotEqual(coll.get_column_values(column_key), sorted(ratings, reverse=True))
                coll.sort_by(column_key)
                self.assertEqual(coll.get_column_values(column_key), sorted(ratings, reverse=True))

    def test_clusters(self):
        bank_coll = self.getBankColl()
        dg = DummyDataGenerator('bank', 10)

        clusters = bank_coll.get_clusters()
        self.assertEqual(sorted(clusters), sorted(dg.val_ranges['cluster']))

        bank_coll.filter_by_cluster('Fashion')
        self.assertEqual(['Fashion'], bank_coll.get_clusters())

    def test_categories(self):
        bank_coll = self.getBankColl()
        test_valid_cats = [1, 5]
        test_half_valid_cats = ['1', 5, 'abc', 2000]
        test_invalid_cats = [100, 'abc', '', 5.55]

        bank_coll.filter_by_cat_allocation(test_invalid_cats)
        self.assertEqual('None of the selected categories are valid.' in bank_coll.messages, True)

        bank_coll.filter_by_cat_allocation(test_half_valid_cats)
        self.assertEqual({1, 5}, set(bank_coll.get_column_values('cat_id')))

        bank_coll2 = self.getBankColl()
        bank_coll2.filter_by_cat_allocation(test_valid_cats)
        self.assertEqual(set(test_valid_cats), set(bank_coll2.get_column_values('cat_id')))

    def test_process_by_criteria(self):
        d_coll = self.getBankColl()
        dg = DummyDataGenerator('bank', 50)
        test_extra_input = {
            'seller_id': dg.df[d_coll.columns['seller_id']].values.tolist(),
            'product_id': dg.df[d_coll.columns['product_id']].values.tolist()
        }
        test_crits = {
            'size_min': 100,
            'size_max': 3000,
            'extra_input': test_extra_input,
            'cat_id': [2, 3],
            'price_min': 100,
            'price_max': 500,
            'sort_first': 'ado',
            'sort_next': 'rating',
            'ratio': {
                'local': 3,
                'offshore': 2
            },
            'out_of_stock': True
        }

        for coll in [self.getCmsColl(), self.getBankColl()]:
            coll.process_by_criteria(test_crits)


if __name__ == '__main__':
    unittest.main()
