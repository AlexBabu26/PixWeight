import base64
import json
import os
import re
import time
from typing import Any, Dict, Optional

import requests

# Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()  # "openrouter" or "groq"

# OpenRouter settings
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Groq settings
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()  # Strip whitespace
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")

# OpenRouter model settings (fallback if provider is openrouter)
OPENROUTER_VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "qwen/qwen2.5-vl-32b-instruct")
OPENROUTER_TEXT_MODEL = os.getenv("OPENROUTER_TEXT_MODEL", "openai/gpt-4o-mini")

APP_REFERER = os.getenv("OPENROUTER_APP_REFERER", "http://localhost:8000")
APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "PixWeight")

# Determine which models to use based on provider
if LLM_PROVIDER == "groq":
    VISION_MODEL = GROQ_VISION_MODEL
    TEXT_MODEL = GROQ_TEXT_MODEL
    BASE_URL = GROQ_BASE_URL
else:  # openrouter (default)
    VISION_MODEL = OPENROUTER_VISION_MODEL
    TEXT_MODEL = OPENROUTER_TEXT_MODEL
    BASE_URL = OPENROUTER_BASE_URL

class LLMError(RuntimeError):
    pass

def _get_headers() -> Dict[str, str]:
    """Get headers based on provider."""
    headers = {"Content-Type": "application/json"}
    
    if LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise LLMError("OPENROUTER_API_KEY is not set.")
        headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"
        headers["HTTP-Referer"] = APP_REFERER
        headers["X-Title"] = APP_TITLE
    elif LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is not set. Please check your .env file.")
        # Ensure API key doesn't have extra whitespace
        api_key = GROQ_API_KEY.strip()
        if not api_key.startswith("gsk_"):
            raise LLMError(f"Invalid GROQ_API_KEY format. Key should start with 'gsk_'. Got: {api_key[:10]}...")
        headers["Authorization"] = f"Bearer {api_key}"
    
    return headers

def _post_chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send chat request to LLM provider."""
    url = f"{BASE_URL}/chat/completions"
    headers = _get_headers()
    
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    if resp.status_code >= 400:
        provider_name = LLM_PROVIDER.upper()
        raise LLMError(f"{provider_name} error {resp.status_code}: {resp.text}")
    
    return resp.json()

def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from model output, handling markdown fences."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    return json.loads(text[start:end + 1])

def _call_with_json_retry(payload: Dict[str, Any], retries: int = 2, backoff_s: float = 1.2) -> Dict[str, Any]:
    """Call LLM with retry logic and JSON extraction."""
    last_err = None
    for i in range(retries + 1):
        try:
            data = _post_chat(payload)
            content = data["choices"][0]["message"]["content"]
            return _extract_json(content)
        except Exception as e:
            last_err = e
            if i < retries:
                time.sleep(backoff_s * (i + 1))
                continue
            raise

def image_file_to_data_url(image_path: str, mime_type: str = "image/jpeg") -> str:
    """Convert image file to base64 data URL."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

class ImageValidationError(RuntimeError):
    """Raised when image validation fails."""
    pass


# ============================================
# CATEGORY DETECTION & SPECIFIC QUESTIONS
# ============================================

CATEGORY_KEYWORDS = {
    "food": [
        "apple", "banana", "fruit", "vegetable", "meat", "chicken", "fish", "bread", 
        "food", "meal", "sandwich", "burger", "pizza", "salad", "rice", "pasta",
        "egg", "cheese", "milk", "yogurt", "beef", "pork", "turkey", "salmon",
        "potato", "tomato", "carrot", "orange", "grape", "strawberry", "mango",
        "pineapple", "watermelon", "avocado", "broccoli", "lettuce", "cucumber",
        "onion", "pepper", "spinach", "cake", "cookie", "chocolate"
    ],
    "package": [
        "box", "package", "parcel", "carton", "envelope", "container", "crate",
        "shipment", "mail", "delivery", "shipping box", "cardboard", "packaging"
    ],
    "pet": [
        "dog", "cat", "puppy", "kitten", "rabbit", "bird", "hamster", "guinea pig",
        "pet", "animal", "canine", "feline", "retriever", "shepherd", "bulldog",
        "poodle", "beagle", "husky", "chihuahua", "persian", "siamese", "parrot"
    ],
    "person": [
        "person", "man", "woman", "human", "body", "people", "adult", "child",
        "male", "female", "guy", "girl", "boy", "individual"
    ]
}

