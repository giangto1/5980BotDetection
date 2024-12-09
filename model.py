
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

df = pd.read_csv('bot_detection_data.csv')
df.head()

# preprocessing: turning categorical variables into numerical representations
df = df.fillna(0)
df['Verified'] = df['Verified'].astype(int)
df['Hashtag Count'] = df['Hashtags'].apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)
features = ['Follower Count', 'Retweet Count', 'Mention Count', 'Verified', 'Hashtag Count']
X = df[features]  # Feature matrix
X = df[features]  # Feature matrix
y = df['Bot Label']  # Target variable (0 = human, 1 = bot)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")

rf_model = RandomForestClassifier(max_depth=100, n_estimators=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"model accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# importances = rf_model.feature_importances_
# for feature, importance in zip(features, importances):
#     print(f"{feature}: {importance:.4f}")