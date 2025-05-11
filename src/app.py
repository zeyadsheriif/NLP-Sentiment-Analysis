from flask import Flask, request, jsonify, render_template
from transformers import BertTokenizer, BertForSequenceClassification
import torch

model_path = "bert_model"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    confidence = None

    if request.method == "POST":
        text = request.form.get("text")

        if text:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1)
                predicted_class = torch.argmax(probs).item()

            prediction = "Positive 😊" if predicted_class == 1 else "Negative 😠"
            confidence = round(probs[0][predicted_class].item() * 100, 2)

    return render_template("index.html", prediction=prediction, confidence=confidence)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No input text provided."}), 400

    inputs = tokenizer(data["text"], return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=1)
        predicted_class = torch.argmax(probs).item()

    sentiment = "positive" if predicted_class == 1 else "negative"
    confidence = round(probs[0][predicted_class].item(), 4)

    return jsonify({"prediction": sentiment, "confidence": confidence})

if __name__ == "__main__":
    app.run(debug=True)

