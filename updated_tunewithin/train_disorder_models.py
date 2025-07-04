import numpy as np
from keras.models import Sequential
from keras.layers import GRU, Dense, Masking
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import os

# Step 1: Simulate mood time-series data (e.g., mood over 7 days)
def generate_data(samples=1000, timesteps=7):
    np.random.seed(42)
    moods = [-1, 0, 1]  # sad, neutral, happy
    data = []
    labels = []
    for _ in range(samples):
        sequence = np.random.choice(moods, size=timesteps)
        data.append(sequence)

        # Label rule: mostly negative -> Depression, high variance -> Bipolar, mostly anxious -> GAD
        if np.mean(sequence) < -0.3:
            labels.append("Depression")
        elif np.std(sequence) > 0.9:
            labels.append("Bipolar")
        elif ((-0.3 < np.mean(sequence) < 0.2) and (0.4 < np.std(sequence) < 0.9 )):
            labels.append("GAD")
        else:
            labels.append("NA")
    return np.array(data), np.array(labels)

# Step 2: Prepare data
X, y = generate_data()
X = X.reshape((X.shape[0], X.shape[1], 1))
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_cat = to_categorical(y_encoded)

# Step 3: Train GRU model
gru_model = Sequential([
    Masking(mask_value=0.0, input_shape=(X.shape[1], 1)),
    GRU(32, return_sequences=False),
    Dense(4, activation='softmax')
])
gru_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
gru_model.fit(X, y_cat, epochs=10, batch_size=32, validation_split=0.2)

# Save GRU model
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "ml_models")

if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_path = os.path.join(model_dir, "gru_disorder.h5")
gru_model.save(model_path)

print(f"✅ GRU model trained and saved at: {model_path}")
