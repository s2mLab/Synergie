import keras
from keras import layers

def lstm():
    temporal_input = keras.Input(shape=(180, 10), name='temporal_input')
    x = layers.BatchNormalization()(temporal_input)
    x = keras.layers.LSTM(128, return_sequences=True)(x)
    x = keras.layers.LSTM(64)(x)
    x = keras.layers.Dropout(0.4)(x)
    x = keras.layers.Dense(64, activation='relu')(x)
    x = keras.layers.Dropout(0.4)(x)
    x = keras.layers.Dense(16, activation='relu')(x)

    scalar_input = keras.Input(shape=(2,), name='scalar_input')  # Ex: masse et taille
    y = layers.Dense(16, activation='relu')(scalar_input)

    combined = layers.concatenate([x, y])

    z = layers.Dense(16, activation="relu")(combined)
    z = keras.layers.Dropout(0.2)(combined)
    outputs = keras.layers.Dense(2, activation='softmax')(z)

    optimizer = keras.optimizers.Adam(learning_rate=0.00001)

    model = keras.Model([temporal_input, scalar_input], outputs)

    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

#
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Normalization and Attention
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = x + inputs

    # Feed Forward Part
    x = layers.LayerNormalization(epsilon=1e-6)(res)
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    return x + res


def transformer(
        input_shape=(240, 10),
        head_size=256,
        num_heads=4,
        ff_dim=4,
        num_transformer_blocks=4,
        mlp_units=128,
        dropout=0,
        mlp_dropout=0,
):
    n_classes = 6

    temporal_input = keras.Input(shape=input_shape, name="temporal_input")
    x = layers.BatchNormalization()(temporal_input)
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)

    x = layers.GlobalAveragePooling1D(data_format="channels_first")(x)
    x = layers.Dense(mlp_units, activation="relu")(x)
    x = layers.Dropout(mlp_dropout)(x)
    x = layers.Dense(16, activation="relu")(x)
    
    scalar_input = keras.Input(shape=(2,), name='scalar_input')  # Ex: masse et taille
    y = layers.Dense(16, activation='relu')(scalar_input)

    combined = layers.concatenate([x, y])
    
    z = layers.Dense(16, activation="relu")(combined)
    z = layers.Dropout(0.2)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(z)

    optimizer = keras.optimizers.Adam(learning_rate=0.00005)

    model = keras.Model([temporal_input, scalar_input], outputs)

    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    return model

def transformerTraining(hp):
    input_shape = (240, 10)
    head_size = hp.Int('head_size', min_value=32, max_value=512, step=32)
    num_heads = hp.Int('num_heads', min_value=2, max_value=16, step=2)
    ff_dim = hp.Int('ff_dim', min_value=128, max_value=2048, step=128)
    num_transformer_blocks = hp.Int('num_transformer_blocks', min_value=1, max_value=12, step=1)
    mlp_units = 128
    dropout = 0.3
    mlp_dropout = 0.1
    n_classes = 6
    learning_rate = 0.00005

    inputs = keras.Input(shape=input_shape)
    x = layers.BatchNormalization()(inputs)
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)

    x = layers.GlobalAveragePooling1D(data_format="channels_first")(x)
    x = layers.Dense(mlp_units, activation="relu")(x)
    x = layers.Dropout(mlp_dropout)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)
    model = keras.Model(inputs, outputs)

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    return model

def save_model(model, path="saved_models/model.keras"):
    keras.saving.save_model(model, path, overwrite=True)


def load_model(path="saved_models/model.keras"):
    return keras.saving.load_model(path)