CATEGORY_SPECIFIC_QUESTIONS = {
    "food": [
        {
            "question": "Is this food raw or cooked?",
            "answer_type": "select",
            "options": ["Raw", "Cooked", "Processed"],
            "required": True
        },
        {
            "question": "Is any portion missing or already eaten?",
            "answer_type": "select",
            "options": ["No, it's whole", "Partially eaten", "Just a portion"],
            "required": True
        },
        {
            "question": "Does it have skin, peel, or shell on?",
            "answer_type": "boolean",
            "required": False
        }
    ],
    "package": [
        {
            "question": "Estimated length in cm?",
            "answer_type": "number",
            "unit": "cm",
            "required": True
        },
        {
            "question": "Estimated width in cm?",
            "answer_type": "number",
            "unit": "cm",
            "required": True
        },
        {
            "question": "Estimated height in cm?",
            "answer_type": "number",
            "unit": "cm",
            "required": True
        },
        {
            "question": "Is the package fragile?",
            "answer_type": "boolean",
            "required": False
        },
        {
            "question": "Shipping destination?",
            "answer_type": "select",
            "options": ["Domestic", "International"],
            "required": False
        }
    ],
    "pet": [
        {
            "question": "What breed is this pet? (if known)",
            "answer_type": "text",
            "required": False
        },
        {
            "question": "What is the pet's age category?",
            "answer_type": "select",
            "options": ["Puppy/Kitten (< 1 year)", "Adult (1-7 years)", "Senior (7+ years)"],
            "required": True
        },
        {
            "question": "Is the pet male or female?",
            "answer_type": "select",
            "options": ["Male", "Female", "Unknown"],
            "required": False
        },
        {
            "question": "Is the pet spayed or neutered?",
            "answer_type": "select",
            "options": ["Yes", "No", "Unknown"],
            "required": False
        }
    ],
    "person": [
        {
            "question": "What is the person's height in cm?",
            "answer_type": "number",
            "unit": "cm",
            "required": True
        },
        {
            "question": "What is the person's age? (optional)",
            "answer_type": "number",
            "unit": "years",
            "required": False
        },
        {
            "question": "Gender?",
            "answer_type": "select",
            "options": ["Male", "Female", "Prefer not to say"],
            "required": False
        },
        {
            "question": "Activity level?",
            "answer_type": "select",
            "options": ["Sedentary", "Lightly active", "Moderately active", "Very active"],
            "required": False
        }
    ]
}


def detect_category(object_label: str) -> str:
    """
    Detect category from object label using keyword matching.
    
    Args:
        object_label: The identified object label from vision model
        
    Returns:
        Category string: "food", "package", "pet", "person", or "general"
    """
    if not object_label:
        return "general"
    
    label_lower = object_label.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in label_lower for keyword in keywords):
            return category
    
    return "general"


def get_category_specific_questions(category: str, base_questions: list) -> list:
    """
    Append category-specific questions to base questions from vision model.
    
    Args:
        category: Detected category
        base_questions: Questions generated by vision model
        
    Returns:
        Combined list of base + category-specific questions
    """
    # Get category-specific questions
    category_questions = CATEGORY_SPECIFIC_QUESTIONS.get(category, [])
    
    # Combine base questions with category-specific ones
    # Limit total to 12 questions max
    all_questions = base_questions + category_questions
    return all_questions[:12]

def validate_image_content(image_data_url: str) -> Dict[str, Any]:
    """
    Validate image content against quality rules using vision model.
    
    Rules checked:
    - For person: Full Body Clear View, Minimal Clothing, Standard standing pose, Plain Background
    - For single objects: Reference Object Inclusion (optional but recommended), Visibility and Clarity, 
      Uniform Lighting, Plain Contrasting Background, Sharp Focus
    - For composite objects (food items, multiple items): Visibility and Clarity, Sharp Focus
      (Reference objects and plain backgrounds are optional for composite items)
    
    Returns validation result dict with 'valid' (bool) and 'issues' (list of strings).
    Raises ImageValidationError if validation fails.
    """
    system = (
        "You validate images for weight estimation. Check if the image meets quality requirements. "
        "Be lenient with composite objects (like food items with multiple ingredients, salads, meals). "
        "For composite objects, focus on visibility and clarity rather than requiring reference objects or plain backgrounds. "
        "Return ONLY valid JSON (no markdown)."
    )

    user_prompt = {
        "task": "validate_image_quality",
        "validation_rules": {
            "person": [
                "Full Body Clear View - person should be fully visible from head to toe",
                "Minimal Clothing - person should wear minimal clothing",
                "Standard standing pose - person should be in a standard standing position",
                "Plain Background - background should be simple and uniform"
            ],
            "single_object": [
                "Reference Object Inclusion - image should include a reference object (coin, ruler, etc.) - OPTIONAL but recommended",
                "Visibility and Clarity - object should be clearly visible and distinct",
                "Uniform Lighting - lighting should be even across the image - OPTIONAL",
                "Plain Contrasting Background - background should be plain and contrast with object - OPTIONAL",
                "Sharp Focus - image should be in sharp focus"
            ],
            "composite_object": [
                "Visibility and Clarity - main object(s) should be clearly visible",
                "Sharp Focus - image should be in sharp focus",
                "Multiple items are acceptable - composite objects like salads, meals, or collections are valid",
                "Reference objects are OPTIONAL - not required for composite objects",
                "Plain background is OPTIONAL - natural backgrounds are acceptable"
            ]
        },
        "instructions": [
            "First, determine if the image contains a single object, composite object (multiple items together like a salad), or a person",
            "For composite objects (food items with multiple ingredients, salads, meals, collections), use 'composite_object' rules",
            "For single distinct objects, use 'single_object' rules",
            "Be lenient - only reject images that are truly unusable (blurry, too dark, completely obscured)",
            "Accept images with multiple objects if they form a cohesive whole (like a salad with ingredients)"
        ],
        "output_schema": {
            "image_type": "person|single_object|composite_object|unknown",
            "valid": "boolean",
            "issues": ["array of strings describing validation failures - only include critical issues"],
            "summary": "short string summarizing validation result"
        }
    }

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": json.dumps(user_prompt)},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
        "temperature": 0.2,
    }

    try:
        out = _call_with_json_retry(payload, retries=2)
        valid = bool(out.get("valid", False))
        issues = out.get("issues", [])
        image_type = out.get("image_type", "unknown")
        
        # For composite objects, be more lenient - only reject if truly unusable
        if image_type == "composite_object":
            # Only reject if there are critical issues (blurry, too dark, completely obscured)
            critical_issues = [issue for issue in issues if any(keyword in issue.lower() for keyword in 
                ["blurry", "too dark", "obscured", "cannot see", "unusable", "completely hidden"])]
            if not critical_issues and issues:
                # Non-critical issues for composite objects - allow through
                valid = True
        
        if not valid and issues:
            issues_str = "; ".join(issues)
            raise ImageValidationError(
                f"Image validation failed: {out.get('summary', 'Image does not meet quality requirements')}. "
                f"Issues: {issues_str}"
            )
        
        return out
    except ImageValidationError:
        raise
    except Exception as e:
        # If validation itself fails, we'll allow the image through but log the error
        # You might want to change this behavior based on your requirements
        raise LLMError(f"Image validation error: {str(e)}")

