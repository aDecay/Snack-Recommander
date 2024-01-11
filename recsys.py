import pandas as pd
from surprise import Reader, Dataset, SVD, accuracy
from surprise.model_selection import train_test_split, cross_validate
from surprise.dataset import DatasetAutoFolds

class Recsys:
    def __init__(self, item_file, rating_file):
        self.item_file = item_file
        self.rating_file = rating_file

        self.algo = SVD(n_epochs=20, n_factors=50, random_state=0)
        self.reader = Reader(rating_scale=(1.0, 5.0))

        self.items = pd.read_csv(item_file)
        self.items['id'] = self.items['id'].apply(str)

        self.ratings = pd.read_csv(rating_file)
        self.ratings['uid'] = self.ratings['uid'].apply(str)
        self.ratings['iid'] = self.ratings['iid'].apply(str)
    
    def train(self):
        data_folds = DatasetAutoFolds(df=self.ratings[['uid', 'iid', 'rating']], reader = self.reader)
        trainset = data_folds.build_full_trainset()
        self.algo.fit(trainset)

    def predict(self, uid, iid):
        return self.algo.predict(str(uid), str(iid), verbose=False)
    
    def item_no_exp(self, uid):
        exp = self.ratings[self.ratings['uid'] == str(uid)]['iid']
        no_exp = self.items[~self.items['id'].isin(exp)]['id']
        return no_exp
    
    def recomm_by_surprise(self, uid, page, top_n = 10):
        no_exp = self.item_no_exp(uid)
        predictions = [self.algo.predict(str(uid), str(iid)) for iid in no_exp]

        def sortkey_est(pred):
            return pred.est

        predictions.sort(key=sortkey_est, reverse=True)
        top_predictions = predictions[page * top_n:min((page + 1) * top_n, len(no_exp))]
        
        id_list = [pred.iid for pred in top_predictions]
        rating_list = [pred.est for pred in top_predictions]
        name_list = [self.items[self.items['id'] == pred.iid]['name'].tolist()[0] for pred in top_predictions]

        pred_list = [(id, title, rating) for id, title, rating in zip(id_list, name_list, rating_list)]
        return pred_list

    def is_first_user(self, uid):
        return len(self.ratings[self.ratings['uid'] == str(uid)]) == 0
    
    def most_reviewed(self):
        def sortkey(iid):
            return len(self.ratings[self.ratings['iid'] == iid])
        
        item_list = self.items['id'].tolist()[:100]
        item_list.sort(key=sortkey, reverse=True)
        item_list = item_list[:10]

        iid_list = [iid for iid in item_list]
        name_list = [self.items[self.items['id'] == iid]['name'].tolist()[0] for iid in iid_list]
        num_reviews = [len(self.ratings[self.ratings['iid'] == iid]['iid']) for iid in iid_list]
        result = [(iid, name, reviews) for iid, name, reviews in zip(iid_list, name_list, num_reviews)]

        return result
    
    def append(self, new_data):
        self.ratings = pd.concat([self.ratings, pd.DataFrame(new_data)])

    def save_ratings(self):
        self.ratings.to_csv(self.rating_file, index=False)

    def cross_validate(self):
        print('start cross validation')
        data = Dataset.load_from_df(self.ratings[['uid', 'iid', 'rating']], reader=self.reader)
        cross_validate(self.algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)