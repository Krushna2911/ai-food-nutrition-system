@'
# AI-Based Food Detection System with Nutrition Estimation and Personalized Diet Planning

A research-oriented full-stack system that combines computer vision, nutrition data, deterministic nutrition calculations, and LLM-based dietary guidance.

## Overview

The system follows this workflow:

Food Image
â†’ Food Detection
â†’ Food Segmentation
â†’ Nutrition Mapping
â†’ Portion/Nutrition Calculation
â†’ Personalized Diet Planning
â†’ AI-Generated Dietary Guidance

The project is designed so that authoritative nutrition values and hard dietary constraints remain deterministic, while the LLM is used for explanation and guidance rather than inventing nutrition values.

## System Architecture

```text
React Frontend
      |
      v
FastAPI Backend
      |
      +--------------------+
      |                    |
      v                    v
Food Analysis        User Profile
      |                    |
      v                    v
YOLO26 Detection    Nutrition Requirements
      |
      +----> Segmentation
      |
      +----> Nutrition Mapping
      |
      v
Deterministic Diet Planner
      |
      v
Validated Diet Plan
      |
      v
LangGraph Recommendation Workflow
      |
      v
Groq LLM
      |
      v
AI Nutrition Guidance

# AI Food Nutrition System

A research project that combines computer vision, USDA-based nutrition data, deterministic diet planning, and an LLM explanation layer. Authoritative numerical computation is deliberately kept separate from generative language output.

## Technology Stack

### Frontend
- React
- Vite
- React Markdown
- remark-gfm
- Responsive CSS
### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite/PostgreSQL-compatible database layer
- Uvicorn
### Machine Learning
- YOLO26
- Ultralytics
- PyTorch
- scikit-learn
- OpenCV
- Random Forest
### Nutrition and Recommendation
- USDA FoodData Central
- LangChain
- LangGraph
- Groq
- openai/gpt-oss-120b
## Machine Learning Pipeline

### 1. Food Detection

The food detection model was trained using the UEC Food100 dataset.

- Trained YOLO model: `ml/models/best.pt`
- Training configuration: `ml/configs/food_detection.yaml`
Detection training used:
- 11,521 training images
- 1,459 validation images
- Image size: 640
- Batch size: 16
- Training epochs: 50
Final validation results:

| Metric | Result |
|---|---|
| Precision | 0.621 |
| Recall | 0.678 |
| mAP@50 | 0.700 |
| mAP@50-95 | 0.543 |

### 2. Food Segmentation

Food segmentation was evaluated using FoodSeg103. The evaluation used an untouched test set containing:
- 2,135 images
- 12,011 food instances
Results:

| Metric | Result |
|---|---|
| Box mAP@50 | 0.219763 |
| Box mAP@50-95 | 0.178586 |
| Mask mAP@50 | 0.219959 |
| Mask mAP@50-95 | 0.170521 |

These results are retained as the current segmentation baseline.

### 3. Mass Estimation

A Random Forest model was trained using Nutrition5k RGB-D data.

Configuration:
- 300 trees
- Random seed: 42
Evaluation results:

| Metric | Result |
|---|---|
| MAE | 63.214 g |
| RMSE | 87.244 g |

> **Important limitation:** The current mass model estimates *total dish mass* from RGB-D input. It should not be interpreted as universal per-food portion estimation for arbitrary RGB-only web images, or as a method that assigns the total dish mass to every detected food item.

## Nutrition Data Pipeline

USDA FoodData Central is used as the authoritative nutrition source. Nutrition values are stored on a per-100-g basis.

The current UEC-to-USDA mapping contains:
- 100 UEC food classes
- 25 mapped nutrition records
- 75 unresolved composite-food mappings
Current mapping status:
- 24 strong candidates
- 1 verified mapping
- 75 requiring composite-source resolution
Composite foods are intentionally not treated as verified exact mappings without a defensible nutrition source. The current processed mapping files are maintained under the project data pipeline.

## Deterministic Nutrition Calculation

Nutrition calculations are performed deterministically from the stored USDA-derived values. For a food with nutrition values defined per 100 g:

```
multiplier = portion_g / 100
```

The system then calculates:
- calories
- protein
- carbohydrates
- fat
The LLM does not calculate or invent these values.

## Personalized Nutrition Requirements

The backend calculates daily calorie requirements using:
- Age
- Height
- Weight
- Activity level
- Diet goal
The current BMR calculation is:

```
BMR = (10 Ã— weight_kg)
    + (6.25 Ã— height_cm)
    - (5 Ã— age)
    + 5
