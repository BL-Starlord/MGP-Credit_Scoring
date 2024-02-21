#%% Importing Dataset
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#!Row65 change randomforest hyperparameter
#!Row 141 change XGB hyperparameter
#%% Input/Output modification
#! Change all these before running the code
#The filename for the data
inputfile = 'CleanedData4.xlsx'
#The file name to store the xbg regressor for NumberOfDependents imputation
regressor_NOD_filename = 'xgb_regressor_NOD_CleanedData4.joblib'
#The file name to store the parameter used for NumberOfDependents imputation
xgb_train_parameter_NOD_filename = 'xgb_train_parameter_NOD_CleanedData4.joblib'
#The file name to store the xbg regressor after Monthly Income imputation
regressor_MI_filename = 'xgb_regressor_MI_CleanedData4.joblib'
#The file name to store the parameter used for Monthly Income imputation
xgb_train_parameter_MI_filename = 'xgb_train_parameter_MI_CleanedData4.joblib'
#Imputed data filename
imputeddata_filename =  "Imputed_Cleaneddata4.xlsx" 

#%% Load the original data into a DataFrame

if inputfile.split('.')[-1] == 'csv':
    df = pd.read_csv(inputfile)
else:
    df = pd.read_excel(inputfile, engine='openpyxl')

# Rename the first column to "Index"
df.rename(columns={df.columns[0]: "Index"}, inplace=True)

#%% Exploratory analysis
# Check for missing values in each column
missing_values = df.isna().sum()
print(missing_values)
# %% Plot the boxplots for ones that contains NA values

# Identify columns with missing values
columns_with_missing_values = missing_values[missing_values > 0].index.tolist()

# Generate boxplots for columns with missing values
for column in columns_with_missing_values:
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=df[column])
    plt.title(f'Boxplot of {column}')
    plt.show()


# %% Predict NumberOfDependents column using the dataset without MonthlyIncome and SeriousDlqin2yrs

# create a dataset for predicting NumberOfDependents
df_1 = df.drop(columns=[ 'MonthlyIncome','SeriousDlqin2yrs'])

# Check for missing values in each column
#missing_values = df_1.isna().sum()
#print(missing_values)

# %% Seperate the dataset with dependents unknown and dependents known

# DataFrame with rows where NumberOfDependents is not NA
df_with_dependents = df_1.dropna(subset=['NumberOfDependents'])
#missing_values = df_with_dependents.isna().sum()
#print(missing_values)

# DataFrame with rows where NumberOfDependents is NA
df_missing_dependents = df_1[df_1['NumberOfDependents'].isna()]
#missing_values = df_missing_dependents.isna().sum()
#print(missing_values)

#%% start training the random forest
#! The hyperparameter is random_state

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV

import xgboost as xgb
from joblib import load,dump #?used for saving model hyperparameters

#%% Load previously trained model
xgb_regressor_prev = load(regressor_NOD_filename)

xgb_best_parameters = load(xgb_train_parameter_NOD_filename)

print(f"The hyperparameters for the previous model are: {xgb_best_parameters}")

#%% xgb model training

X = df_with_dependents.drop(['NumberOfDependents','Index'], axis=1)  # Features
y = df_with_dependents['NumberOfDependents']  # Target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

param_grid = {
    'n_estimators': [400,500],
    'learning_rate': [0.01],
    'max_depth': [3, 5],
    'colsample_bytree': [ 0.8,1.0],
    'subsample': [0.6, 0.7]
}

#! max_depth: Maximum Depth of a Tree: The depth of a tree is the length of the longest path from the root node down to a leaf node. A tree with a depth of 3 means that there are at most three levels of nodes, including the root node.
#! The colsample_bytree parameter in XGBoost is a hyperparameter that specifies the fraction of features (columns) to be randomly sampled for each tree. Before constructing each tree in the model, XGBoost randomly selects a subset of the features based on the colsample_bytree value. This is part of the model's built-in feature selection method to prevent overfitting and to add more randomness to the model fitting process.

grid_search = GridSearchCV(
    estimator=xgb.XGBRegressor(objective='reg:squarederror', random_state=42),
    param_grid=param_grid,
    scoring='neg_mean_squared_error',
    cv=3,
    verbose=2,
    n_jobs=-1
)

#%%grid_search fit

grid_search.fit(X_train, y_train)

#%% New model Best parameter set
print("Best Hyper-parameters for training: ", grid_search.best_params_)
xgb_regressor =  grid_search.best_estimator_
#%% Model prediction

y_pred = xgb_regressor.predict(X_test) #New model
y_pred_prev = xgb_regressor_prev.predict(X_test) #Old model

#%%
# Compare two models
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'New Model Mean Squared Error: {mse}')
print("New Model Mean Absolute Error:", mae)
print("New Model R-squared:", r2)

mse = mean_squared_error(y_test, y_pred_prev)
mae = mean_absolute_error(y_test, y_pred_prev)
r2 = r2_score(y_test, y_pred_prev)
print(f'Old Model Mean Squared Error: {mse}')
print("Old Model Mean Absolute Error:", mae)
print("Old Model R-squared:", r2)


#%% save the trained model

# Save the model
#dump(xgb_regressor, regressor_NOD_filename)
# Save the best parameters
#dump(grid_search.best_params_, xgb_train_parameter_NOD_filename)

# %% 

# Prepare df_missing_dependents for prediction
# Ensure to drop the 'NumberOfDependents' column if it hasn't been dropped already
X_missing = df_missing_dependents.drop(['NumberOfDependents','Index'], axis=1)

