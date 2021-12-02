#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.utils import as_float_array
import seaborn as sns
from sklearn.linear_model import LinearRegression, RidgeCV, Ridge, Lasso, LassoCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.ensemble import AdaBoostRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error

get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')


# In[12]:


def load_data(file):
    data = pd.read_csv(file)
    return data

file = "2016_519.csv"
my_data = load_data(file)

data_backup = my_data


# In[13]:


def transform_data(data):
    data = data.dropna(axis = 0)
    data['date'] = pd.to_datetime(data['date'])
    data['Year'] = data['date'].dt.year
    data['Month'] = data['date'].dt.month
    data['Day'] = data['date'].dt.day
    data['DayOfWeek'] = data['date'].dt.day_name()
    data = data[data.AVG_WIND != 'Unknown']
    data['AVG_WIND'] = as_float_array(data['AVG_WIND'])
    lb = LabelEncoder() 
    data['FOG'] = lb.fit_transform(data['FOG'])
    data['THUNDER'] = lb.fit_transform(data['THUNDER'])
    data['ICE'] = lb.fit_transform(data['ICE'])
    data['HAIL'] = lb.fit_transform(data['HAIL'])
    data['HAZE_SMOKE'] = lb.fit_transform(data['HAZE_SMOKE'])
    data['BLW_SNOW'] = lb.fit_transform(data['BLW_SNOW'])
    data['HIGH_WIND'] = lb.fit_transform(data['HIGH_WIND'])
    data['DRIZZLE'] = lb.fit_transform(data['DRIZZLE'])
    data['RAIN'] = lb.fit_transform(data['RAIN'])
    data['SNOW'] = lb.fit_transform(data['SNOW'])
    data = pd.get_dummies(data, columns = ['DayOfWeek'])
    return data

df1 = transform_data(my_data)


# In[14]:


df1 = df1.drop(columns = ['date', 'Year', 'weatherHour', 'weatherDate'])
df1.isnull().values.any()


# In[15]:


X = df1[['hour', 'start_station_id', 'AVG_WIND', 'PRECIP', 'SNOW_TOTAL', 'MAX_TEMP', 'Month',
         'DayOfWeek_Saturday', 'DayOfWeek_Sunday']]

y = df1['count']

scale = StandardScaler()
X_scaled = scale.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size = 0.30, random_state = 42)


# In[16]:


model = AdaBoostRegressor(n_estimators = 100)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("MSE: %.2f" % mse)
print("RMSE: %.2f" % np.sqrt(mse))
print("R2: %.2f" % model.score(X_test, y_test))


# In[ ]:




