import numpy as np   
from sklearn.linear_model import LinearRegression
import pandas as pd    
from sklearn.model_selection import train_test_split
import csv

#print("running!")

df = pd.read_csv(r'coin_data.csv') #reads the csv file from the bot
#print(df.sample(10))
#print(df.dtypes)

X = df.drop(['profit', 'profit change'], axis=1) #creates the x data
y = df[['profit change']] #creates the y
# print(X.sample())
# print(y.sample())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=1) #splits into training and testing sets

regression_model = LinearRegression()
regression_model.fit(X_train, y_train) #builds model

print("the R^2 value for the model using the sample data is",regression_model.score(X_train, y_train))
print("the R^2 value for the model using the out of sample data is",regression_model.score(X_test, y_test))

sample_score = str(regression_model.score(X_train, y_train))
test_score = str(regression_model.score(X_test, y_test))
info = "the R^2 value for the model using the sample data is {} and the R^2 value for the model using the out of sample data is {}".format(sample_score, test_score)
# this just makes a file that allows you to see your R^2 for the model created
f = open("model info.txt", "w")
f.write(info)
f.close()

model_coef = []
for idx, col_name in enumerate(X_train.columns): #grabs the coefficients of the linear function
    model_coef.append(regression_model.coef_[0][idx])
    #print("The coefficient for {} is {}".format(col_name, regression_model.coef_[0][idx]))
    
with open('regression.csv','w') as f: #adds the coefficients to a file that the bot grabs
    write = csv.writer(f) 
    write.writerow(model_coef) 
