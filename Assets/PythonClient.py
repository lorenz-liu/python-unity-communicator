import socket
import openai
from dotenv import load_dotenv
import os
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image as PILImage
import requests
import numpy as np


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 12345        # Port to listen on

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    try:
        server_socket.bind((HOST, PORT))
    except OSError:
        print('Continue using port', PORT)
    
    server_socket.listen()
    print(f"Listening on {HOST}:{PORT}")

    while True:
        connection, address = server_socket.accept()
        with connection:
            print(f"Connected by {address}")
            data = connection.recv(1024)
            if not data:
                break
            # Process the received data from Unity
                
            print(f"Received data from Unity: {data.decode()}")

            SOURCE_IMAGE_URL = "https://cdn7.dissolve.com/p/D2115_143_759/D2115_143_759_1200.jpg"
            CARTOON_SIZE = "1024x1024"

            # BELOW: RESNET
            image = PILImage.open(requests.get(SOURCE_IMAGE_URL, stream=True).raw).convert('RGB')

            processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
            model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

            inputs = processor(images=image, return_tensors="pt")
            outputs = model(**inputs)

            # convert outputs (bounding boxes and class logits) to COCO API
            # let's only keep detections with score > 0.9
            target_sizes = torch.tensor([image.size[::-1]])
            results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                box = [round(i, 2) for i in box.tolist()]
                print(
                    f"Detected {model.config.id2label[label.item()]} with confidence "
                    f"{round(score.item(), 3)} at location {box}"
                )

            max_index = torch.argmax(results['scores']).item()
            max_confidence = model.config.id2label[results["labels"][max_index].item()]

            print("\nTherefore, we select the object with max confidence to generate cartoon:", max_confidence)

            # BELOW: OPENAI

            load_dotenv()
            openai.api_key = os.getenv("OPENAI_API_KEY") # You have to get your own OpenAI API Key

            print("This is to generate this cartoon:", max_confidence)

            response = openai.Image.create(
                prompt="draw a cute, delightful, colorful, and single cartoon character of " + max_confidence, # Modify the prompt based on your intention
                n=1,
                size=CARTOON_SIZE
            )

            image_url = response['data'][0]['url']

            print("Generated Cartoon URL:", image_url)
            print("\n======================================================================================================================\n")

            # Send a response back to Unity
            connection.sendall(image_url.encode('utf-8'))
