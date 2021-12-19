# project: p7
# submitter: yeo9
# partner: none
# hours: 20


import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_transformer
from sklearn.model_selection import cross_val_score


class UserPredictor():
    def __init__(self):
        self.model = Pipeline([("poly", make_column_transformer((OneHotEncoder(), ["badge"]),
                                                             (OneHotEncoder(handle_unknown = "ignore"), ['url']), #ignore zeros in url column
                                                             (PolynomialFeatures(degree = 2,include_bias=False), ["avg_min"]),
                                                             (PolynomialFeatures(degree = 2,include_bias=False), ["total_min"]),
                                                             (PolynomialFeatures(degree = 2,include_bias=False), ["url_counts"]),
                                                             remainder = "passthrough")),
                             ("std", StandardScaler()),
                             ("lr", LogisticRegression(fit_intercept=False,max_iter = 1000))
                              ])
        self.xcol = ["age", "badge", "past_purchase_amt", "avg_min", "url_counts", "total_min", "url"]


    def fit_df(self,train_users, train_logs, train_y):
        train_logs['minutes'] = train_logs['seconds'] / 60
        train_y['target'] = train_y['y'].astype(int)
        
        df1 = train_logs.groupby('user_id')['minutes'].agg(["mean"]) #average mins on url
        df2 = train_logs.groupby('user_id')['url'].agg(['count']) #the number of visited urls
        df3 = train_logs.groupby('user_id')['minutes'].agg(["sum"]) #total mins on url
        stats = pd.merge(df1, df2, on = "user_id")
        final_stats = pd.merge(stats, df3, on = "user_id")
        #train_users + stats
        user_stats = pd.merge(train_users, final_stats, on = "user_id")
        #url with the maximum seconds
        visited_url = train_logs.sort_values(by = "minutes").drop_duplicates(subset="user_id",keep="last").sort_values(by="user_id")[['user_id',"url"]]
        #stats+url
        stats_url = pd.merge(user_stats, visited_url, on = "user_id")
        #final_df
        final_df = pd.merge(stats_url, train_y[['user_id', 'target']], on = 'user_id')
        final_df = final_df.rename(columns = {"mean":"avg_min", "count":"url_counts", "sum":"total_min"})
        return final_df
        
    def predict_df(self, test_users, test_logs):
        test_logs['minutes'] = test_logs['seconds'] / 60
        
        df1 = test_logs.groupby('user_id')['minutes'].agg(["mean"])
        df2 = test_logs.groupby('user_id')['url'].agg(['count']) #the number of visited urls
        df3 = test_logs.groupby('user_id')['minutes'].agg(["sum"])

        stats = pd.merge(df1, df2, on = "user_id")
        final_stats = pd.merge(stats, df3, on = "user_id")

        user_stats = pd.merge(test_users, final_stats, on = "user_id", how = "outer").fillna(0)
        visited_url = test_logs.sort_values(by = "minutes").drop_duplicates(subset="user_id",keep="last").sort_values(by="user_id")[['user_id',"url"]]
        stats_url = pd.merge(user_stats, visited_url, on = "user_id", how = "outer").fillna(0)
        stats_url = stats_url.rename(columns = {"mean":"avg_min", "count":"url_counts", "sum":"total_min"})
        return stats_url
    
    def fit(self,train_users, train_logs, train_y):
        train = self.fit_df(train_users, train_logs, train_y)
        output = self.model.fit(train[self.xcol], train['target'])
        return output
    
    def predict(self, test_users, test_logs):
        test = self.predict_df(test_users, test_logs)
        prediction = self.model.predict(test[self.xcol])
        return prediction