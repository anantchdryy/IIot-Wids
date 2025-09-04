import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import numpy as np 
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from collections import Counter
from focal_loss import SparseCategoricalFocalLoss

df = pd.read_csv(r'C:\Google AI hackathon\IIoT_Malware_Timeseries_CLEAN.csv')
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex = False)
df2 = df.drop(['timestamp', 'protocol_type', 'flags'], axis = 1)
X = df2.drop('label', axis = 1)
y = df2['label']
categorical_features = X.select_dtypes(include=['object']).columns.tolist()

if categorical_features: #categorial variables
    le = LabelEncoder()
    X_processed = X.copy()
    for col in categorical_features:
        X_processed[col] = le.fit_transform(X_processed[col].astype(str))
    X = X_processed

#handling the missing and infinite values
if X.isnull().sum().sum() > 0:
    imputer = SimpleImputer (strategy= 'median')
    X = pd.DataFrame(imputer.fit_transform(X), columns= X.columns)
if np.isinf(X.select_dtypes(include= [np.number])).sum().sum()>0:
    X= X.replace([np.inf, -np.inf], np.nan)
    if X.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy= 'median')
        X = pd.DataFrame(imputer.fit_transform(X), columns = X.columns)

#splitting into train test data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify= y, random_state= 42)

#smote oversampling 

smote= SMOTE(random_state= 42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

#standard scaling 
scaler = StandardScaler()
X_train_res = scaler.fit_transform(X_train_res)
X_test = scaler.transform(X_test)

#label encode targeting 
le_y = LabelEncoder()
y_train_enc = le_y.fit_transform(y_train_res)
y_test_enc = le_y.transform(y_test)
num_classes = len(le_y.classes_)


#compute class weights for cost sensitive learning 

y_train_enc = np.array(y_train_enc).flatten()

# recompute counter safely
counter = Counter(y_train_enc)
max_count = max(counter.values())

# ensure all values are floats, not dicts
class_weights = {int(cls): float(max_count) / float(num) for cls, num in counter.items()}

print("Final class_weights:", class_weights)


#starting with deep learning, define deep learning

def make_model(input_dim, num_classes, hp=None):
    n_hidden = int(hp['n_hidden'])
    dropout = float(hp['dropout'])
    lr = float(hp['lr'])
    gamma = float(hp['gamma'])

    model = keras.Sequential()
    model.add(layers.Input(shape=(input_dim,)))
    model.add(layers.Dense(n_hidden, activation='relu'))
    model.add(layers.Dropout(dropout))
    model.add(layers.Dense(num_classes, activation='softmax'))
    loss_fn = SparseCategoricalFocalLoss(gamma=gamma)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss=loss_fn,
        metrics=['accuracy']
    )
    return model

#hyperparameter space for bayesian optimization 

from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
def objective(hp_params):
    # Directly use the values, but ensure they are the correct type
    n_hidden = int(hp_params['n_hidden'])
    dropout = float(hp_params['dropout'])
    lr = float(hp_params['lr'])
    gamma = float(hp_params['gamma'])

    model = keras.Sequential()
    model.add(layers.Input(shape=(X_train_res.shape[1],)))
    model.add(layers.Dense(n_hidden, activation='relu'))
    model.add(layers.Dropout(dropout))
    model.add(layers.Dense(num_classes, activation='softmax'))

    # Use a simpler loss function for the hyperparameter search
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Train a small amount and evaluate
    history = model.fit(
        X_train_res, y_train_enc,
        epochs=1,  # Train for only 1 epoch to speed up search
        batch_size=int(hp_params['batch_size']),
        verbose=0,
        validation_split=0.2
    )

    # Get the validation loss from the history object
    val_loss = history.history['val_loss'][-1]
    
    return {'loss': val_loss, 'status': STATUS_OK}

search_space = {
    'n_hidden': hp.quniform('n_hidden', 64, 512, 16),
    'dropout' : hp.uniform('dropout', 0.2, 0.5),
    'lr': hp.loguniform('lr', np.log(1e-4), np.log(1e-2)),
    'batch_size': hp.quniform('batch_size', 32, 128, 16),
    'gamma' : hp.uniform('gamma', 1.0, 3.0)
}

trials = Trials()
best_hp = fmin(objective, search_space, algo = tpe.suggest, max_evals= 30, trials=trials)
print('Best hyperparametes have been found', best_hp)

#final model training with the hyperparameters

best_hp_clean = {
    'n_hidden': int(best_hp['n_hidden']),
    'batch_size': int(best_hp['batch_size']),
    'dropout': float(best_hp['dropout']),
    'lr': float(best_hp['lr']),
    'gamma': float(best_hp['gamma'])
}

print("Cleaned best_hp:", best_hp_clean)



final_model = make_model(X_train_res.shape[1], num_classes, best_hp_clean)
print("Type of best_hp_clean['batch_size'] before fit:", type(best_hp_clean['batch_size']))
print("Value of best_hp_clean['batch_size'] before fit:", best_hp_clean['batch_size'])
final_model.fit(
    X_train_res, y_train_enc,
    epochs=50,
    batch_size=int(best_hp_clean['batch_size']),
    class_weight = class_weights,
    verbose=1,
    validation_split=0.2,
    callbacks=[EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)]
)

#evaluation

y_pred = np.argmax(final_model.predict(X_test), axis = 1)
print(classification_report(y_test_enc, y_pred, target_names=le_y.classes_ ))
print(confusion_matrix(y_test_enc, y_pred))
print(f"Test of F1 Macro: {f1_score(y_test_enc, y_pred, average = 'macro'):.4f}")
print(f"f1 test weighted {f1_score(y_test_enc, y_pred, average='weighted'):.4f}")
