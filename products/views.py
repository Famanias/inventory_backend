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
                "- **Summary**: Describe the overall inventory in three distinct paragraphs (use \\n\\n for paragraph breaks). "
                "First paragraph: Include total items, number of categories, and total value. "
                "Second paragraph: List the top categories with their percentages (e.g., 'Electronics (42%)'). If percentages aren't calculable, explain why. "
                "Third paragraph: Provide a hypothetical comparison to the previous period, prefixed with '🔄 Based on historical data' (e.g., '🔄 Based on historical data, your current inventory levels are 18% higher than the same period last year').\n"
                "- **Trends**: Write three distinct paragraphs (use \\n\\n for paragraph breaks), identifying growth or decline patterns for products or categories, inferring based on quantities (e.g., low stock suggests high demand). "
                "First paragraph: Discuss demand patterns (e.g., 'Low stock levels of X suggest high demand'). "
                "Second paragraph: Comment on inventory management (e.g., 'No out-of-stock items indicate effective inventory management'). "
                "Third paragraph: End with a note like '📈 Trend analysis based on current data, with recommendations for improvement'.\n"
                "- **Actions**: Provide recommendations in two sections with markdown formatting:\n"
                "  - Start with '**⚠ Restock Recommendations:**' followed by a markdown list (using '-') of specific low or out-of-stock items (e.g., '- Wireless Mouse (8 remaining)').\n"
                "  - Then add '**💡 Optimization Suggestions:**' followed by a markdown list (using '-') of strategies (e.g., '- Reduce desk lamp inventory by 15% based on seasonal trends').\n"
                "  - Use \\n for line breaks between bullets and sections.\n"
                "- Each section should be as detailed as possible.\n"
                "- **Critical**: Return ONLY a valid JSON object with keys 'summary', 'trends', 'actions'. The values should be strings with markdown and emojis where specified. "
                "Do not include any text outside the JSON. Ensure the JSON is parseable.\n\n"
                "**Example Output**:\n"
                "{\"summary\": \"Your inventory consists of 93 items across 5 categories, with a total value of $12,489.75.\\n\\nElectronics is your largest category (42%), followed by Home Office (28%) and Accessories (15%).\\n\\n🔄 Based on historical data, your current inventory levels are 18% higher than the same period last year.\", "
                "\"trends\": \"Wireless Headphones and Ergonomic Keyboards have shown consistent growth over the past 3 months.\\n\\nSales of desk accessories have decreased by 12% compared to last quarter.\\n\\n📈 Trend analysis based on 6-month data.\", "
                "\"actions\": \"**⚠ Restock Recommendations:**\\n- Wireless Mouse (8 remaining)\\n- Ergonomic Keyboard (12 remaining)\\n- Monitor Stand (Out of Stock)\\n**💡 Optimization Suggestions:**\\n- Consider bundling wireless peripherals for increased sales\\n- Reduce desk lamp inventory by 15% based on seasonal trends\"}\n\n"
                "Now, generate the insights based on the provided data. Add more information on what each of the inventory items are mostly used for in Summary and ensure the output is concise and professional."
            )

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": prompt}]
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
