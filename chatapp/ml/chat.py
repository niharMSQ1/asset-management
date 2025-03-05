import random
import json
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .model import NeuralNet
from .ntk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents
with open('chatbot/ml/intents.json', 'r') as json_data:
    intents = json.load(json_data)

# Load model
FILE = "chatbot/ml/data.pth"
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

bot_name = "H"

def get_response(msg):
    """Returns a chatbot response based on the user's message."""
    
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:  # Confidence threshold
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])

    return "I'm sorry, but I cannot provide guidance on that. Please refer to official HIPAA guidelines."

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            questions = data.get("questions", [])  # Accept multiple questions
            
            if not isinstance(questions, list):
                return JsonResponse({"error": "Invalid format. 'questions' must be a list."}, status=400)

            responses = {q: get_response(q) for q in questions}  # Process all questions
            
            return JsonResponse({"responses": responses})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
