#%%

import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression



def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

z = np.arange(-7,7,0.1)
phi_z = sigmoid(z)
plt.plot(z, phi_z)
# axvline adds a vertical line across the axes, the parameter specifies the color of the vertical line
# in matplotlib 'k' stands for black. 
# the 0.0 specifies that x coodinate where the vertical line will be placed. 
plt.axvline(0.0, color='k')

# the command plt.ylim(-0.1,1.1) is used to set the limits of the y-axis on a plot generated by matplotlib's pyplot module
plt.ylim(-0.1,1.1)
plt.xlabel('z')
plt.ylabel('$\phi (z)$')

# y axis ticks and gridline 
plt.yticks([0.0,0.5,1])

#gca stands for 'get current axis' it retrieves the current axes instance of the current figure matching the current subplot specification, or creates one if it doesn't exist
# this object contains info about the plot, such as the x-axis, y-axis, title, x and y labels, and more. by getting access to the current axes you can modify it directly plus customize your plot further
ax=plt.gca()

#ax.yaxis.grid(True) enables the grid lines for the y-axis of the plot. The 'yaxis' attribute of the Axes object accesses the yaxis instance, and 
# the 'grid' method controls whether grid lines are visible. 
ax.yaxis.grid(True)
plt.tight_layout()
plt.show()

# %%
# Below is a short code snippet to create a plot that illustrates teh cost of classifying a single training exmaple for
# for different values of phi_z


# def cost_1(z):
#     return 1 - np.log(sigmoid(z))

# def cost_0(z):
#     return - np.log(1 - sigmoid(z))

# z = np.arange(-10,10,0.1)
# phi_z = sigmoid(z)

# c1= [cost_1(x) for x in z]
# plt.plot(phi_z, c1, label='J(w) if y=1')

# c0 = [cost_0(x) for x in z]

# plt.plot(phi_z, c0, linestyle='--', label= 'J(w) if y=0')

# plt.ylim(0.0, 5.1)
# plt.xlim([0,1])
# plt.xlabel('$\phi$(z)')
# plt.ylabel('J(w)')
# plt.legend(loc='best')
# plt.tight_layout()
# plt.show()


# %%
class LogisticRegressionGD(object):
    """
    Logistic Regression Classifier using gradient descent
    
    Parameters
    -----------
    eta: float
         Learning rate/step size (between 0.0 and 1.0)
         
    n_iter: int
            Passes over the training dataset
            
    random_state: int
                  Random number generator seed for random weight initialization. 
                  
    
    Attributes
    ----------
    w_: 1d-array
        weights after fitting. 
        
    cost_: list 
           Logistic cost function value in each epoch
    """
    
    def __init__(self, eta=0.05, n_iter=100, random_state=1):
        self.eta = eta
        self.n_iter = n_iter
        self.random_state = random_state
        
        
    def fit(self, X, y):
        """Fit the training data.
        
        Parameters
        ----------
        X: {array-like}, shape = [n_examples, n_features]
            Training vectors, where n_examples is the number of examples and n_features is the number of features. 
            
        y:  array-like, shape =[n_examples]
            Target values. 
            
        Returns
        -------
        self : object
        """
        
        # create a new random number generator
        rng = np.random.default_rng(self.random_state)
        # The line below generates an array of normally distributed random numbers (gaussion distribution)
        # with mean (loc) of 0.o and standard deviation (scale) = 0.01. The size of teh array is 1 + X.shape[1],
        # X.shape[1] is the number of features or columns in X. The '+1' part is likely accounting for a bias unit or intercept term in teh weight array
        
        self.w_ = rng.normal(loc = 0.0, scale=0.01, size =1+ X.shape[1])
        self.cost_= []
        
        for i in range(self.n_iter):
            net_input = self.net_input(X)
            output = self.activation(net_input)
            
            errors = (y - output )
            
            self.w_[1:] += self.eta * X.T.dot(errors)
            self.w_[0] += self.eta * errors.sum()
            
            # note that we compute the logistic 'cost' now 
            # instad of the sum of squared errors cost
            
            cost = (-y.dot(np.log(output)) - ((1-y).dot(np.log(1-output))))
            self.cost_.append(cost)
            
            
            
            
        return self
        
    def net_input(self,X):
        """Calculate net input"""
        return np.dot(X, self.w_[1:]) + self.w_[0]
    
    def activation(self, z):
        """Compute logistic sigmoid activation"""
        
        # 'np.exp(-np.clip(z,-250,250))' calculates the exponential of '-z', but before 
        # doing so, it 'clips' the value of 'z' to be within the range of '-250' to '250'. 
        # clipping is done to avoid overflow errors in the exponential function, which can occur if 
        # 'z' is too large or too small when passed to the np.exp function. 
        return 1. / (1. + np.exp(-np.clip(z,-250,250)))
    
    
    def predict(self, X):
        """Return class label after unit step"""
        
        return np.where(self.net_input(X) >= 0.0, 1, 0)
    # equivalent to:
    # return np.where(self.activation(self.net_input(X)) >= 0.5, 1, 0) 
    
    
    
    
    