def identify_object_and_questions(image_data_url: str, user_hint: str = "") -> Dict[str, Any]:
    """Identify object in image and generate questions using vision model."""
    system = (
        "You identify the main object in an image and generate the minimum set of questions "
        "needed to estimate its weight. Return ONLY valid JSON (no markdown)."
    )

    user_prompt = {
        "objectives": [
            "Identify the main object in the image (simple label).",
            "Provide a short summary of what you see that matters for weight.",
            "Ask 4-8 practical questions that a user can answer."
        ],
        "output_schema": {
            "object_label": "string",
            "object_summary": "string",
            "questions": [
                {
                    "question": "string",
                    "answer_type": "text|number|boolean|select",
                    "unit": "optional string",
                    "options": "optional list of strings (select only)",
                    "required": "boolean"
                }
            ]
        },
        "user_hint": user_hint
    }

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": json.dumps(user_prompt)},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
        "temperature": 0.2,
    }

    out = _call_with_json_retry(payload, retries=2)
    out.setdefault("questions", [])
    if not isinstance(out["questions"], list):
        out["questions"] = []
    
    # Detect category from object label
    object_label = out.get("object_label", "")
    category = detect_category(object_label)
    out["category"] = category
    
    # Add category-specific questions
    base_questions = out["questions"][:8]  # Limit base questions
    out["questions"] = get_category_specific_questions(category, base_questions)
    
    return out

def _to_grams(value: float, unit: str) -> float:
    """Convert weight to grams."""
    u = (unit or "").strip().lower()
    if u in ["g", "gram", "grams"]:
        return value
    if u in ["kg", "kilogram", "kilograms"]:
        return value * 1000.0
    if u in ["lb", "lbs", "pound", "pounds"]:
        return value * 453.59237
    if u in ["oz", "ounce", "ounces"]:
        return value * 28.349523125
    return value

def estimate_weight(object_label: str, object_summary: str, qa: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate weight using text model."""
    system = (
        "You estimate object weight from user answers. Return ONLY valid JSON (no markdown). "
        "If uncertain, give a realistic range and lower confidence."
    )

    schema = {
        "estimated_weight": {"value": "number", "unit": "g|kg|lb|oz", "min": "number", "max": "number"},
        "confidence": "number between 0 and 1",
        "rationale": "short string",
        "key_factors": ["string"]
    }

    user_payload = {
        "task": "estimate_weight",
        "object_label": object_label,
        "object_summary": object_summary,
        "qa": qa,
        "output_schema": schema,
        "constraints": [
            "min <= value <= max",
            "do not invent facts not supported by user answers",
            "if dimensions are missing, widen range and reduce confidence"
        ],
    }

    payload = {
        "model": TEXT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0.2,
    }

    out = _call_with_json_retry(payload, retries=2)
    ew = out.get("estimated_weight", {}) or {}

    unit = str(ew.get("unit", "g") or "g")
    value = float(ew.get("value", 0) or 0)
    minv = float(ew.get("min", value) or value)
    maxv = float(ew.get("max", value) or value)

    out["_normalized_grams"] = {
        "value_g": _to_grams(value, unit),
        "min_g": _to_grams(minv, unit),
        "max_g": _to_grams(maxv, unit),
    }
    return out

# Keep OpenRouterError for backward compatibility
OpenRouterError = LLMError
