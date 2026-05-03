"""
cnn_classifier.py — Loads trained MobileNet model and classifies leaf images.
The model file (crop_disease_model.h5) is trained on Google Colab and downloaded.
"""

import os
import numpy as np
from PIL import Image

# Suppress TensorFlow warnings (noisy on CPU-only machines)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf


# These MUST match exactly what you used during training in Colab
# Order matters — this is alphabetical, which is what ImageDataGenerator uses
CLASS_NAMES = [
    "corn_common_rust",
    "corn_northern_leaf_blight",
    "healthy",
    "potato_early_blight",
    "potato_late_blight",
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_leaf_mold",
    "wheat_leaf_rust",
    "wheat_septoria",
]

IMG_SIZE = 128  # Must match training size


class CropDiseaseClassifier:
    """
    Loads the trained CNN model and classifies leaf images.
    Returns disease label, confidence, and alternative predictions.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Step 1: Check the expected obvious path first
            expected_path = os.path.join(script_dir, "models", "crop_disease_model.h5")
            
            # Step 2: If not in the exact expected path, search recursively for ANY .h5 file
            if not os.path.exists(expected_path):
                print(f"[CNN] File not found at {expected_path}. Searching directories...")
                found_h5 = None
                for root, dirs, files in os.walk(script_dir):
                    for file in files:
                        if file.endswith(".h5"):
                            found_h5 = os.path.join(root, file)
                            break
                    if found_h5:
                        break
                
                if found_h5:
                    model_path = found_h5
                    print(f"[CNN] Automatically found alternative model file at: {model_path}")
                else:
                    raise FileNotFoundError(
                        f"Model file not found anywhere in {script_dir}\n"
                        f"Please ensure crop_disease_model.h5 is uploaded to the repository."
                    )
            else:
                model_path = expected_path

        print(f"[CNN] Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        print(f"[CNN] Model loaded successfully. Input shape: {self.model.input_shape}")

    def preprocess_image(self, image_path):
        """
        Load and preprocess a leaf image for the CNN.
        Resizes to 128x128 and normalizes pixel values to [0, 1].
        """
        img = Image.open(image_path).convert("RGB")
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img) / 255.0  # Normalize to [0, 1]
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array

    def predict(self, image_path, confidence_threshold=0.65):
        """
        Classify a leaf image.

        Args:
            image_path: path to the leaf photograph
            confidence_threshold: below this, flag as low confidence

        Returns:
            dict with keys:
                - disease: predicted disease label
                - confidence: float 0-1
                - is_confident: bool
                - alternatives: list of (disease, confidence) if low confidence
                - all_predictions: list of (disease, confidence) sorted by confidence
        """
        img_array = self.preprocess_image(image_path)
        predictions = self.model.predict(img_array, verbose=0)[0]

        # Get sorted indices by confidence (highest first)
        sorted_indices = np.argsort(predictions)[::-1]

        top_disease = CLASS_NAMES[sorted_indices[0]]
        top_confidence = float(predictions[sorted_indices[0]])

        is_confident = top_confidence >= confidence_threshold

        # Get top 3 alternatives if low confidence
        alternatives = []
        if not is_confident:
            for i in range(1, min(3, len(sorted_indices))):
                idx = sorted_indices[i]
                alternatives.append({
                    "disease": CLASS_NAMES[idx],
                    "confidence": float(predictions[idx]),
                })

        # All predictions for debugging/display
        all_predictions = []
        for idx in sorted_indices:
            all_predictions.append({
                "disease": CLASS_NAMES[idx],
                "confidence": float(predictions[idx]),
            })

        return {
            "disease": top_disease,
            "confidence": top_confidence,
            "is_confident": is_confident,
            "alternatives": alternatives,
            "all_predictions": all_predictions,
        }


def test_classifier():
    """Quick test — requires the model file to exist."""
    print("=" * 60)
    print("TESTING CNN CLASSIFIER")
    print("=" * 60)

    try:
        classifier = CropDiseaseClassifier()
        print("[CNN] Model loaded successfully!")
        print(f"[CNN] Classes: {CLASS_NAMES}")
        print(f"[CNN] Number of classes: {len(CLASS_NAMES)}")
        print("\nTo test with a real image, run:")
        print('  result = classifier.predict("path/to/leaf_image.jpg")')
        print('  print(result)')
    except FileNotFoundError as e:
        print(f"[CNN] {e}")
        print("\nThis is expected if you haven't trained the model yet.")
        print("Run the Colab notebook first!")


if __name__ == "__main__":
    test_classifier()
