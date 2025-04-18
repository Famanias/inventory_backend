from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import json


# Create your views here.
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

class InsightsView(APIView):
    def post(self, request):
        try:
            products = Product.objects.all()

            total_items= products.count()
            total_value = sum(p.quantity * p.price for p in products)
            categories = list(set(p.category for p in products))
            low_stock = [p for p in products if p.quantity <= 10]
            out_of_stock = [p for p in products if p.quantity == 0]

            inventory_summary = (
                f"Total items: {total_items}\n"
                f"Total value: ${total_value:.2f}\n"
                f"Categories: {', '.join(categories)}\n"
                f"Low stock items (<=10): {', '.join([f'{p.name} ({p.quantity})' for p in low_stock]) or 'None'}\n"
                f"Out of stock items: {', '.join([p.name for p in out_of_stock]) or 'None'}"
            )

            prompt = (
                "You are an AI inventory analyst. Based on the provided inventory data, generate insights in three sections: Summary, Trends, and Actions. "
                "Provide concise, professional responses suitable for a dashboard.\n\n"
                "**Inventory Data**:\n"
                f"{inventory_summary}\n\n"
                "**Instructions**:\n"
                "- **Summary**: Describe the overall inventory, including total items, number of categories, total value, and the largest category by item count. "
                "Include a hypothetical comparison to the previous period (e.g., last year or quarter, assume reasonable growth or decline).\n"
                "- **Trends**: Identify growth or decline patterns for products or categories, inferring based on quantities (e.g., low stock suggests high demand).\n"
                "- **Actions**: Suggest restocking for specific low or out-of-stock items and optimization strategies (e.g., reduce overstock, bundle items).\n"
                "- Each section should be a single paragraph or bullet list, max 100 words.\n"
                "- Use markdown for formatting (e.g., **Summary**, - Bullet).\n"
                "- **Important**: Return the response as a JSON object with keys 'summary', 'trends', and 'actions'. "
                "Wrap the JSON in triple backticks (```json\n...\n```) to ensure it is valid and parseable.\n\n"
                "**Example Output**:\n"
                "```json\n"
                "{\n"
                "  \"summary\": \"Your inventory has 10 items across 3 categories...\",\n"
                "  \"trends\": \"Electronics show high demand...\",\n"
                "  \"actions\": \"- Restock Item X (0 remaining)\\n- Bundle Item Y...\"\n"
                "}\n"
                "```\n\n"
                "Now, generate the insights based on the provided data."
            )

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
            )

            if not response.ok:
                error_body = response.text
                print(f"Groq API Error: {response.status_code} {error_body}")
                return Response(
                    {"error": f"Failed to generate insights: {error_body}"},
                    status=response.status_code
                )
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Raw Groq response: {content}")

            import re
            json_match = re.search(r"```json\n([\s\S]*?)\n```", content)
            if not json_match:
                print(f"Failed to find JSON block in Groq response: {content}")
                return Response(
                    {"error": "Invalid JSON format in Groq response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            try:
                generated_insights = json.loads(json_match.group(1))
                # Validate expected keys
                if not all(key in generated_insights for key in ["summary", "trends", "actions"]):
                    print(f"Missing required keys in Groq response: {generated_insights}")
                    return Response(
                        {"error": "Incomplete insights data from Groq API"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                return Response(generated_insights)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {str(e)}, content: {json_match.group(1)}")
                return Response(
                    {"error": "Invalid JSON format in Groq response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            print(f"Server error: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
