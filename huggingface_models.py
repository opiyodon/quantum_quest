from transformers import pipeline

# Initialize Hugging Face pipelines
text_generator = pipeline("text-generation", model="gpt2")
image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
audio_classifier = pipeline("audio-classification", model="superb/hubert-large-superb-er")
video_classifier = pipeline("video-classification", model="microsoft/resnet-50")