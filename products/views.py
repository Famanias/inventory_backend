from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer
from django.conf import settings
import requests
import json

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return products for the authenticated user
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the authenticated user
        serializer.save(user=self.request.user)

class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return products for the authenticated user
        return Product.objects.filter(user=self.request.user)

class InsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            products = Product.objects.filter(user=request.user)

            # Handle empty inventory
            if not products.exists():
                return Response(
                    {
                        "summary": "No inventory data available.",
                        "trends": "No trends available due to lack of inventory data.",
                        "actions": "No actions recommended at this time."
                    },
                    status=status.HTTP_200_OK
                )

            total_items = products.count()
            total_value = sum(p.quantity * p.price for p in products)
            categories = list(set(p.category for p in products))
            low_stock = [p for p in products if p.quantity < 10 and p.quantity != 0]
            out_of_stock = [p for p in products if p.quantity == 0]

            # Calculate category percentages
            category_counts = {}
            for product in products:
                category_counts[product.category] = category_counts.get(product.category, 0) + 1
            category_percentages = {
                cat: (count / total_items * 100) for cat, count in category_counts.items()
            }
            sorted_categories = sorted(
                category_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            )   

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
                "- **Summary**: Provide a concise overview of the inventory in three distinct paragraphs, separated by double line breaks (use \n\n)."
                "First paragraph: State the total number of items, number of distinct categories, and the total inventory value (e.g., 'The inventory includes 1,200 items across 8 categories, with a total value of $150,000'). Ensure figures are clear and precise, using approximate values if exact data is unavailable."
                "Second paragraph: Identify the top categories by inventory share, including their percentages (e.g., 'Electronics (42%), Apparel (25%), and Home Goods (15%) dominate the inventory'). If percentages cannot be calculated due to missing data, briefly explain the limitation (e.g., 'Category percentages are unavailable due to incomplete sales data')."
                "Offer a hypothetical comparison to a previous period, prefixed with '🔄 Based on historical data' (e.g., '🔄 Based on historical data, current inventory levels are 18% higher than last year, reflecting increased stock in high-demand categories'). If no prior data exists, note the assumption or use industry trends for context.\n"
                "- **Trends**: Write three distinct paragraphs (use \\n\\n for paragraph breaks), identifying growth or decline patterns for products or categories, inferring based on quantities (e.g., low stock suggests high demand). "
                "First paragraph: Discuss demand patterns (e.g., 'Low stock levels of X suggest high demand'). "
                "Second paragraph: Comment on inventory management (e.g., 'No out-of-stock items indicate effective inventory management'). "
                "Third paragraph: Summarize how demand patterns and inventory management affect sales, customer experience, or operational efficiency (e.g., 'High demand for X, paired with strong inventory practices, likely boosts customer satisfaction by ensuring product availability'). Highlight any potential risks or opportunities, such as overstocking less popular items or scaling up stock for high-demand products."
                "Fourth paragraph: End with a note like '📈 Trend analysis based on current data, with recommendations for improvement'.\n"
                "- **Actions**: Provide recommendations in two sections with markdown formatting:\n"
                "  - Start with '**❗ Out of Stock:**' followed by a markdown list (using '-') of out-of-stock items (e.g., '- Wireless Mouse').\n"
                "  - Followed '**⚠️ Low on Stock:**' followed by a markdown list (using '-') of low stock items or items less than 10 (e.g., '- [8] Wireless Mouse').\n"
                "  - Then add '**💡 Optimization Suggestions:**' Provide strategic suggestions to improve inventory management in a markdown list (using '-'). Base recommendations on trends, demand, or efficiency (e.g., '- Reduce desk lamp inventory by 15% due to seasonal demand decline', '- Increase stock of high-demand wireless keyboards by 10%').\n"
                "  - Use \\n for line breaks between bullets and sections.\n"
                "- Each section should be as detailed as possible.\n"
                "- **Critical**: Return ONLY a valid JSON object with keys 'summary', 'trends', 'actions'. The values should be strings with markdown and emojis where specified. "
                "Do not include any text outside the JSON. Ensure the JSON is parseable.\n\n"
                "**Example Output**:\n"
                "{\"summary\": \"Your inventory consists of 93 items across 5 categories, with a total value of $12,489.75.\\n\\nElectronics is your largest category (42%), followed by Home Office (28%) and Accessories (15%).\\n\\n🔄 Based on historical data, your current inventory levels are 18% higher than the same period last year.\", "
                "\"trends\": \"Wireless Headphones and Ergonomic Keyboards have shown consistent growth over the past 3 months.\\n\\nSales of desk accessories have decreased by 12% compared to last quarter.\\n\\n📈 Trend analysis based on 6-month data.\", "
                "\"actions\": \"**❗ Out of Stock:**\\n- Wireless Mouse\\n- Ergonomic Keyboard\\n- Monitor Stand\\n**⚠️ Low on Stock:**\\n-[2] Wireless Keyboard\\n-[9] Wireless Earphones\\n**💡 Optimization Suggestions:**\\n- Consider bundling wireless peripherals for increased sales\\n- Reduce desk lamp inventory by 15% based on seasonal trends\"}\n\n"
                "Now, generate the insights based on the provided data. Add more information on what each of the item category are mostly used for in Summary and ensure the output is concise and professional."
                "Make at least 5 optimization suggestions."
                "Make sure to include the emojis and markdown formatting as specified."
                "Ensure that the Low on Stock displays the number of items in square brackets (e.g., -[2] Wireless Keyboard)."
                "- **Important Note**: Ensure the JSON output is syntactically correct (e.g., proper brackets, quotes, commas). Do not include trailing commas, unclosed brackets, or any invalid JSON syntax. Double-check that the output can be parsed by a JSON parser without errors."
                "Ensure that the JSON output will not return this error: Failed to generate insights error: Invalid JSON format in Groq response."
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
            json_match = re.search(r"```json\s*\n([\s\S]*?)\n```", content)

            if json_match:
                json_text = json_match.group(1)
            else:
                # Fallback: Try using full content directly
                json_text = content.strip()
            
            try:
                generated_insights = json.loads(json_text)

                # Check for required keys
                if not all(key in generated_insights for key in ["summary", "trends", "actions"]):
                    print(f"Missing required keys in Groq response: {generated_insights}")
                    return Response(
                        {"error": "Incomplete insights data from Groq API"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return Response(generated_insights)

            except json.JSONDecodeError as e:
                print(f"JSON parse error: {str(e)}, content: {json_text}")
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