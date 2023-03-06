import pandas as pd
from models.Collection import CmsColl, BankColl
from config import DEF_F_EXTENSION, CMS_COLL_COLUMNS, BANK_COLL_COLUMNS, COLL_MAX_SIZE


def validate_src(source_f_path: str):
    try:
        df = pd.read_csv(source_f_path, low_memory=False)
    except Exception as e:
        msg = "Error while selecting/opening source file."
        return msg, None

    df_columns = list(df.columns)
    if df_columns == CMS_COLL_COLUMNS:
        return 'cms', df
    elif df_columns == BANK_COLL_COLUMNS:
        return 'bank', df
    else:
        msg = f'Invalid source column headers. Please try:\n' \
              f'For CMS: {CMS_COLL_COLUMNS}.\n\n' \
              f'For Products Bank: {BANK_COLL_COLUMNS}\n'
        return msg, None


def validate_extra_input(extra_input: str):
    valid_input = {
        'seller_id': [],
        'product_id': []
    }
    try:
        user_input = extra_input.split('\n')

        for i, pair in enumerate(user_input):
            pair = pair.split('\t')
            try:
                if len(pair[0]) == 0 or len(pair[1]) == 0:
                    continue
            except IndexError:
                continue
            if pair[0].isnumeric() and pair[1].isnumeric():
                if len(pair[0]) > len(pair[1]):
                    valid_input['product_id'].append(int(pair[0].strip()))
                    valid_input['seller_id'].append(int(pair[1].strip()))
                elif len(pair[0]) < len(pair[1]):
                    valid_input['product_id'].append(int(pair[1].strip()))
                    valid_input['seller_id'].append(int(pair[0].strip()))

        if len(valid_input['product_id']) > 0:
            return valid_input
        else:
            return None
    except:
        return None


def validate_size(user_size: str, max_size: int = COLL_MAX_SIZE):
    user_size = int(user_size)
    if user_size <= max_size:
        return user_size
    elif user_size >= max_size:
        return max_size


def validate_cat_ids(user_cats: str, cats_in_src: list):
    valid_cat_ids = []
    try:
        user_cats = list(set(user_cats.split('\n')))
        for val in user_cats:
            try:
                val = int(val.strip())
                if val in cats_in_src:
                    valid_cat_ids.append(val)
            except:
                continue
        if len(valid_cat_ids) > 0:
            return valid_cat_ids
        else:
            return None
    except:
        return None


def validate_clusters(clusters: list):
    clusters = list(set(clusters))
    for val in clusters:
        if not isinstance(val, str):
            clusters.remove(val)
    # append All in case user changes their mind
    if len(clusters) > 0:
        clusters.append('All')

    if len(clusters) == 0:
        return None

    return clusters


def validate_price_points(price_points: dict):
    for key, price in price_points.items():
        try:
            price_points[key] = float(price)
        except:
            price_points[key] = ''

    # check if min and max are not switched
    try:
        if price_points['min'] > price_points['max']:
            price_points['min'], price_points['max'] = price_points['max'], price_points['min']
    except:
        return price_points

    return price_points