```

Activity multipliers are applied to estimate maintenance calories. Diet goals then adjust the daily target.

## Diet Planning

The diet planner is deterministic and operates on the validated nutrition database.

Current meal calorie targets:
- Breakfast: 25%
- Lunch: 40%
- Dinner: 35%
The planner evaluates food combinations and portions while considering:
- Daily calorie target
- Protein
- Carbohydrates
- Fat
- AMDR compliance
- Dietary preference
- Food restrictions
AMDR ranges used by the planner:
- Protein: 10â€“35%
- Carbohydrates: 45â€“65%
- Fat: 20â€“35%
The planner calculates these values deterministically.

## LLM Recommendation Layer

The LLM is placed after the deterministic diet-planning stage.

```
Validated User Profile
        |
        v
Nutrition Requirement Service
        |
        v
Deterministic Diet Planner
        |
        v
Validated Diet Plan
        |
        v
LangGraph
        |
        v
Groq LLM
        |
        v
Dietary Guidance
```

The recommendation layer is explicitly constrained so that the LLM:
- Does not invent nutrition values
- Does not recalculate calories
- Does not modify validated portions
- Does not introduce unvalidated foods
- Does not replace deterministic dietary constraints
Its role is to explain the validated plan and provide practical adherence guidance.

## Backend API

Main API areas:

```
POST /food/upload
POST /food/detect
POST /food/segment
POST /food/mass-estimate

GET  /nutrition/{food_name}
POST /nutrition/calculate

POST /profile
GET  /profile/{profile_id}

POST /nutrition-requirement

POST /diet-plan

POST /recommendation

GET  /analysis
GET  /analysis/{image_id}
```

The backend entry point is `backend/app/main.py`.

## Project Structure

```
ai-food-nutrition-system/
â”‚
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ repositories/
â”‚   â”‚   â”œâ”€â”€ routers/
â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â””â”€â”€ main.py
â”‚   â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ tests/
â”‚   â””â”€â”€ requirements.txt
â”‚
â”œâ”€â”€ frontend/
â”‚   â””â”€â”€ src/
â”‚       â””â”€â”€ App.jsx
â”‚
â”œâ”€â”€ ml/
â”‚   â”œâ”€â”€ configs/
â”‚   â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ notebooks/
â”‚   â””â”€â”€ src/
â”‚
â”œâ”€â”€ rag/
â”œâ”€â”€ recommendation/
â”œâ”€â”€ data/
â”œâ”€â”€ docs/
â”œâ”€â”€ experiments/
â”œâ”€â”€ tests/
â””â”€â”€ test_images/
```

## Local Setup

### Backend

Create and activate the Python environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Set the backend Python path:

```powershell
$env:PYTHONPATH=".\backend"
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The frontend communicates with the FastAPI backend running on port 8000.

## Environment Variables

API credentials are kept outside source control using `.env`. Do not commit API keys or other secrets. The project `.gitignore` excludes environment files.

## Testing

Backend regression tests:

```powershell
$env:PYTHONPATH=".\backend"
.\.venv\Scripts\python.exe -m pytest backend/tests -q
```

Current result: **20 passed**

The frontend production build is also validated using:

```bash
cd frontend
npm run build
```

## Research Limitations

The current system has several deliberate limitations.

- **Food mapping coverage:** Only 25 of the 100 UEC classes currently have mapped nutrition records. The remaining 75 classes require additional composite-food or ingredient-level source resolution.
- **Segmentation performance:** The current FoodSeg103 evaluation provides a baseline rather than production-level segmentation performance.
- **Mass estimation:** The Nutrition5k mass model is an RGB-D total-dish-mass estimator. It is not currently a validated per-detection portion estimator for arbitrary RGB images.
- **Food recognition:** Performance depends on the trained UEC Food100 model and can produce incorrect classifications for visually ambiguous or out-of-distribution images.
- **LLM recommendations:** The LLM is used only after deterministic nutrition and diet-plan generation. The system intentionally does not allow the LLM to act as the authoritative nutrition calculator.
## Validation Status

The following workflows have been functionally validated:
- Balanced diet profile
- Beef food restriction
- Vegetarian preference
- Vegan preference
- Deterministic calorie targeting
- AMDR compliance
- LLM recommendation generation
- Food image upload
- Food detection API
- Food segmentation API
- Nutrition calculation
- Diet-plan generation
- Recommendation generation
Backend regression suite: **20 passed**

## Research Positioning

The project combines:
1. Computer vision for food recognition
2. Food segmentation
3. RGB-D mass estimation
4. USDA-based nutrition retrieval
5. Deterministic nutrition calculation
6. Constraint-based personalized diet planning
7. LangGraph orchestration
8. LLM-generated dietary explanation
The architecture intentionally separates authoritative numerical computation from generative language generation. This separation is important for maintaining reproducibility, traceability, and control over nutrition-related outputs.

## License

This repository is currently presented as a research project.
