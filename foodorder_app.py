import streamlit as st
from streamlit_chat import message
import re

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'order' not in st.session_state:
    st.session_state.order = {}
if 'stage' not in st.session_state:
    st.session_state.stage = 'welcome'

# Indian Restaurant Menu
MENU = {
    "Paneer Butter Masala": 250,
    "Chicken Biryani": 300,
    "Dal Tadka": 180,
    "Butter Naan": 40,
    "Gulab Jamun": 60,
    "Masala Chai": 30
}

def display_menu():
    menu_text = "Here's our menu:\n\n"
    for item, price in MENU.items():
        menu_text += f"🍛 {item}: ₹{price}\n"
    menu_text += "\nExample order: '2 Chicken Biryani and 3 Butter Naan'"
    return menu_text

def calculate_total():
    return sum(MENU[item] * qty for item, qty in st.session_state.order.items())

def show_current_order():
    order_text = "📝 Your Current Order:\n\n"
    for item, qty in st.session_state.order.items():
        order_text += f"• {item} x{qty}\n"
    order_text += "\nYou can:\n- Add more items (e.g., 'Add 1 Masala Chai')\n- Type 'remove' to delete items\n- Type 'total' to see bill\n- Type 'confirm' to finalize"
    return order_text

def handle_user_input(user_input):
    current_stage = st.session_state.stage
    user_input = user_input.strip().lower()
    
    # Welcome stage
    if current_stage == 'welcome':
        st.session_state.messages.append(("bot", "Namaste! 🙏 I'm Chaiwala, your food ordering assistant.\n\nYou can:\n- Type 'menu' to see our offerings\n- Start ordering directly (e.g., '2 Chicken Biryani')"))
        st.session_state.stage = 'main'
    
    # Main interaction stage
    elif current_stage == 'main':
        if 'menu' in user_input:
            st.session_state.messages.append(("bot", display_menu()))
            st.session_state.messages.append(("bot", "💡 Example orders:\n- '1 Paneer Butter Masala with 2 Butter Naan'\n- '3 Masala Chai and 2 Gulab Jamun'"))
        elif any(word in user_input for word in ['order', 'add', 'x', 'quantity']):
            process_order(user_input)
        elif 'total' in user_input:
            show_total()
        elif 'confirm' in user_input:
            confirm_order()
        elif 'no' in user_input and st.session_state.order:
            st.session_state.messages.append(("bot", show_current_order()))
        else:
            st.session_state.messages.append(("bot", "Please let me know how I can help! 😊\n\nTry:\n- 'Show menu'\n- 'Add 2 Chicken Biryani'\n- 'What's my total?'\n- 'Confirm order'"))

def process_order(user_input):
    # Clean and parse input
    user_input = re.sub(r'\b(and|with)\b', ',', user_input, flags=re.IGNORECASE)
    pairs = re.findall(r'(\d+)\s*([a-zA-Z\s]+)', user_input)
    
    if not pairs:
        st.session_state.messages.append(("bot", "❌ Please specify items with quantities!\n\nExample formats:\n- '2 Chicken Biryani'\n- '1 Paneer Butter Masala, 2 Butter Naan'\n- 'Add 3 Masala Chai'"))
        return
    
    for qty, item in pairs:
        item = item.strip().title()
        qty = int(qty)
        
        if item not in MENU:
            st.session_state.messages.append(("bot", f"❌ Sorry, '{item}' is not in our menu. Please check:\n{display_menu()}"))
            continue
            
        if item in st.session_state.order:
            st.session_state.order[item] += qty
        else:
            st.session_state.order[item] = qty
    
    st.session_state.messages.append(("bot", f"✅ Added {qty} {item} to your order!"))
    st.session_state.messages.append(("bot", show_current_order()))

def show_total():
    total = calculate_total()
    st.session_state.messages.append(("bot", f"💰 Total Bill: ₹{total}\n\nType 'confirm' to place your order or add more items!"))

def confirm_order():
    total = calculate_total()
    confirmation_msg = f"""🎉 Order Confirmed! 🎉
    
Your total: ₹{total}
Estimated preparation time: 25-35 minutes

Thank you for choosing Chaiwala! 🙏
You'll receive an SMS confirmation shortly.

Start new order: Type 'menu' or 'hi'"""
    
    # Complete session reset
    st.session_state.messages = [("bot", confirmation_msg)]
    st.session_state.order = {}
    st.session_state.stage = 'welcome'

def main():
    st.title("🍛 Chaiwala - Food Ordering Assistant")
    
    # Chat container
    chat_container = st.container()
    
    # User input
    with st.form(key='input_form'):
        user_input = st.text_input("Type your message here:", key='input', placeholder="E.g., '2 Chicken Biryani and 1 Gulab Jamun'")
        submit_button = st.form_submit_button("📤 Send")
    
    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))
        handle_user_input(user_input)
    
    # Display messages
    with chat_container:
        for i, (sender, msg) in enumerate(st.session_state.messages):
            if sender == 'user':
                message(msg, is_user=True, key=f"{i}_user")
            else:
                message(msg, key=f"{i}_bot", allow_html=True)

if __name__ == "__main__":
    main()