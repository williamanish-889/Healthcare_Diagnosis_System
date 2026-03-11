"""Medical image analysis service using Hugging Face pre-trained models."""
import io
import torch
from PIL import Image
from transformers import AutoFeatureExtractor, AutoModelForImageClassification


class MedicalImageService:
    """Uses microsoft/resnet-50 fine-tuned on ImageNet as a base,
    with medical-specific prompt engineering via OpenAI for interpretation."""

    def __init__(self):
        self._model = None
        self._extractor = None
        self._loaded = False
        self.model_name = "microsoft/swin-base-patch4-window7-224-in22k"

    def load(self):
        if self._loaded:
            return
        try:
            self._extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
            self._model = AutoModelForImageClassification.from_pretrained(self.model_name)
            self._model.eval()
            self._loaded = True
            print(f"Image model loaded: {self.model_name}")
        except Exception as e:
            print(f"Failed to load image model: {e}. Will use OpenAI vision fallback.")
            self._loaded = False

    async def analyze_image(
        self, image_bytes: bytes, image_type: str = "xray"
    ) -> dict:
        """Analyze medical image and return findings."""
        from app.services.openai_service import openai_service
        from app.config import get_settings
        import base64

        settings = get_settings()

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        image_type_labels = {
            "xray": "chest X-ray",
            "mri": "MRI scan",
            "ct": "CT scan",
            "other": "medical image",
        }
        img_label = image_type_labels.get(image_type, "medical image")

        prompt = f"""You are a senior radiologist AI assistant. Analyze this {img_label} and provide:

1. **Image Type Confirmation**: Confirm the type of medical image
2. **Findings**: Detailed findings from the image
3. **Abnormalities**: List any abnormalities detected
4. **Confidence Level**: Your confidence in the findings (0-100%)
5. **Recommendation**: Next steps or additional imaging needed

Respond ONLY with valid JSON:
{{
  "image_type": "{img_label}",
  "findings": "detailed findings...",
  "confidence": 85.0,
  "abnormalities_detected": ["abnormality1", "abnormality2"],
  "recommendation": "recommendation text..."
}}"""

        try:
            if settings.openai_api_key:
                response = await openai_service.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a medical imaging AI specialist. Respond only with valid JSON.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{b64_image}",
                                        "detail": "high",
                                    },
                                },
                            ],
                        },
                    ],
                    temperature=0.2,
                    max_tokens=1500,
                )
                import json
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                return json.loads(content)
            else:
                return self._basic_analysis(image_bytes, image_type)
        except Exception as e:
            print(f"Image analysis error: {e}")
            return self._basic_analysis(image_bytes, image_type)

    def _basic_analysis(self, image_bytes: bytes, image_type: str) -> dict:
        """Fallback analysis using the Hugging Face model features."""
        try:
            self.load()
            if self._model and self._extractor:
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                inputs = self._extractor(images=image, return_tensors="pt")
                with torch.no_grad():
                    outputs = self._model(**inputs)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    top_prob, top_idx = torch.topk(probs, 5)

                findings = []
                for prob, idx in zip(top_prob[0], top_idx[0]):
                    label = self._model.config.id2label.get(idx.item(), f"class_{idx.item()}")
                    findings.append(f"{label} ({prob.item()*100:.1f}%)")

                return {
                    "image_type": image_type,
                    "findings": f"Image classification results: {', '.join(findings[:3])}. Note: Using general vision model - results should be reviewed by a radiologist.",
                    "confidence": round(top_prob[0][0].item() * 100, 2),
                    "abnormalities_detected": ["Requires specialist review"],
                    "recommendation": "Please have a qualified radiologist review this image for accurate medical interpretation.",
                }
        except Exception as e:
            print(f"Basic analysis error: {e}")

        return {
            "image_type": image_type,
            "findings": "Unable to perform automated analysis. Image received successfully.",
            "confidence": 0.0,
            "abnormalities_detected": [],
            "recommendation": "Please configure OpenAI API key for AI-powered image analysis, or have a radiologist review manually.",
        }


image_service = MedicalImageService()
