import random
import json
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml.model import NeuralNet
from .ml.ntk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('chatapp/ml/intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "chatapp/ml/data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Nihar"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])

    return "I do not understand..."


@csrf_exempt
def chatapp_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("question", "")
        bot_reply = get_response(user_message)
        return JsonResponse({"response": bot_reply})

    return JsonResponse({"error": "Invalid request"}, status=400)