# Use the trained model to predict 'NumberOfDependents' for the missing values dataset
predicted_dependents = xgb_regressor.predict(X_missing)

# You can then add these predictions back to df_missing_dependents if you want to fill the missing values
df_missing_dependents['NumberOfDependents'] = predicted_dependents

# Now df_missing_dependents contains the predicted values for 'NumberOfDependents'

df_imputed = df_missing_dependents

# %% now put the imputed values back into df

# Concatenate df_with_dependents and df_missing_dependents to get a complete DataFrame
df_incomplete_unordered = pd.concat([df_with_dependents, df_imputed])

# Sort df_complete by the "Index" column
df_incomplete_ordered = df_incomplete_unordered.sort_values(by="Index")

# Check for missing values in each column
#missing_values = df_complete_ordered.isna().sum()
#print(missing_values)

df_incomplete_ordered['MonthlyIncome'] = df.set_index('Index')['MonthlyIncome'].loc[df_incomplete_ordered['Index']].values

#missing_values = df_complete_ordered.isna().sum()
#print(missing_values)

df_2 = df_incomplete_ordered

# %% Seperate the dataset with dependents unknown and dependents known

df_with_MonthlyIncome = df_2.dropna(subset=['MonthlyIncome']) # DataFrame with rows where MonthlyIncome is not NA
df_missing_MonthlyIncome = df_2[df_2['MonthlyIncome'].isna()] # DataFrame with rows where MonthlyIncome is NA

#Seperate X and Y for model training
X = df_with_MonthlyIncome.drop(['MonthlyIncome','Index'], axis=1)  # Features
y = df_with_MonthlyIncome['MonthlyIncome']  # Target

#%% Load previously trained model
xgb_regressor_prev = load(regressor_MI_filename)
xgb_best_parameters = load(xgb_train_parameter_MI_filename)

print(f"The hyperparameters for the previous model are: {xgb_best_parameters}")



#%% xgb model training
# Splitting the data with known MonthlyIncome for training and validation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

y_pred_prev = xgb_regressor_prev.predict(X_test)

param_grid = {
    'n_estimators': [100, 500, 1000],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 7],
    'colsample_bytree': [0.7, 0.8, 1.0],
    'subsample': [0.7, 0.8, 1.0]
}

#! max_depth: Maximum Depth of a Tree: The depth of a tree is the length of the longest path from the root node down to a leaf node. A tree with a depth of 3 means that there are at most three levels of nodes, including the root node.
#! The colsample_bytree parameter in XGBoost is a hyperparameter that specifies the fraction of features (columns) to be randomly sampled for each tree. Before constructing each tree in the model, XGBoost randomly selects a subset of the features based on the colsample_bytree value. This is part of the model's built-in feature selection method to prevent overfitting and to add more randomness to the model fitting process.

grid_search = GridSearchCV(
    estimator=xgb.XGBRegressor(objective='reg:squarederror', random_state=42),
    param_grid=param_grid,
    scoring='neg_mean_squared_error',
    cv=3,
    verbose=2,
    n_jobs=-1
)

#%%grid_search fit

grid_search.fit(X_train, y_train)

#%% Best parameter set
print("Best Hyper-parameters for training: ", grid_search.best_params_)
xgb_regressor =  grid_search.best_estimator_

#%% Predict on the test set
y_pred = xgb_regressor.predict(X_test)

#%%
# Evaluate the trained model
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'New Model Mean Squared Error: {mse}')
print("New Model Mean Absolute Error:", mae)
print("New Model R-squared:", r2)

mse = mean_squared_error(y_test, y_pred_prev)
mae = mean_absolute_error(y_test, y_pred_prev)
r2 = r2_score(y_test, y_pred_prev)
print(f'Old Model Mean Squared Error: {mse}')
print("Old Model Mean Absolute Error:", mae)
print("Old Model R-squared:", r2)
#%% save the parameters 
#! only save it if you are 100% sure it's better than previous model
# Save the model
#dump(xgb_regressor, regressor_MI_filename)
# Save the best parameters
#dump(grid_search.best_params_, xgb_train_parameter_MI_filename)



# %% 
# Prepare df_missing_dependents for prediction
# Ensure to drop the 'NumberOfDependents' column if it hasn't been dropped already
X_missing = df_missing_MonthlyIncome.drop(['MonthlyIncome','Index'], axis=1)

# Use the trained model to predict 'NumberOfDependents' for the missing values dataset
predicted_MonthlyIncome = xgb_regressor.predict(X_missing)

# You can then add these predictions back to df_missing_dependents if you want to fill the missing values
df_missing_MonthlyIncome['MonthlyIncome'] = predicted_MonthlyIncome

# Now df_missing_dependents contains the predicted values for 'NumberOfDependents'

df_imputed = df_missing_MonthlyIncome

# %% now put the imputed values back

# Concatenate df_with_dependents and df_missing_dependents to get a complete DataFrame
df_complete_unordered = pd.concat([df_with_MonthlyIncome, df_imputed])

# Sort df_complete by the "Index" column
df_complete_ordered = df_complete_unordered.sort_values(by="Index")

# Check for missing values in each column
missing_values = df_complete_ordered.isna().sum()
print(missing_values)

df_3 = df_complete_ordered
# %%
df_3['SeriousDlqin2yrs'] = df['SeriousDlqin2yrs']

new_order =  [col for col in df]

df_3 = df_3[new_order]

df_3.to_excel(imputeddata_filename, index=False)

# %%
