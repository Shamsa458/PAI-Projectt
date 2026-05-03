import os
import gradio as gr
from cnn_classifier import CropDiseaseClassifier
from expert_engine import CropDiseaseExpert

# Initialize our AI modules
expert_loaded = False
classifier_loaded = False
expert = None
classifier = None

try:
    expert = CropDiseaseExpert()
    expert_loaded = True
except Exception as e:
    print(f"[ERROR] Expert engine failed to load: {e}")

try:
    classifier = CropDiseaseClassifier()
    classifier_loaded = True
except Exception as e:
    print(f"[ERROR] CNN classifier failed to load: {e}")


def diagnose(image_path, crop_type, growth_stage, weather):
    """Gradio prediction function mapping inputs to the pipeline."""
    if not image_path:
        return "⚠️ **Please upload a leaf image first.**"
    
    if not classifier_loaded:
        return "❌ **CNN Model Error:** The model is not loaded. Ensure `crop_disease_model.h5` is in the `models/` directory."
    
    if not expert_loaded:
        return "❌ **Expert Engine Error:** Failed to load the rule-based expert system."
    
    try:
        # Step 1: Predict Disease
        cnn_result = classifier.predict(image_path)
        disease = cnn_result["disease"]
        confidence = cnn_result["confidence"]
        is_confident = cnn_result["is_confident"]
        
        # Step 2: Expert Reasoning
        prolog_result = expert.get_diagnosis(disease, growth_stage, weather)
        
        # Step 3: Format Output neatly as Markdown
        md = f"### 🔍 Diagnosis Results\n\n"
        
        disease_display = disease.replace("_", " ").title()
        md += f"# {disease_display}\n"
        
        # Confidence
        conf_pct = f"{confidence * 100:.1f}%"
        if is_confident:
            md += f"**Confidence:** ✅ {conf_pct}\n\n"
        else:
            md += f"**Confidence:** ⚠️ {conf_pct} (Low Confidence)\n\n"
            md += "*Possible Alternatives:*\n"
            for alt in cnn_result["alternatives"]:
                alt_name = alt["disease"].replace("_", " ").title()
                alt_conf = f"{alt['confidence'] * 100:.1f}%"
                md += f"- {alt_name} ({alt_conf})\n"
            md += "\n"
        
        if prolog_result["description"]:
            md += f"**Description:** {prolog_result['description']}\n\n"
            
        # Urgency
        urgency_level = prolog_result["urgency_level"]
        urgency_label = prolog_result["urgency_label"]
        if urgency_level >= 3:
            md += f"### 🔴 Urgency: {urgency_label}\n\n"
        elif urgency_level >= 2:
            md += f"### 🟡 Urgency: {urgency_label}\n\n"
        else:
            md += f"### 🟢 Urgency: {urgency_label}\n\n"
            
        md += f"**Context:** Crop: {crop_type.title()} | Stage: {growth_stage.title()} | Weather: {weather.title()}\n\n"
        
        # Treatments
        md += "### 💊 Recommended Treatments\n"
        treatments = prolog_result["treatments"]
        if treatments:
            for i, t in enumerate(treatments, 1):
                name = t["name"].replace("_", " ").title()
                md += f"{i}. **{name}**\n"
                md += f"   - *Method:* {t['method']}\n"
                md += f"   - *Frequency:* {t['frequency']}\n"
        else:
            md += "No treatments specific to this context.\n"
            
        md += "\n"
        
        # Preventions
        md += "### 🛡️ Preventive Actions\n"
        preventions = prolog_result["preventions"]
        if preventions:
            for i, p in enumerate(preventions, 1):
                md += f"{i}. **{p['action']}**\n"
                md += f"   - *Reason:* {p['reason']}\n"
        else:
            md += "No specific preventive actions for current conditions.\n"
            
        return md
            
    except Exception as e:
        return f"❌ **Error during diagnosis:**\n{str(e)}"

# Layout
with gr.Blocks(title="Smart Crop Disease Detector", theme=gr.themes.Base()) as demo:
    gr.Markdown("# 🌿 Smart Crop Disease Detector\nUpload a leaf photo, select the farm conditions, and get a treatment plan powered by a CNN + Expert System.")
    
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="filepath", label="Upload Leaf Photo")
            
            crop_input = gr.Dropdown(
                choices=["tomato", "potato", "corn", "wheat"],
                value="tomato",
                label="Crop Type"
            )
            
            stage_input = gr.Dropdown(
                choices=["seedling", "vegetative", "flowering", "harvest"],
                value="vegetative",
                label="Growth Stage"
            )
            
            weather_input = gr.Dropdown(
                choices=["dry", "normal", "wet"],
                value="normal",
                label="Recent Weather"
            )
            
            submit_btn = gr.Button("🔍 Diagnose Disease", variant="primary")
            
        with gr.Column(scale=1):
            output_md = gr.Markdown(label="Results", value="*Results will appear here.*")
            
    submit_btn.click(
        fn=diagnose,
        inputs=[image_input, crop_input, stage_input, weather_input],
        outputs=output_md
    )

if __name__ == "__main__":
    demo.launch()