# load the data
data = pd.read_excel('CleanedData.xlsx')
#
# Assuming 'X' are all columns except the target variable and 'y' is teh target variable

X = data.drop('SeriousDlqin2yrs', axis=1).values

y=data['SeriousDlqin2yrs'].values
# print first 5 
# print(X[0:5])
# print(y[0:5])


# split up our dataset into training and testing, with 20% of the dataset being used for training 
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3, random_state=13)

# count the number of 0's and 1's in the test target variable
count_ones = np.count_nonzero(y_test)
count_zeros = y_test.size - count_ones

print(f"Number of 1's: {count_ones}")
print(f"Number of 0's: {count_zeros}")

# Perform feature scaling 
scaler = StandardScaler()
# when you scale the training data, you calculate the mean and standard deviation of this data. 

# standardScaler().fit_transform(X_train), computes the mean and standard deviation of X_train for each feature, 
# and then uses these statistics to scale the training data by subtracting the mean from each feautre and dividing by the standard deviation
# This process transforms each feature in your data to have mean 0 and standard deviation 1, which helps gradient descent to converge more quickly
# and also ensures that all features contribute equally to teh distance computations in algorithms that are sensitive to the scale of the data (like K-NN or SVM)


X_train = scaler.fit_transform(X_train)
# when you scale the test data, you shoud use the same mean and standard deviation that wer ecomputed from teh training data. 
# StandardScaler().transform(X_test), applies the previously computed mean and standard deviaiaton from teh training data to the test data. 
# This is crucial becauase the scaling parameters (mean and standard deviation ) are part of the model you created and learned from the training data. 
# if you were to re-calculate the mean and standard deviation from the test data, it would introduce a data leak where information from the test set influences the model, 
# leading to overly optimistic performance estimates. 
# by using the training data's scaling parameters, you are ensuring that the model is being evaluated ont the same scale as the scale it was trained on, which is a fair assessment of its performance on new data. 

X_test = scaler.transform(X_test)

# Initialize and train the logisticRegressionGD model

model= LogisticRegressionGD(eta=0.05, n_iter =100, random_state=2)


model.fit(X_train, y_train)

# After training we can now make predicitions and evaluate the model
# predictions = model.predict(X_test)


def accuracy(y_true, y_pred):
    correct_count = (y_true == y_pred).sum()
    accuracy = correct_count/ len(y_true)
    return accuracy

y_pred = model.predict(X_test)

# cakculate the accuracy 
acc= accuracy(y_test, y_pred)
print(f"Accuracy: {acc:.3f}")


lr = LogisticRegression(C=100.0, random_state=1, solver='lbfgs')

sklearn_ypred =lr.fit(X_train, y_train)
lr.predict(X_test)
sklearn_acc = accuracy(y_test, sklearn_ypred)
print(f'Sk learn Accuracy:{acc:.3f}')




# %%
