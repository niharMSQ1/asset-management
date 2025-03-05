# Chatbot using PyTorch and Django

This project implements a chatbot using PyTorch for the machine learning model and Django for serving the chatbot via an API. The chatbot is trained on a custom dataset (`intents.json`) and can provide responses to user inputs based on intent classification.

## Project Structure

### 1. `views.py`
This file defines the Django view for handling chatbot API requests. It uses the trained PyTorch model to process user inputs and return chatbot responses.

**Key Functions:**
- `get_response(msg)`: 
  - Tokenizes the input message.
  - Converts the tokenized message into a bag-of-words vector.
  - Passes the vector through the trained neural network model to predict the intent.
  - Retrieves a random response from the predicted intent if confidence is above 75%; otherwise, returns a fallback message.
- `chatapp_response(request)`:
  - Handles POST requests to receive user messages and respond with the chatbot's reply.

---

### 2. `train.py`
This script is used to train the chatbot's neural network model using data from `intents.json`.

**Steps in Training:**
1. **Data Preparation:**
   - Loads and processes `intents.json` to extract patterns and tags.
   - Tokenizes the patterns and applies stemming.
   - Creates a bag-of-words representation for training data.

2. **Model Training:**
   - Defines a `NeuralNet` model with an input layer, two hidden layers, and an output layer.
   - Trains the model using the `CrossEntropyLoss` loss function and `Adam` optimizer for 6000 epochs.

3. **Saving the Model:**
   - After training, the model's state and metadata (e.g., `input_size`, `hidden_size`, `tags`) are saved to `data.pth`.

---

### 3. `ntk_utils.py`
This file contains utility functions for preprocessing text.

**Functions:**
- `tokenize(sentence)`: Splits a sentence into tokens (words).
- `stem(word)`: Reduces a word to its root form using Porter Stemming.
- `bag_of_words(tokenized_sentence, words)`: Converts a tokenized sentence into a bag-of-words vector based on the vocabulary.

---

### 4. `model.py`
Defines the neural network model (`NeuralNet`) used for intent classification.

**Model Architecture:**
- Input Layer: Takes the bag-of-words vector.
- Hidden Layers: Two fully connected layers with ReLU activation.
- Output Layer: Outputs probabilities for each intent tag.

---

### 5. `chat.py`
Similar to `views.py`, this file demonstrates an alternative implementation of the chatbot response logic. It processes multiple questions in a single API call.

**Key Features:**
- Processes a list of questions in a single request.
- Returns responses for all questions in a dictionary format.

---

### 6. `intents.json`
This file contains the dataset for training the chatbot. 

**Structure:**
- `tag`: The label for an intent.
- `patterns`: Example sentences that represent the intent.
- `responses`: Possible replies for the intent.

**Example:**
```json
{
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["Hello", "Hi", "How are you?"],
      "responses": ["Hello!", "Hi there!", "I'm doing fine, thank you!"]
    },
    {
      "tag": "goodbye",
      "patterns": ["Bye", "See you later", "Goodbye"],
      "responses": ["Goodbye!", "Take care!", "See you later!"]
    }
  ]
}
