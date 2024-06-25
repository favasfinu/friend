from django.shortcuts import render
from .models import Question, Product, Order, FAQ
from difflib import get_close_matches
import spacy
from django.conf import settings

nlp = spacy.load('en_core_web_sm')

def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.9)
    return matches[0] if matches else None

def process_input(user_input):
    doc = nlp(user_input)
    tokens = [token.text for token in doc]
    return tokens, doc.ents

def chatbot_view(request):
    response = ''
    user_input = ''

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        new_answer = request.POST.get('new_answer', '').strip()

        # After processing the user input
        print(f"User input: {user_input}")
        print(f"New answer: {new_answer}")

        if user_input and not new_answer:
            tokens, entities = process_input(user_input)

            # Product-related queries
            if any('product' in token.lower() for token in tokens) or any('stock' in token.lower() for token in tokens):
                product_name = next((ent.text for ent in entities if ent.label_ in ['PRODUCT', 'ORG']), None)
                if product_name:
                    products = Product.objects.filter(name__icontains=product_name)
                    if products:
                        product_details = [
                            f"{product.name} (Price: {product.price}, Stock: {product.stock})"
                            for product in products
                        ]
                        response = f"Products found: {', '.join(product_details)}"
                    else:
                        response = "No products found."
                else:
                    response = "Please specify a product name."

            # Order-related queries
            elif any('order' in token.lower() for token in tokens):
                order_id = next((ent.text for ent in entities if ent.label_ == 'CARDINAL'), None)
                if order_id:
                    try:
                        order = Order.objects.get(id=order_id)
                        response = f"Order #{order.id} by {order.customer_name} is currently {order.status}."
                    except Order.DoesNotExist:
                        response = "Order not found."
                else:
                    response = "Please specify an order ID."

            # FAQ-related queries
            elif any('faq' in token.lower() for token in tokens):
                questions = FAQ.objects.values_list('question', flat=True)
                best_match = find_best_match(user_input, list(questions))
                if best_match:
                    answer = FAQ.objects.get(question=best_match).answer
                    response = answer
                else:
                    response = "No FAQ found matching your query."

            # General questions
            else:
                questions = Question.objects.values_list('question_text', flat=True)
                best_match = find_best_match(user_input, list(questions))
                if best_match:
                    answer = Question.objects.get(question_text=best_match).answer_text
                    response = answer
                else:
                    response = "I don't know the answer, can you teach me?"
                    if settings.CHATBOT_LEARNING_MODE:
                        return render(request, 'chatbot/chatbot.html', {'response': response, 'user_input': user_input})

        elif user_input and new_answer.lower() != 'skip':
            if new_answer:
                print(f"New question: {user_input}, New answer: {new_answer}")
                Question.objects.create(question_text=user_input, answer_text=new_answer)
                print("New question and answer saved.")
                response = "Thank you! New response added."
            else:
                response = "No new answer provided. Please provide an answer or type 'skip'."

    return render(request, 'chatbot/chatbot.html', {'response': response, 'user_input': user_input})
