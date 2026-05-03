"""
expert_engine.py — Pure Python expert system replacing Prolog
"""

class CropDiseaseExpert:
    """
    Python-based knowledge base and rule engine for crop disease treatment reasoning.
    """

    def __init__(self):
        # Disease Information: (CropType, Description, SpreadRate)
        self.disease_info = {
            "tomato_early_blight": ("tomato", "Fungal disease causing dark concentric rings on older leaves", "moderate"),
            "tomato_late_blight": ("tomato", "Aggressive fungal disease causing water-soaked lesions that rapidly kill foliage", "fast"),
            "tomato_leaf_mold": ("tomato", "Fungal infection causing yellow patches on upper leaf surface and olive-green mold beneath", "moderate"),
            "potato_early_blight": ("potato", "Fungal disease causing brown spots with target-like rings on potato leaves", "moderate"),
            "potato_late_blight": ("potato", "Devastating fungal disease causing dark water-soaked patches that destroy tubers", "fast"),
            "corn_common_rust": ("corn", "Fungal disease producing small reddish-brown pustules on both leaf surfaces", "moderate"),
            "corn_northern_leaf_blight": ("corn", "Fungal disease causing long elliptical gray-green lesions on corn leaves", "slow"),
            "wheat_leaf_rust": ("wheat", "Fungal disease causing small orange-brown pustules scattered on wheat leaves", "fast"),
            "wheat_septoria": ("wheat", "Fungal disease causing tan lesions with dark borders on wheat leaves", "moderate"),
            "healthy": ("any", "No disease detected", "none")
        }

        # Treatments: {Disease: [(TreatmentName, Method, Frequency)]}
        self.treatments = {
            "tomato_early_blight": [
                ("chlorothalonil_spray", "Apply chlorothalonil fungicide spray to all affected and surrounding plants", "Every 7-10 days"),
                ("copper_fungicide", "Apply copper-based fungicide as a protective barrier on leaves", "Every 7 days"),
                ("remove_infected_leaves", "Carefully remove and destroy all leaves showing dark ring symptoms", "Immediately upon detection"),
                ("mulching", "Apply thick organic mulch around base to prevent soil splash onto lower leaves", "Once after detection")
            ],
            "tomato_late_blight": [
                ("metalaxyl_spray", "Apply metalaxyl-based systemic fungicide immediately to stop rapid spread", "Every 5-7 days"),
                ("destroy_infected_plants", "Remove and burn severely infected plants to prevent spore spread to neighbours", "Immediately"),
                ("copper_fungicide", "Apply copper hydroxide spray as protective treatment on remaining healthy plants", "Every 5 days")
            ],
            "tomato_leaf_mold": [
                ("improve_ventilation", "Increase spacing between plants and prune lower branches to improve air flow", "Once after detection"),
                ("reduce_humidity", "Avoid overhead watering and water at base of plants early in the morning", "Ongoing practice"),
                ("fungicide_spray", "Apply mancozeb or chlorothalonil fungicide to affected plants", "Every 7-10 days")
            ],
            "potato_early_blight": [
                ("mancozeb_spray", "Apply mancozeb fungicide to all potato plants in the affected area", "Every 7-10 days"),
                ("remove_infected_foliage", "Remove and destroy lower leaves showing brown target-spot symptoms", "Immediately upon detection"),
                ("crop_rotation", "Plan to rotate potatoes with non-solanaceous crops next season", "Next planting season")
            ],
            "potato_late_blight": [
                ("metalaxyl_spray", "Apply metalaxyl or cymoxanil systemic fungicide to stop rapid infection", "Every 5-7 days"),
                ("destroy_infected_plants", "Remove and burn all severely infected plants and nearby volunteer potatoes", "Immediately"),
                ("harvest_early", "If tubers are near maturity, harvest immediately before blight reaches them", "Within 48 hours if applicable")
            ],
            "corn_common_rust": [
                ("triazole_fungicide", "Apply triazole-based fungicide such as propiconazole to infected corn", "Every 10-14 days"),
                ("remove_infected_leaves", "Remove heavily rusted lower leaves to reduce spore load", "Immediately upon detection"),
                ("resistant_varieties", "Plan to use rust-resistant corn varieties for next planting cycle", "Next planting season")
            ],
            "corn_northern_leaf_blight": [
                ("strobilurin_fungicide", "Apply strobilurin-based fungicide at first sign of gray-green lesions", "Every 14 days"),
                ("remove_crop_debris", "Remove and destroy all corn residue after harvest to eliminate overwintering fungus", "After harvest"),
                ("crop_rotation", "Rotate corn with non-grass crops for at least one season", "Next planting season")
            ],
            "wheat_leaf_rust": [
                ("propiconazole_spray", "Apply propiconazole fungicide immediately to slow rust spread across the field", "Every 10-14 days"),
                ("tebuconazole_spray", "Apply tebuconazole as an alternative systemic fungicide for rust control", "Every 10-14 days"),
                ("resistant_varieties", "Switch to rust-resistant wheat cultivars for the next sowing", "Next planting season")
            ],
            "wheat_septoria": [
                ("azoxystrobin_spray", "Apply azoxystrobin fungicide to control septoria leaf blotch spread", "Every 14 days"),
                ("remove_crop_debris", "Remove and burn infected wheat stubble after harvest", "After harvest"),
                ("seed_treatment", "Use treated seeds with fungicide coating for next planting season", "Next planting season")
            ]
        }

        # Safe Growth Stages: {TreatmentName: [Stages]}
        self.stage_safe = {
            "chlorothalonil_spray": ["seedling", "vegetative", "flowering"],
            "copper_fungicide": ["seedling", "vegetative", "flowering", "harvest"],
            "metalaxyl_spray": ["vegetative", "flowering"],
            "mancozeb_spray": ["seedling", "vegetative", "flowering"],
            "triazole_fungicide": ["vegetative", "flowering"],
            "strobilurin_fungicide": ["vegetative", "flowering"],
            "propiconazole_spray": ["vegetative", "flowering"],
            "tebuconazole_spray": ["vegetative", "flowering"],
            "azoxystrobin_spray": ["vegetative", "flowering"],
            "fungicide_spray": ["vegetative", "flowering"],
            "remove_infected_leaves": ["seedling", "vegetative", "flowering", "harvest"],
            "remove_infected_foliage": ["seedling", "vegetative", "flowering", "harvest"],
            "destroy_infected_plants": ["seedling", "vegetative", "flowering", "harvest"],
            "mulching": ["seedling", "vegetative", "flowering", "harvest"],
            "improve_ventilation": ["seedling", "vegetative", "flowering", "harvest"],
            "reduce_humidity": ["seedling", "vegetative", "flowering", "harvest"],
            "harvest_early": ["harvest"],
            "crop_rotation": ["seedling", "vegetative", "flowering", "harvest"],
            "resistant_varieties": ["seedling", "vegetative", "flowering", "harvest"],
            "remove_crop_debris": ["harvest"],
            "seed_treatment": ["seedling", "vegetative", "flowering", "harvest"]
        }

        # Preventions: {Disease: {(Weather): (Action, Reason)}}
        self.preventions = {
            "tomato_early_blight": {
                "wet": ("Apply preventive copper spray to all tomato plants in the area", "Wet conditions accelerate early blight fungal spore spread"),
                "normal": ("Monitor lower leaves closely for early ring-shaped lesions", "Moderate moisture can still support early blight development")
            },
            "tomato_late_blight": {
                "wet": ("Apply preventive metalaxyl spray to all tomato and potato crops nearby", "Late blight spreads explosively in wet and cool conditions"),
                "normal": ("Inspect all tomato plants for water-soaked patches every 2-3 days", "Late blight can emerge even in moderate humidity")
            },
            "tomato_leaf_mold": {
                "wet": ("Improve greenhouse ventilation and reduce watering immediately", "High humidity is the primary driver of leaf mold outbreaks"),
                "normal": ("Maintain good air circulation between plants", "Moderate humidity can support leaf mold in dense plantings")
            },
            "potato_early_blight": {
                "wet": ("Apply preventive mancozeb spray to all potato crops in the field", "Wet conditions promote rapid spread of early blight in potatoes"),
                "dry": ("Continue regular monitoring but risk is lower in dry conditions", "Dry weather slows early blight but does not eliminate it")
            },
            "potato_late_blight": {
                "wet": ("Begin emergency preventive spraying on ALL potato and tomato crops nearby", "Potato late blight caused the Irish Famine — wet conditions make it devastating"),
                "normal": ("Increase inspection frequency to daily for all potato fields", "Late blight can appear suddenly even in moderate conditions")
            },
            "corn_common_rust": {
                "wet": ("Apply preventive fungicide to corn fields near the infected area", "Rust spores spread rapidly through wind and rain splash"),
                "dry": ("Monitor but risk is reduced in dry conditions", "Dry weather suppresses rust spore germination")
            },
            "corn_northern_leaf_blight": {
                "wet": ("Apply preventive strobilurin spray to nearby corn plantings", "Cool wet weather drives northern leaf blight epidemics")
            },
            "wheat_leaf_rust": {
                "wet": ("Apply preventive propiconazole spray to entire wheat field", "Wet conditions cause explosive wheat rust spread across fields"),
                "normal": ("Scout field borders first as rust often enters from edges", "Rust spores can travel long distances on wind")
            },
            "wheat_septoria": {
                "wet": ("Apply preventive azoxystrobin to wheat fields in the area", "Septoria thrives in prolonged wet and cool conditions"),
                "normal": ("Monitor lower leaves where septoria typically appears first", "Moderate conditions can support septoria development")
            }
        }

    def get_diagnosis(self, disease_label, growth_stage, weather):
        if disease_label == "healthy":
            return {
                "disease": "healthy",
                "description": "No disease detected — your crop looks healthy!",
                "urgency_level": 0,
                "urgency_label": "NO ACTION NEEDED",
                "treatments": [],
                "preventions": [
                    {
                        "action": "Continue regular monitoring and good agricultural practices",
                        "reason": "Prevention is always better than cure"
                    }
                ],
            }

        result = {
            "disease": disease_label,
            "description": "",
            "urgency_level": 0,
            "urgency_label": "UNKNOWN",
            "treatments": [],
            "preventions": [],
        }

        info = self.disease_info.get(disease_label)
        if info:
            crop_type, description, spread_rate = info
            result["description"] = description
            
            # Urgency
            if spread_rate == "fast":
                result["urgency_level"] = 3
                result["urgency_label"] = "URGENT INTERVENTION"
            elif spread_rate == "moderate":
                result["urgency_level"] = 2
                result["urgency_label"] = "TREAT NOW"
            elif spread_rate == "slow":
                result["urgency_level"] = 1
                result["urgency_label"] = "MONITOR"

        # Treatments
        disease_treatments = self.treatments.get(disease_label, [])
        for t_name, method, freq in disease_treatments:
            safe_stages = self.stage_safe.get(t_name, [])
            if growth_stage in safe_stages:
                result["treatments"].append({
                    "name": t_name,
                    "method": method,
                    "frequency": freq
                })

        # Preventions
        disease_preventions = self.preventions.get(disease_label, {})
        if weather in disease_preventions:
            action, reason = disease_preventions[weather]
            result["preventions"].append({
                "action": action,
                "reason": reason
            })

        return result

def test_expert_engine():
    """Quick test to verify everything works."""
    print("=" * 60)
    print("TESTING EXPERT ENGINE")
    print("=" * 60)

    expert = CropDiseaseExpert()

    # Test 1: Tomato Early Blight, vegetative stage, wet weather
    print("\\n--- Test 1: Tomato Early Blight | Vegetative | Wet ---")
    result = expert.get_diagnosis("tomato_early_blight", "vegetative", "wet")
    print(f"Disease: {result['disease']}")
    print(f"Description: {result['description']}")
    print(f"Urgency: {result['urgency_label']} (Level {result['urgency_level']})")
    print(f"Treatments ({len(result['treatments'])}):")
    for i, t in enumerate(result["treatments"], 1):
        print(f"  {i}. {t['name']}: {t['method']} — {t['frequency']}")
    print(f"Preventions ({len(result['preventions'])}):")
    for i, p in enumerate(result["preventions"], 1):
        print(f"  {i}. {p['action']}")
        print(f"     Reason: {p['reason']}")

if __name__ == "__main__":
    test_expert_engine()
